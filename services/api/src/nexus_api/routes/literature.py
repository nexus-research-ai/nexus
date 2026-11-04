from fastapi import APIRouter, Query
from nexus_discovery.literature import search_literature, build_literature_graph

router = APIRouter()


@router.get("/search")
def search(q: str = Query(..., min_length=1), limit: int = Query(default=10, ge=1, le=50)):
    return search_literature(q, limit)


@router.get("/graph")
def graph():
    return build_literature_graph()
