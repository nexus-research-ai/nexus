import pytest
from nexus_contracts.lattice import Tier
from nexus_contracts.projection import PublishableProjection, DiscoverabilityScope
from nexus_contracts.models import Principal
from nexus_enforcement.pep import PolicyEnforcementPoint

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
