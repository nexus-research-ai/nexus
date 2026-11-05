from pathlib import Path
import subprocess, json, math, textwrap

base = Path(__file__).resolve().parent.parent
segments = json.loads((base / 'segments.json').read_text())

def run(command):
    return subprocess.run(command, check=True, capture_output=True, text=True).stdout

def duration(path):
    return float(run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration', '-of', 'default=nw=1:nk=1', str(path)]).strip())

for segment in segments:
    raw = base / 'audio' / f"{segment['id']}.aiff"
    textfile = base / 'audio' / f"{segment['id']}.txt"
    if not raw.exists() or raw.stat().st_size < 5000 or raw.stat().st_mtime < textfile.stat().st_mtime:
        run(['say', '-v', segment['voice'], '-r', str(segment['rate']), '-f', str(textfile), '-o', str(raw)])
    segment['raw_duration'] = duration(raw)
    ratio = max(1.0, segment['raw_duration'] / (segment['duration'] - 0.18))
    segment['tempo'] = round(ratio, 6)
    print(segment['id'], segment['title'], 'raw', round(segment['raw_duration'], 2), 'target', segment['duration'], 'tempo', segment['tempo'], flush=True)

(base / 'segments.json').write_text(json.dumps(segments, indent=2, ensure_ascii=False) + '\n')
overbudget = [segment for segment in segments if segment['tempo'] > 1.12]
if overbudget:
    raise SystemExit('Rewrite overbudget segments before synthesis: ' + ','.join(segment['id'] for segment in overbudget))

for segment in segments:
    raw = base / 'audio' / f"{segment['id']}.aiff"
    output = base / segment['audio']
    af = f"atempo={segment['tempo']},loudnorm=I=-18:TP=-2:LRA=7,aresample=48000,apad=whole_len={segment['duration'] * 48000},atrim=end_sample={segment['duration'] * 48000},asetpts=N/SR/TB"
    run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-i', str(raw), '-af', af, '-ar', '48000', '-ac', '1', '-c:a', 'pcm_s16le', str(output)])
    assert abs(duration(output) - segment['duration']) < .002

concatfile = base / 'audio' / 'concat.txt'
concatfile.write_text(''.join(f"file '{segment['id']}.wav'\n" for segment in segments))
run(['ffmpeg', '-nostdin', '-hide_banner', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(concatfile), '-c:a', 'pcm_s16le', str(base / 'narration.wav')])
assert abs(duration(base / 'narration.wav') - 180) < .002

def timestamp(seconds):
    millis = round(seconds * 1000)
    hours, millis = divmod(millis, 3600000)
    minutes, millis = divmod(millis, 60000)
    whole, millis = divmod(millis, 1000)
    return f'{hours:02}:{minutes:02}:{whole:02},{millis:03}'

captions = []
for segment in segments:
    words = segment['narration'].split()
    groups = [words[i:i+9] for i in range(0, len(words), 9)]
    spoken = min(segment['duration'] - .1, segment['raw_duration'] / segment['tempo'])
    offset = 0
    for group in groups:
        start = segment['start'] + .1 + (spoken - .2) * offset / len(words)
        offset += len(group)
        end = segment['start'] + .1 + (spoken - .2) * offset / len(words)
        caption = '\n'.join(textwrap.wrap(' '.join(group), width=44))
        captions.append(f"{len(captions)+1}\n{timestamp(start)} --> {timestamp(end)}\n{caption}\n")
(base / 'narration.srt').write_text('\n'.join(captions))
print('COMPLETE narration.wav 180.000 seconds;', len(captions), 'captions', flush=True)
