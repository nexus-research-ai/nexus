from fastapi import APIRouter, Query
from typing import Optional
from nexus_discovery.campus_graph import LivingCampusGraph, GraphNode, GraphEdge
from nexus_discovery.matcher import CollaboratorMatcher, MatchProfile

router = APIRouter()
graph = LivingCampusGraph()
matcher = CollaboratorMatcher()

# Pre-seed sample campus graph
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
def get_full_graph():
    return graph.to_json_export()
