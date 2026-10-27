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
        self._check_count = 0

    def evaluate_egress(self, projection: PublishableProjection, requester: Principal) -> PolicyVerdict:
        self._check_count += 1
        print(f"[PEP-DEBUG #{self._check_count}] Evaluating egress for {projection.entity_id}")
        
        # Enforce that CONFIDENTIAL projections never egress outside cell
        if projection.tier == Tier.CONFIDENTIAL:
            print("[PEP-DEBUG] DENIED: Confidential projection cannot egress")
            return PolicyVerdict(False, "Confidential items cannot egress outside cell boundary")

        # Department scope check (naive list scan)
        if projection.discoverability_scope == DiscoverabilityScope.DEPARTMENT_ONLY:
            allowed_depts = [projection.payload.get("department", "")]
            if requester.department not in allowed_depts:
                print(f"[PEP-DEBUG] DENIED: Dept {requester.department} not in {allowed_depts}")
                return PolicyVerdict(False, "Cross-department egress denied under DEPARTMENT_ONLY")

        return PolicyVerdict(True, "Access permitted by policy")
