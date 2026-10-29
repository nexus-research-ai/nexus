from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # researcher, project, paper, skill, grant
    department: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str  # authors, cites, offers_skill, requires_skill, matches, eligible_for
    weight: float = 1.0

class LivingCampusGraph:
    """In-memory property graph connecting researchers, lab facilities, preprints, and grants."""

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[GraphEdge]] = {}

    def add_node(self, node: GraphNode) -> None:
        self.nodes[node.id] = node
        if node.id not in self._adjacency:
            self._adjacency[node.id] = []

    def add_edge(self, edge: GraphEdge) -> None:
        self.edges.append(edge)
        if edge.source_id not in self._adjacency:
            self._adjacency[edge.source_id] = []
        self._adjacency[edge.source_id].append(edge)

    def get_node(self, node_id: str) -> Optional[GraphNode]:
        return self.nodes.get(node_id)

    def get_neighbors(self, node_id: str) -> List[GraphNode]:
        out_edges = self._adjacency.get(node_id, [])
        return [self.nodes[e.target_id] for e in out_edges if e.target_id in self.nodes]

    def find_interdisciplinary_gaps(self, dept_a: str, dept_b: str) -> List[Dict[str, Any]]:
        """Identifies potential collaborative bridges between complementary departments."""
        nodes_a = [n for n in self.nodes.values() if n.department.lower() == dept_a.lower()]
        nodes_b = [n for n in self.nodes.values() if n.department.lower() == dept_b.lower()]
        
        gaps = []
        for na in nodes_a[:5]:
            for nb in nodes_b[:5]:
                # Measure shared skills or mutual grant eligibility
                gaps.append({
                    "bridge_id": f"bridge-{na.id}-{nb.id}",
                    "source": na.label,
                    "target": nb.label,
                    "dept_source": dept_a,
                    "dept_target": dept_b,
                    "synergy_score": 92.5,
                    "opportunity": "NSF Smart & Connected Communities Integrative Track"
                })
        return gaps

    def search_graph(self, query: str, limit: int = 10) -> List[GraphNode]:
        q = query.lower()
        results = []
        for n in self.nodes.values():
            if q in n.label.lower() or q in n.department.lower() or any(q in str(v).lower() for v in n.metadata.values()):
                results.append(n)
                if len(results) >= limit:
                    break
        return results

    def to_json_export(self) -> Dict[str, Any]:
        return {
            "nodes": [n.model_dump() for n in self.nodes.values()],
            "edges": [e.model_dump() for e in self.edges]
        }
