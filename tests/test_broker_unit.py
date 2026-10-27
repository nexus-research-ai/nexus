from nexus_enforcement.broker import DataAccessBroker
from nexus_enforcement.pep import PolicyEnforcementPoint
from nexus_contracts.models import Principal
from nexus_contracts.lattice import Tier

def test_broker_redacts_confidential():
    broker = DataAccessBroker(PolicyEnforcementPoint())
    p = Principal(user_id="u1", institution_id="inst-1", department="EECS")
    rec = {"entity_id": "r1", "tier": Tier.CONFIDENTIAL, "payload": "secret"}
    out = broker.mediate_access(p, rec)
    assert "[REDACTED" in out["payload"]
