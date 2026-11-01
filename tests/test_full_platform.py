from nexus_discovery.campus_graph import LivingCampusGraph, GraphNode, GraphEdge
from nexus_discovery.matcher import CollaboratorMatcher, MatchProfile
from nexus_funding.finder import FundingFinder
from nexus_funding.tracker import PursuitTracker
from nexus_intelligence.citation_auditor import CitationAuditor
from nexus_contracts.models import GroundingSource

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

def test_collaborator_matcher():
    matcher = CollaboratorMatcher()
    u1 = MatchProfile(
        user_id="u1",
        name="Aria Malik",
        department="EECS",
        academic_role="MSCS Candidate",
        offers_skills=["Differential Privacy", "PyTorch"],
        needs_skills=["Clinical EEG Data"]
    )
    u2 = MatchProfile(
        user_id="u2",
        name="Jordan Lee",
        department="Bioengineering",
        academic_role="PhD Researcher",
        offers_skills=["Clinical EEG Data", "Signal Processing"],
        needs_skills=["Differential Privacy"]
    )
    match = matcher.evaluate_match(u1, u2)
    assert match.compatibility_score >= 90
    assert "Clinical EEG Data" in match.they_offer
    assert "Differential Privacy" in match.you_offer

def test_citation_auditor():
    auditor = CitationAuditor()
    source = GroundingSource(
        source_id="s1",
        title="Optimal Transport for EEG Alignment",
        authors="Li, Verma et al.",
        year=2024,
        abstract="We show optimal transport aligns neural telemetry across diverse cohorts without privacy loss.",
        exact_quote="aligns neural telemetry across diverse cohorts without privacy loss",
        confidence_score=0.96
    )
    res = auditor.audit_claim("Optimal transport achieves cross-cohort neural telemetry alignment.", [source])
    assert res["status"] == "supported"
    assert res["grounding_score"] >= 80
