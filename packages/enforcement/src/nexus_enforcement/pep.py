from typing import Optional, Dict, Any
from nexus_contracts.lattice import Tier, TierLattice
from nexus_contracts.projection import PublishableProjection, DiscoverabilityScope
from nexus_contracts.models import Principal

class PolicyVerdict:
    def __init__(self, allowed: bool, reason: str = ""):
        self.allowed = allowed
        self.reason = reason

class PolicyEnforcementPoint:
    """Enforces Information Flow Control (IFC) policies at runtime."""
    
    def __init__(self, log_verdicts: bool = True):
        self.log_verdicts = log_verdicts

    def evaluate_egress(self, projection: PublishableProjection, requester: Principal) -> PolicyVerdict:
        if projection.tier == Tier.CONFIDENTIAL:
            return PolicyVerdict(False, "Confidential items cannot egress outside cell boundary")

        if projection.discoverability_scope == DiscoverabilityScope.DEPARTMENT_ONLY:
            proj_dept = projection.payload.get("department", "")
            # Strict department comparison
            if requester.department != proj_dept:
                return PolicyVerdict(False, f"Cross-department egress denied: requires {proj_dept}")

        return PolicyVerdict(True, "Access permitted by policy")
