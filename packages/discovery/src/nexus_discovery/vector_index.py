import math
from typing import List, Dict, Any, Optional, Callable
from pydantic import BaseModel, Field

class VectorRecord(BaseModel):
    id: str
    vector: List[float]
    metadata: Dict[str, Any] = Field(default_factory=dict)

def cosine_similarity(v1: List[float], v2: List[float]) -> float:
    """Compute cosine similarity between two dense vectors."""
    if len(v1) != len(v2):
        raise ValueError(f"Vector dimensions must match ({len(v1)} != {len(v2)})")
    
    dot_product = sum(a * b for a, b in zip(v1, v2))
    norm_v1 = math.sqrt(sum(a * a for a in v1))
    norm_v2 = math.sqrt(sum(b * b for b in v2))
    
    if norm_v1 == 0.0 or norm_v2 == 0.0:
        return 0.0
    return dot_product / (norm_v1 * norm_v2)

class InMemoryVectorIndex:
    """In-memory dense vector index for campus graph embeddings and semantic search."""

    def __init__(self, dimension: int = 128):
        self.dimension = dimension
        self.records: Dict[str, VectorRecord] = {}

    def add_vector(self, record_id: str, vector: List[float], metadata: Optional[Dict[str, Any]] = None) -> None:
        if len(vector) != self.dimension:
            raise ValueError(f"Vector dimension {len(vector)} does not match index dimension {self.dimension}")
        self.records[record_id] = VectorRecord(id=record_id, vector=vector, metadata=metadata or {})

    def search(
        self,
        query_vector: List[float],
        top_k: int = 5,
        filter_fn: Optional[Callable[[Dict[str, Any]], bool]] = None
    ) -> List[Dict[str, Any]]:
        if len(query_vector) != self.dimension:
            raise ValueError(f"Query vector dimension {len(query_vector)} does not match index dimension {self.dimension}")

        scored: List[Dict[str, Any]] = []
        for rec in self.records.values():
            if filter_fn and not filter_fn(rec.metadata):
                continue
            sim = cosine_similarity(query_vector, rec.vector)
            scored.append({
                "id": rec.id,
                "score": round(sim, 4),
                "metadata": rec.metadata
            })

        scored.sort(key=lambda x: x["score"], reverse=True)
        return scored[:top_k]

    def size(self) -> int:
        return len(self.records)

    def clear(self) -> None:
        self.records.clear()
