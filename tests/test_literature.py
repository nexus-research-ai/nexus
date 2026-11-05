import json

from fastapi.testclient import TestClient
from nexus_api.main import app
from nexus_api.routes import literature


def test_literature_search_uses_imported_public_papers(tmp_path, monkeypatch):
    paper = {
        'title': 'Artificial Intelligence for Accessible Research',
        'authors': ['Research Author'],
        'abstract': 'Artificial intelligence helps researchers inspect published evidence.',
        'pdf_url': 'https://arxiv.org/pdf/2401.01234',
        'source': 'arxiv',
    }
    (tmp_path / 'imported.json').write_text(json.dumps(paper))
    monkeypatch.setattr(literature, 'PAPERS_DIR', tmp_path)
    response = TestClient(app).get('/api/v1/literature/search', params={'q': 'artificial intelligence'})
    assert response.status_code == 200
    data = response.json()
    assert data['items'][0]['title'] == paper['title']
    assert data['items'][0]['origin'] == paper['pdf_url']
    assert data['items'][0]['evidence_kind'] == 'public'
    assert data['corpus'] == 'imported_public_papers'


def test_literature_search_does_not_substitute_synthetic_results(tmp_path, monkeypatch):
    monkeypatch.setattr(literature, 'PAPERS_DIR', tmp_path)
    data = TestClient(app).get('/api/v1/literature/search', params={'q': 'artificial intelligence'}).json()
    assert data['items'] == []
    assert data['degraded'] is True
