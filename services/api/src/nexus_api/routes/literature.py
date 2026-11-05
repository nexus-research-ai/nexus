import json
import os
from functools import lru_cache
from pathlib import Path
from urllib.parse import urlparse

from fastapi import APIRouter, Query
from nexus_discovery.literature import _tokens, _bm25_scores, build_literature_graph

router = APIRouter()
PAPERS_DIR = Path(os.environ.get('NEXUS_PAPERS_DIR', Path(__file__).resolve().parents[5] / 'data' / 'papers'))


@lru_cache(maxsize=4)
def imported_papers(directory: Path):
    papers = []
    for path in sorted(directory.glob('*.json')):
        try:
            record = json.loads(path.read_text())
            title = str(record.get('title') or '').strip()
            abstract = str(record.get('abstract') or '').strip()
            origin = str(record.get('pdf_url') or record.get('url') or '')
            parsed = urlparse(origin)
            if not title or not abstract or parsed.scheme not in ('https', 'http') or not parsed.netloc:
                continue
            authors = record.get('authors') or []
            if isinstance(authors, str):
                authors = [authors]
            papers.append({
                'id': f'imported:{path.stem}', 'title': title,
                'authors': [str(author) for author in authors],
                'department': str(record.get('department') or 'Imported research'),
                'text': abstract, 'origin': origin, 'kind': 'paper', 'evidence_kind': 'public',
            })
        except (OSError, ValueError, TypeError, AttributeError):
            continue
    return papers, [_tokens(f"{p['title']} {p['title']} {p['text']}") for p in papers]


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50)):
    papers, corpus_tokens = imported_papers(PAPERS_DIR)
    terms = _tokens(q)
    scores = _bm25_scores(corpus_tokens, terms)
    ranked = sorted(((paper, score) for paper, score in zip(papers, scores) if score > 0), key=lambda item: -(item[1] + (10 if q.strip().casefold() in f"{item[0]['title']} {item[0]['text']}".casefold() else 0)))
    items = []
    for paper, score in ranked[:limit]:
        matched = sorted(set(terms) & set(_tokens(f"{paper['title']} {paper['text']}")))
        lower = paper['text'].casefold()
        positions = [lower.find(term) for term in matched if term in lower]
        start = max(0, min(positions) - 65) if positions else 0
        items.append({**paper, 'snippet': paper['text'][start:start + 280], 'score': round(score, 6), 'reason': f"Imported paper · keyword match in title or abstract: {', '.join(matched)}."})
    return {'query': q.strip(), 'items': items, 'degraded': not bool(papers), 'corpus': 'imported_public_papers', 'corpus_size': len(papers)}


@router.get("/graph")
def graph():
    return build_literature_graph()
