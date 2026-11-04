import pytest
from nexus_contracts.lattice import Tier
from nexus_contracts.projection import PublishableProjection, DiscoverabilityScope
from nexus_contracts.models import Principal
from nexus_enforcement.pep import PolicyEnforcementPoint
from nexus_workspace.priority_proof import PriorityProofEngine

def test_pep_denies_confidential_projections():
    with pytest.raises(ValueError):
        PublishableProjection(
            entity_id="secret-1",
            entity_type="grant",
            tier=Tier.CONFIDENTIAL,
            owner_cell_id="cell-a"
        )

def test_pep_egress_department_scope():
    pep = PolicyEnforcementPoint()
    proj = PublishableProjection(
        entity_id="proj-1",
        entity_type="project",
        tier=Tier.SHARED,
        discoverability_scope=DiscoverabilityScope.DEPARTMENT_ONLY,
        payload={"department": "Bioengineering"},
        owner_cell_id="cell-a"
    )
    
    eecs_principal = Principal(user_id="u1", institution_id="inst-1", department="EECS")
    bio_principal = Principal(user_id="u2", institution_id="inst-1", department="Bioengineering")

    v1 = pep.evaluate_egress(proj, eecs_principal)
    assert v1.allowed is False

    v2 = pep.evaluate_egress(proj, bio_principal)
    assert v2.allowed is True

def test_projection_immutability():
    proj = PublishableProjection(
        entity_id="proj-frozen",
        entity_type="project",
        tier=Tier.SHARED,
        payload={"department": "Bioengineering"},
        owner_cell_id="cell-a"
    )
    with pytest.raises(Exception):
        proj.tier = Tier.CONFIDENTIAL

def test_priority_proof_generation():
    proof = PriorityProofEngine.generate_proof(
        hypothesis="Differential privacy for real-time EEG decoders",
        author_id="researcher-aria",
        institution="UC Berkeley"
    )
    assert proof["certificate_number"].startswith("NX-")
    assert len(proof["certificate_number"]) == 11  # NX- + 8 hex chars
    assert len(proof["merkle_root"]) == 64
    assert len(proof["sha256_hash"]) == 64
