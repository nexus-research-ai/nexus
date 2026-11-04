import os
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from nexus_discovery.campus_graph import LivingCampusGraph, GraphNode, GraphEdge
from nexus_discovery.matcher import CollaboratorMatcher

router = APIRouter()
graph = LivingCampusGraph()
matcher = CollaboratorMatcher()

# Load full campus knowledge graph if dataset exists
DATA_PATH = os.environ.get("NEXUS_GRAPH_DATA", "/Users/anurag/Startups/nexus/data/nexus_full_graph.json")
if os.path.exists(DATA_PATH):
    graph.load_dataset(DATA_PATH)
else:
    # Pre-seed fallback graph
    graph.add_node(GraphNode(id="prof-1", label="Dr. Elena Vasquez", node_type="researcher", department="Bioengineering", metadata={"title": "Associate Professor"}))
    graph.add_node(GraphNode(id="prof-2", label="Dr. Marcus Thorne", node_type="researcher", department="EECS", metadata={"title": "Professor"}))
    graph.add_node(GraphNode(id="stud-1", label="Aria Malik", node_type="researcher", department="EECS", metadata={"degree": "MSCS Candidate"}))
    graph.add_edge(GraphEdge(source_id="stud-1", target_id="prof-2", relation="authors", weight=1.0))

@router.get("/search")
def search_campus(q: str = Query(..., min_length=1), limit: int = 10):
    nodes = graph.search_graph(q, limit)
    return {"query": q, "results": [n.model_dump() for n in nodes]}

@router.get("/gaps")
def get_interdisciplinary_gaps(dept_a: str = "EECS", dept_b: str = "Bioengineering"):
    return {"gaps": graph.find_interdisciplinary_gaps(dept_a, dept_b)}

@router.get("/graph")
def get_campus_graph(
    limit: int = Query(default=300, ge=1, le=2500),
    topic: Optional[str] = Query(default=None),
    center_id: Optional[str] = Query(default=None),
    hops: int = Query(default=2, ge=1, le=3)
) -> Dict[str, Any]:
    """Returns knowledge graph nodes and links formatted for ForceGraph2D visualizer."""
    return graph.query_graph(limit=limit, topic=topic, center_id=center_id, hops=hops)
