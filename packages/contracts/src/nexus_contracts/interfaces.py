from abc import ABC, abstractmethod
from typing import Any, Dict, List, Optional
from .lattice import Tier
from .projection import PublishableProjection
from .models import Principal, PolicyVerdict, AccessGrant, GroundingSource, GrantProposal

class IPolicyEnforcement(ABC):
    """The single Policy Enforcement Point (PEP) chokepoint (D4)."""

    @abstractmethod
    def evaluate_egress(self, projection: PublishableProjection, requester: Principal) -> PolicyVerdict:
        """Check outbound projection against allowlists and discoverability scope."""
        pass

    @abstractmethod
    def evaluate_drill_down(self, resource_id: str, requester: Principal) -> PolicyVerdict:
        """Owner-mediated drill-down re-deriving authority locally."""
        pass

class IModelProvider(ABC):
    """Interface for LLM serving engines."""

    @abstractmethod
    def generate(self, prompt: str, max_tokens: int, temperature: float = 0.2) -> str:
        pass

class IModelRouter(ABC):
    """Locality-aware AI model router."""

    @abstractmethod
    def select_provider(self, tier: Tier) -> IModelProvider:
        pass

class IRetrievalStrategy(ABC):
    """Hybrid retrieval across vector, lexical, and graph stores."""

    @abstractmethod
    def retrieve_grounding(self, claim: str, limit: int = 5) -> List[GroundingSource]:
        pass

class IGrantStore(ABC):
    """Authoritative, durable grant and proposal storage."""

    @abstractmethod
    def save_proposal(self, proposal: GrantProposal) -> None:
        pass

    @abstractmethod
    def get_proposal(self, proposal_id: str) -> Optional[GrantProposal]:
        pass

class IRevocationAuthority(ABC):
    """Local fail-closed revocation authority (D5)."""

    @abstractmethod
    def revoke(self, grant_id: str) -> int:
        """Revoke grant and return monotonic epoch counter."""
        pass

    @abstractmethod
    def is_revoked(self, grant_id: str) -> bool:
        pass

class IAuditSink(ABC):
    """Immutable hash-chained audit logging sink."""

    @abstractmethod
    def log_action(self, actor: Principal, action: str, resource_id: str, metadata: Dict[str, Any]) -> str:
        """Append audit entry and return cryptographic hash."""
        pass
