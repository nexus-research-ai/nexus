import os
from fastapi import APIRouter, Query
from typing import Optional, Dict, Any
from nexus_discovery.campus_graph import LivingCampusGraph, GraphNode, GraphEdge
from nexus_discovery.matcher import CollaboratorMatcher

router = APIRouter()
graph = LivingCampusGraph()
matcher = CollaboratorMatcher()

# Resolve dataset path dynamically: env var -> relative repo data dir -> Docker path
REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "../../../../../"))
CANDIDATE_PATHS = [
    os.environ.get("NEXUS_GRAPH_DATA"),
    os.path.join(REPO_ROOT, "data", "nexus_full_graph.json"),
    os.path.join(REPO_ROOT, "data", "nexus_brain.json"),
    "/app/data/nexus_full_graph.json",
]
# Dynamic scan of data folder for any indexed knowledge graph exports
data_dir = os.path.join(REPO_ROOT, "data")
if os.path.isdir(data_dir):
    for f in os.listdir(data_dir):
        if f.endswith(".json") and "brain" in f:
            CANDIDATE_PATHS.append(os.path.join(data_dir, f))

loaded = False
for p in CANDIDATE_PATHS:
    if p and os.path.exists(p):
        if graph.load_dataset(p):
            loaded = True
            break

if not loaded:
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
