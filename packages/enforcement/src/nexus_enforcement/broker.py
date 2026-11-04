from typing import Any, Dict
from nexus_contracts.models import Principal
from nexus_contracts.lattice import Tier
from .pep import PolicyEnforcementPoint

class DataAccessBroker:
    """The ONLY component permitted to hold raw store credentials."""

    def __init__(self, pep: PolicyEnforcementPoint):
        self.pep = pep

    def execute_query(self, requester: Principal, query_tier: Tier, query_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute query through PEP validation."""
        roles_lower = [r.lower() for r in requester.roles]
        if query_tier == Tier.CONFIDENTIAL and "faculty" not in roles_lower and "co-pi" not in roles_lower:
            raise PermissionError("Access to confidential research derivatives requires Co-PI authorization.")

        resource_id = query_data.get("resource_id")
        if resource_id:
            verdict = self.pep.evaluate_drill_down(resource_id, requester)
            if not verdict.allowed:
                raise PermissionError(f"PEP Access Denied: {verdict.reason}")

        if self.pep.audit_sink:
            self.pep.audit_sink.log_action(
                actor=requester,
                action="broker_query",
                resource_id=resource_id or "ad-hoc-query",
                metadata={"tier": query_tier.value, "roles": requester.roles}
            )

        return {"status": "success", "records": [], "tier": query_tier.value}
