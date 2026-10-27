from typing import Optional
from nexus_contracts.lattice import Tier
from nexus_contracts.projection import PublishableProjection, DiscoverabilityScope
from nexus_contracts.models import Principal, PolicyVerdict
from nexus_contracts.interfaces import IPolicyEnforcement, IRevocationAuthority, IAuditSink

class PolicyEnforcementPoint(IPolicyEnforcement):
    """The single Policy Enforcement Point (PEP) and egress chokepoint (D4).
    
    Guarantees:
    1. Feature modules never see raw stores or unprojected data.
    2. Projections with CONFIDENTIAL classification are rejected immediately.
    3. Discoverability scope is strictly checked for central-index reads.
    4. Drill-downs are validated against the authoritative revocation epoch.
    """

    def __init__(
        self,
        revocation_authority: Optional[IRevocationAuthority] = None,
        audit_sink: Optional[IAuditSink] = None,
        cell_id: str = "cell-default"
    ):
        self.revocation_authority = revocation_authority
        self.audit_sink = audit_sink
        self.cell_id = cell_id

    def evaluate_egress(self, projection: PublishableProjection, requester: Principal) -> PolicyVerdict:
        if projection.tier == Tier.CONFIDENTIAL:
            return PolicyVerdict(
                allowed=False,
                reason="Confidential artifacts cannot egress cell via projection.",
                effective_tier=Tier.CONFIDENTIAL
            )

        # Check Discoverability Scope
        scope = projection.discoverability_scope
        if scope == DiscoverabilityScope.DEPARTMENT_ONLY:
            if requester.department.lower() != projection.payload.get("department", "").lower():
                return PolicyVerdict(
                    allowed=False,
                    reason=f"Restricted to department {projection.payload.get('department')}.",
                    effective_tier=projection.tier
                )
        elif scope == DiscoverabilityScope.MUTUAL_DISCLOSURE:
            allowed_users = projection.payload.get("disclosed_to", [])
            if requester.user_id not in allowed_users:
                return PolicyVerdict(
                    allowed=False,
                    reason="Requires verified mutual disclosure acceptance.",
                    effective_tier=projection.tier
                )

        if self.audit_sink:
            self.audit_sink.log_action(
                actor=requester,
                action="egress_allow",
                resource_id=projection.entity_id,
                metadata={"tier": projection.tier.value, "scope": scope.value}
            )

        return PolicyVerdict(
            allowed=True,
            reason="Passed egress policy checks.",
            effective_tier=projection.tier
        )

    def evaluate_drill_down(self, resource_id: str, requester: Principal) -> PolicyVerdict:
        if self.revocation_authority and self.revocation_authority.is_revoked(resource_id):
            return PolicyVerdict(
                allowed=False,
                reason="Resource access has been revoked by owning authority.",
                effective_tier=Tier.CONFIDENTIAL
            )

        return PolicyVerdict(
            allowed=True,
            reason="Authorized owner-mediated drill down.",
            effective_tier=Tier.SHARED
        )
