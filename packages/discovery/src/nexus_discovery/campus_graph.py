from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional

@dataclass
class GraphNode:
    id: str
    label: str
    node_type: str
    department: str
    skills: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)

@dataclass
class GraphEdge:
    source_id: str
    target_id: str
    relation: str
    weight: float = 1.0

# Initial hardcoded campus department graph stubs
MOCK_CAMPUS_DEPARTMENTS = [
    {"dept": "EECS", "building": "Cory Hall", "faculty_count": 84, "clusters": ["Systems", "AI", "Security"], "active_grants": 42},
    {"dept": "Bioengineering", "building": "Stanley Hall", "faculty_count": 42, "clusters": ["Neural Eng", "Biomechanics"], "active_grants": 28},
    {"dept": "Neuroscience", "building": "Barker Hall", "faculty_count": 31, "clusters": ["Cognitive", "Cellular"], "active_grants": 19},
    {"dept": "Statistics", "building": "Evans Hall", "faculty_count": 28, "clusters": ["High-dim Inference", "Probability"], "active_grants": 15},
    {"dept": "Mechanical Engineering", "building": "Etcheverry Hall", "faculty_count": 52, "clusters": ["Robotics", "Controls"], "active_grants": 33},
    {"dept": "Chemical Engineering", "building": "Tan Hall", "faculty_count": 36, "clusters": ["Catalysis", "Polymers"], "active_grants": 24},
    {"dept": "Physics", "building": "LeConte Hall", "faculty_count": 60, "clusters": ["Quantum", "Condensed Matter"], "active_grants": 38},
    {"dept": "Molecular & Cell Biology", "building": "Weill Hall", "faculty_count": 78, "clusters": ["Genetics", "Structural Bio"], "active_grants": 55},
    {"dept": "Mathematics", "building": "Evans Hall", "faculty_count": 65, "clusters": ["Topology", "Algebra", "Analysis"], "active_grants": 21},
    {"dept": "Materials Science", "building": "Hearst Mining", "faculty_count": 32, "clusters": ["Nanomaterials", "Electronic"], "active_grants": 26},
]

class LivingCampusGraph:
    """In-memory academic knowledge graph representation."""
    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []

    def add_node(self, node: GraphNode):
        self.nodes[node.id] = node

    def add_edge(self, edge: GraphEdge):
        self.edges.append(edge)

    def get_neighbors(self, node_id: str) -> List[str]:
        neighbors = []
        for e in self.edges:
            if e.source_id == node_id:
                neighbors.append(e.target_id)
            elif e.target_id == node_id:
                neighbors.append(e.source_id)
        return neighbors
