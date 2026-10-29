import math
from typing import List, Dict, Any, Tuple

class InMemoryVectorIndex:
    """In-memory vector store for academic publications and researcher skills."""
    def __init__(self):
        self._vectors: Dict[str, List[float]] = {}
        self._metadata: Dict[str, Dict[str, Any]] = {}

    def insert(self, item_id: str, embedding: List[float], metadata: Dict[str, Any]):
        self._vectors[item_id] = embedding
        self._metadata[item_id] = metadata

    def search_euclidean(self, query: List[float], top_k: int = 5) -> List[Tuple[str, float]]:
        scores = []
        for i_id, vec in self._vectors.items():
            dist = math.sqrt(sum((a - b) ** 2 for a, b in zip(query, vec)))
            scores.append((i_id, dist))
        scores.sort(key=lambda x: x[1])
        return scores[:top_k]
