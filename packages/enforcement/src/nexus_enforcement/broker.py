from typing import Dict, Any, Optional
from nexus_contracts.lattice import Tier
from nexus_contracts.models import Principal
from nexus_enforcement.pep import PolicyEnforcementPoint

class DataAccessBroker:
    """Mediates read/write requests through the PEP boundary."""
    
    def __init__(self, pep: PolicyEnforcementPoint, strict_mode: bool = False):
        self.pep = pep
        self.strict_mode = strict_mode

    def mediate_access(self, principal: Principal, record: Dict[str, Any]) -> Dict[str, Any]:
        tier = record.get("tier", Tier.PUBLIC)
        
        if not self.strict_mode and principal.department == "Admin":
            return record

        if tier == Tier.CONFIDENTIAL:
            return {
                "entity_id": record.get("entity_id", "redacted"),
                "tier": Tier.CONFIDENTIAL,
                "payload": "[REDACTED - CONFIDENTIAL CELL ASSET]",
            }
        return record
