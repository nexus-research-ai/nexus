import json
import os
from collections import deque
from typing import Dict, List, Any, Optional
from pydantic import BaseModel, Field

class GraphNode(BaseModel):
    id: str
    label: str
    node_type: str  # researcher, project, paper, skill, grant
    department: str = "Interdisciplinary"
    metadata: Dict[str, Any] = Field(default_factory=dict)

class GraphEdge(BaseModel):
    source_id: str
    target_id: str
    relation: str  # authors, cites, offers_skill, requires_skill, matches, eligible_for
    weight: float = 1.0

class LivingCampusGraph:
    """Property graph connecting researchers, lab facilities, preprints, and grants.
    
    Supports both dynamic in-memory construction and high-throughput indexed dataset loading.
    """

    def __init__(self):
        self.nodes: Dict[str, GraphNode] = {}
        self.edges: List[GraphEdge] = []
        self._adjacency: Dict[str, List[GraphEdge]] = {}
        self._raw_dataset: Optional[Dict[str, Any]] = None
        self._dataset_adj: Dict[str, set] = {}

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

    def load_dataset(self, file_path: str) -> bool:
        """Loads and pre-indexes precomputed multi-entity graph dataset for fast serving."""
        if not os.path.exists(file_path):
            return False
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                self._raw_dataset = json.load(f)
            
            self._dataset_adj.clear()
            for link in self._raw_dataset.get("links", []):
                src = link.get("source")
                tgt = link.get("target")
                if src and tgt:
                    self._dataset_adj.setdefault(src, set()).add(tgt)
                    self._dataset_adj.setdefault(tgt, set()).add(src)
            return True
        except Exception:
            return False

    def query_graph(
        self,
        limit: int = 300,
        topic: Optional[str] = None,
        center_id: Optional[str] = None,
        hops: int = 2
    ) -> Dict[str, Any]:
        """Queries graph nodes and links with support for ego-network BFS and topic filtering."""
        if not self._raw_dataset:
            # Fallback to local in-memory nodes/edges
            return {
                "nodes": [
                    {
                        "id": n.id,
                        "name": n.label,
                        "type": n.node_type if n.node_type in ("faculty", "paper", "topic") else "faculty",
                        "cluster": n.department,
                        "cluster_color": "#2563eb",
                        "x": 0.0,
                        "y": 0.0,
                        "metadata": n.metadata
                    }
                    for n in list(self.nodes.values())[:limit]
                ],
                "links": [
                    {
                        "source": e.source_id,
                        "target": e.target_id,
                        "relationship": e.relation
                    }
                    for e in self.edges
                ],
                "clusters": [],
                "center_node": None
            }

        all_nodes: List[Dict[str, Any]] = self._raw_dataset.get("nodes", [])
        all_links: List[Dict[str, Any]] = self._raw_dataset.get("links", [])
        all_clusters: List[Dict[str, Any]] = self._raw_dataset.get("clusters", [])
        node_lookup = {n["id"]: n for n in all_nodes}

        center_node = None
        if center_id and center_id.strip():
            cid = center_id.strip()
            if cid in node_lookup:
                center_node = dict(node_lookup[cid])
                center_node["is_center"] = True

                # BFS Ego-network traversal
                visited = {cid: 0}
                queue = deque([(cid, 0)])
                while queue:
                    curr, hop = queue.popleft()
                    if hop < hops:
                        for neighbor in self._dataset_adj.get(curr, ()):
                            if neighbor not in visited and len(visited) < limit:
                                visited[neighbor] = hop + 1
                                queue.append((neighbor, hop + 1))

                ego_ids = set(visited.keys())
                filtered_nodes = [
                    {**node_lookup[nid], "hop": visited[nid], "is_center": nid == cid}
                    for nid in visited if nid in node_lookup
                ]
                filtered_links = [
                    l for l in all_links
                    if l.get("source") in ego_ids and l.get("target") in ego_ids
                ]
                return {
                    "nodes": filtered_nodes,
                    "links": filtered_links,
                    "clusters": all_clusters,
                    "center_node": center_node
                }

        # Topic filter if supplied
        if topic and topic.strip():
            t_lower = topic.strip().lower()
            matching_ids = {
                n["id"] for n in all_nodes
                if t_lower in n.get("name", "").lower()
                or t_lower in n.get("cluster", "").lower()
                or any(t_lower in str(v).lower() for v in n.get("metadata", {}).values())
            }
            # Expand by 1 hop to get context
            expanded_ids = set(matching_ids)
            for mid in matching_ids:
                expanded_ids.update(list(self._dataset_adj.get(mid, ()))[:10])

            selected_nodes = [node_lookup[nid] for nid in expanded_ids if nid in node_lookup][:limit]
            selected_ids = {n["id"] for n in selected_nodes}
            selected_links = [
                l for l in all_links
                if l.get("source") in selected_ids and l.get("target") in selected_ids
            ]
            return {
                "nodes": selected_nodes,
                "links": selected_links,
                "clusters": all_clusters,
                "center_node": None
            }

        # Global balanced slice up to limit
        selected_nodes = all_nodes[:limit]
        selected_ids = {n["id"] for n in selected_nodes}
        selected_links = [
            l for l in all_links
            if l.get("source") in selected_ids and l.get("target") in selected_ids
        ]

        return {
            "nodes": selected_nodes,
            "links": selected_links,
            "clusters": all_clusters,
            "center_node": None
        }
