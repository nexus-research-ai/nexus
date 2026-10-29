from nexus_discovery.campus_graph import LivingCampusGraph, GraphNode, GraphEdge

def test_living_campus_graph():
    g = LivingCampusGraph()
    n1 = GraphNode(id="r1", label="Aria Malik", node_type="researcher", department="EECS")
    n2 = GraphNode(id="r2", label="Dr. Vasquez", node_type="researcher", department="Bioengineering")
    g.add_node(n1)
    g.add_node(n2)
    g.add_edge(GraphEdge(source_id="r1", target_id="r2", relation="matches", weight=0.94))

    assert len(g.nodes) == 2
    assert len(g.get_neighbors("r1")) == 1
    gaps = g.find_interdisciplinary_gaps("EECS", "Bioengineering")
    assert len(gaps) > 0
    assert gaps[0]["synergy_score"] == 92.5
