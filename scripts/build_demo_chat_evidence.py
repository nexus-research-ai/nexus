"""Export exact abstract excerpts and source references for the example chats."""

import hashlib
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SOURCES = [
    ('eegDefense', 'zhibo_reputation-based_federated_learning_defense_to_mitigate_thre.json',
     'introduces a reputation-based mechanism to mitigate the influence of data poisoning attacks and identify compromised participants.'),
    ('fragmentedPrivacy', 'najeeb_enhanced_security_and_privacy_via_fragmented_federated_learn.json',
     'good updates sent by honest participants may reveal their private local information'),
    ('multiObjective', 'haibo_federated_multi-objective_learning.json',
     'Both algorithms allow local updates to significantly reduce communication costs'),
    ('communication', 'haibo_cfedavg_achieving_efficient_communication_and_fast_convergen.json',
     'a large number of workers jointly learn a model without sharing their training data.'),
]


def build_evidence():
    evidence = []
    for key, filename, quote in SOURCES:
        paper = json.loads((ROOT / 'data' / 'papers' / filename).read_text())
        abstract = paper['abstract']
        assert quote in abstract, f'Excerpt absent from {filename}'
        assert len(quote) <= 160 and len(quote.split()) <= 25, f'Excerpt too long in {filename}'
        assert paper['pdf_url'].startswith('https://arxiv.org/pdf/')
        evidence.append({
            'key': key,
            'source_id': f'imported:{Path(filename).stem}',
            'version': '1',
            'content_hash': hashlib.sha256(abstract.encode()).hexdigest(),
            'title': paper['title'],
            'origin': paper['pdf_url'],
            'quote': quote,
            'abstract': abstract,
        })
    assert len({entry['source_id'] for entry in evidence}) == len(SOURCES)
    return evidence


if __name__ == '__main__':
    entries = build_evidence()
    content = "import type { ChatCitation } from './api';\n\n"
    content += "export type DemoEvidenceKey = 'eegDefense' | 'fragmentedPrivacy' | 'multiObjective' | 'communication';\n"
    content += "export type DemoEvidence = ChatCitation & { key: DemoEvidenceKey; abstract: string };\n\n"
    content += 'export const demoEvidence: DemoEvidence[] = ' + json.dumps(entries, indent=2, ensure_ascii=False) + ';\n\n'
    content += 'export const demoEvidenceByKey = Object.fromEntries(demoEvidence.map(item => [item.key, item])) as Record<DemoEvidenceKey, DemoEvidence>;\n'
    (ROOT / 'frontend' / 'src' / 'lib' / 'demoEvidence.ts').write_text(content)
    print(f'Exported {len(entries)} validated source excerpts.')
