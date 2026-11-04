"""In-memory literature search and knowledge-graph engine.

Pure Python BM25 + a deterministic subword semantic vectorizer, combined with
Reciprocal Rank Fusion (RRF) for hybrid ranking. No external ML runtime or
database required — the corpus below is a small, synthetic sample set, not a
live crawl.
"""

from __future__ import annotations

import math
import re
import zlib
from collections import Counter
from dataclasses import dataclass, field

_TOKEN = re.compile(r"[^\W_]+", re.UNICODE)
_STOP_WORDS = frozenset(
    "a an and are as at be by for from in is it of on or that the this to was were with".split()
)


def _tokens(text: str) -> list[str]:
    return [t for token in _TOKEN.findall(text) if (t := token.casefold()) not in _STOP_WORDS]


def _char_ngrams(word: str, n_min: int = 3, n_max: int = 5) -> list[str]:
    word = f"<{word}>"
    length = len(word)
    grams = []
    for n in range(n_min, min(n_max + 1, length + 1)):
        for i in range(length - n + 1):
            grams.append(word[i : i + n])
    return grams


class SemanticVectorizer:
    """Deterministic subword TF-IDF vectorizer into a fixed-size dense vector."""

    def __init__(self, dim: int = 128):
        self.dim = dim

    def encode(self, text: str) -> list[float]:
        vector = [0.0] * self.dim
        if not text or not text.strip():
            return vector
        toks = _tokens(text)
        if not toks:
            return vector
        features: list[str] = []
        for token in toks:
            features.append(f"w:{token}")
            features.extend(_char_ngrams(token))
        counts = Counter(features)
        for feature, count in counts.items():
            h = zlib.crc32(feature.encode("utf-8"))
            idx = h % self.dim
            sign = 1.0 if (h // self.dim) % 2 == 0 else -1.0
            vector[idx] += sign * (1.0 + math.log(count))
        norm = math.sqrt(sum(v * v for v in vector))
        if norm > 1e-6:
            vector = [v / norm for v in vector]
        return vector

    @staticmethod
    def similarity(a: list[float], b: list[float]) -> float:
        dot = sum(x * y for x, y in zip(a, b))
        return max(0.0, min(1.0, dot))


def _bm25_scores(corpus_tokens: list[list[str]], query_terms: list[str], k1: float = 1.5, b: float = 0.75) -> list[float]:
    n_docs = len(corpus_tokens)
    if n_docs == 0:
        return []
    doc_lens = [len(doc) for doc in corpus_tokens]
    avgdl = sum(doc_lens) / n_docs or 1.0
    df: Counter = Counter()
    for doc in corpus_tokens:
        for term in set(doc):
            df[term] += 1
    idf = {term: max(math.log(1 + (n_docs - freq + 0.5) / (freq + 0.5)), 0.01) for term, freq in df.items()}

    scores = []
    for doc, dl in zip(corpus_tokens, doc_lens):
        tf = Counter(doc)
        score = 0.0
        for term in query_terms:
            if term not in tf:
                continue
            freq = tf[term]
            denom = freq + k1 * (1 - b + b * dl / avgdl)
            score += idf.get(term, 0.01) * (freq * (k1 + 1)) / denom
        scores.append(score)
    return scores


def reciprocal_rank_fusion(ranked_a: list[str], ranked_b: list[str], rrf_k: int = 60) -> dict[str, float]:
    scores: dict[str, float] = {}
    for rank, doc_id in enumerate(ranked_a, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)
    for rank, doc_id in enumerate(ranked_b, start=1):
        scores[doc_id] = scores.get(doc_id, 0.0) + 1.0 / (rrf_k + rank)
    return scores


@dataclass
class Paper:
    id: str
    title: str
    authors: list[str]
    department: str
    topics: list[str]
    text: str
    origin: str
    kind: str = "paper"


# Synthetic sample corpus (fixture data, not a live crawl / private snapshot).
LITERATURE_CORPUS: list[Paper] = [
    Paper(
        id="lit-001",
        title="Federated Foundation Models for Privacy-Preserving Neural Decoding",
        authors=["Dr. Elena Vasquez", "Dr. Marcus Thorne"],
        department="Bioengineering",
        topics=["neural decoding", "federated learning", "privacy"],
        text="We present a federated learning framework for training foundation models on distributed neural recordings without centralizing raw signal data. Each clinical site retrains a shared encoder locally and exchanges only gradient summaries, preserving patient privacy while achieving decoding accuracy within 3% of a centralized baseline across five held-out cohorts.",
        origin="sample-corpus:lit-001",
    ),
    Paper(
        id="lit-002",
        title="Soft Aerial Sensors for Forest Canopy Health Monitoring",
        authors=["Maya Rodriguez"],
        department="Robotics",
        topics=["soft robotics", "sensing", "ecology"],
        text="Biodegradable soft aerial sensors are deployed across forest canopy sites to continuously measure stress indicators such as leaf moisture and volatile organic compound emission. The platform combines compliant actuation with low-power wireless telemetry and is validated against ground-truth plant pathology assessments.",
        origin="sample-corpus:lit-002",
    ),
    Paper(
        id="lit-003",
        title="Differential Privacy Bounds for Multi-Site Clinical Data Sharing",
        authors=["Dr. Marcus Thorne", "Aria Malik"],
        department="EECS",
        topics=["privacy", "differential privacy", "clinical data"],
        text="We derive tight differential privacy bounds for gradient aggregation across multiple clinical sites under heterogeneous data distributions, and show the bound is critical for maintaining utility in Aim 2 of federated neural decoding pipelines while meeting institutional compliance requirements.",
        origin="sample-corpus:lit-003",
    ),
    Paper(
        id="lit-004",
        title="Hybrid BM25 and Dense Retrieval for Scientific Literature Discovery",
        authors=["Aria Malik"],
        department="EECS",
        topics=["information retrieval", "search", "nlp"],
        text="This work evaluates a hybrid retrieval pipeline combining classical BM25 keyword ranking with a lightweight dense subword encoder, fused via Reciprocal Rank Fusion. The hybrid approach improves recall on long-tail queries over academic corpora compared to either method alone, without requiring a large pretrained language model.",
        origin="sample-corpus:lit-004",
    ),
    Paper(
        id="lit-005",
        title="SLAM-Guided Precision Agriculture for Edge Vision Systems",
        authors=["Dr. Elena Vasquez"],
        department="Robotics",
        topics=["slam", "agriculture", "computer vision"],
        text="We propose a robust edge vision pipeline for precision agriculture that fuses simultaneous localization and mapping (SLAM) with lightweight object detection to identify crop stress under variable field lighting, enabling low-cost deployment on embedded hardware.",
        origin="sample-corpus:lit-005",
    ),
    Paper(
        id="lit-006",
        title="Cross-Site Validation of Wearable EEG for Motor Intent Decoding",
        authors=["Dr. Marcus Thorne"],
        department="Bioengineering",
        topics=["eeg", "neural decoding", "wearables"],
        text="Wearable dry-electrode EEG systems are benchmarked against clinical-grade arrays for motor intent decoding across three independent sites. Results show preserved classification accuracy when combined with federated model updates, supporting deployment in rehabilitation settings.",
        origin="sample-corpus:lit-006",
    ),
    Paper(
        id="lit-007",
        title="Interdisciplinary Gaps Between Computing and Bioengineering Research",
        authors=["Aria Malik", "Dr. Elena Vasquez"],
        department="EECS",
        topics=["research gaps", "interdisciplinary", "collaboration"],
        text="We map citation and co-authorship patterns between Computing & Information Sciences and Bioengineering departments to surface under-explored interdisciplinary opportunities, finding a persistent gap in applied federated learning for biosignal processing.",
        origin="sample-corpus:lit-007",
    ),
    Paper(
        id="lit-008",
        title="Low-Power Wireless Telemetry for Distributed Environmental Sensing",
        authors=["Maya Rodriguez", "Aria Malik"],
        department="EECS",
        topics=["sensing", "wireless", "sustainability"],
        text="A low-power wireless telemetry stack is presented for distributed environmental sensor networks, enabling multi-month deployments on harvested solar energy while maintaining sub-second latency for anomaly alerts in forest and agricultural monitoring applications.",
        origin="sample-corpus:lit-008",
    ),
]


def search_literature(query: str, limit: int = 10) -> dict:
    """Hybrid BM25 + semantic search over the sample literature corpus."""
    if not isinstance(query, str):
        raise ValueError("Search query must be a string.")
    query = query.strip()
    if not query:
        return {"query": query, "items": [], "degraded": True}

    terms = _tokens(query)
    corpus_tokens = [_tokens(p.title + " " + p.title + " " + p.text) for p in LITERATURE_CORPUS]
    bm25_scores = _bm25_scores(corpus_tokens, terms)

    bm25_ranked = sorted(
        ((p.id, s) for p, s in zip(LITERATURE_CORPUS, bm25_scores) if s > 0),
        key=lambda x: -x[1],
    )
    bm25_ranked_ids = [doc_id for doc_id, _ in bm25_ranked]

    vectorizer = SemanticVectorizer(dim=128)
    query_vec = vectorizer.encode(query)
    semantic_scores: dict[str, float] = {}
    for paper in LITERATURE_CORPUS:
        doc_vec = vectorizer.encode(f"{paper.title}. {paper.text}")
        sim = vectorizer.similarity(query_vec, doc_vec)
        if sim >= 0.12:
            semantic_scores[paper.id] = sim
    semantic_ranked_ids = [doc_id for doc_id, _ in sorted(semantic_scores.items(), key=lambda x: -x[1])]

    rrf_scores = reciprocal_rank_fusion(bm25_ranked_ids, semantic_ranked_ids, rrf_k=60)
    if not rrf_scores:
        return {"query": query, "items": [], "degraded": False}

    items = []
    by_id = {p.id: p for p in LITERATURE_CORPUS}
    for doc_id, score in sorted(rrf_scores.items(), key=lambda x: -x[1])[:limit]:
        paper = by_id[doc_id]
        matched = set(_tokens(paper.title + " " + paper.text)) & set(terms)
        sim = semantic_scores.get(doc_id, 0.0)
        if matched and sim >= 0.12:
            reason = f"BM25 & Semantic hybrid match (RRF score: {score:.4f}, semantic similarity: {sim:.2f}). Matched terms: {', '.join(sorted(matched))}."
        elif matched:
            reason = f"BM25 keyword match: {', '.join(sorted(matched))}. RRF score: {score:.4f}."
        else:
            reason = f"Semantic conceptual match (similarity: {sim:.2f}, RRF score: {score:.4f})."
        positions = [m.start() for m in _TOKEN.finditer(paper.text) if m.group().casefold() in matched]
        start = max(0, min(positions) - 65) if positions else 0
        items.append(
            {
                "id": paper.id,
                "title": paper.title,
                "authors": paper.authors,
                "department": paper.department,
                "snippet": paper.text[start : start + 280],
                "text": paper.text,
                "origin": paper.origin,
                "score": round(score, 6),
                "reason": reason,
                "kind": paper.kind,
            }
        )
    return {"query": query, "items": items, "degraded": False}


def build_literature_graph() -> dict:
    """Build a nodes/edges graph of papers, topics, and authoring researchers."""
    nodes = []
    edges = []
    seen_topics: dict[str, str] = {}
    seen_authors: dict[str, str] = {}

    for paper in LITERATURE_CORPUS:
        nodes.append(
            {
                "id": paper.id,
                "label": paper.title,
                "type": "paper",
                "department": paper.department,
            }
        )
        for author in paper.authors:
            author_id = seen_authors.setdefault(author, f"author-{len(seen_authors) + 1}")
            if author_id not in {n["id"] for n in nodes}:
                nodes.append({"id": author_id, "label": author, "type": "researcher", "department": paper.department})
            edges.append({"source": author_id, "target": paper.id, "relation": "authors"})
        for topic in paper.topics:
            topic_id = seen_topics.setdefault(topic, f"topic-{len(seen_topics) + 1}")
            if topic_id not in {n["id"] for n in nodes}:
                nodes.append({"id": topic_id, "label": topic, "type": "topic"})
            edges.append({"source": paper.id, "target": topic_id, "relation": "about"})

    clusters = {
        "papers": sum(1 for n in nodes if n["type"] == "paper"),
        "researchers": sum(1 for n in nodes if n["type"] == "researcher"),
        "topics": sum(1 for n in nodes if n["type"] == "topic"),
    }
    return {"nodes": nodes, "edges": edges, "clusters": clusters}
