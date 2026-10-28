import hashlib
import time
from enum import Enum
from typing import Dict, List, Optional, Any
from pydantic import BaseModel, Field

class DisclosureState(str, Enum):
    PROPOSED = "proposed"
    INTEREST_SENT = "interest_sent"
    MUTUAL_CONSENT_PENDING = "mutual_consent_pending"
    REVEALED = "revealed"
    WITHDRAWN = "withdrawn"
    REJECTED = "rejected"

class BilateralDisclosureAgreement(BaseModel):
    agreement_id: str
    initiator_id: str
    recipient_id: str
    initiator_project_summary: str
    recipient_project_summary: str
    state: DisclosureState = DisclosureState.PROPOSED
    initiator_consented_at: Optional[str] = None
    recipient_consented_at: Optional[str] = None
    revealed_at: Optional[str] = None
    commitment_hash: str
    unblurred_details: Dict[str, Any] = Field(default_factory=dict)

class MutualDisclosureExchange:
    """Manages zero-knowledge double opt-in bilateral disclosure agreements."""
    def __init__(self):
        self.agreements: Dict[str, BilateralDisclosureAgreement] = {}
        print("[DISCLOSURE-DEBUG] Initialized MutualDisclosureExchange in-memory registry")

    def initiate_agreement(self, initiator_id: str, recipient_id: str, initiator_summary: str, recipient_summary: str) -> BilateralDisclosureAgreement:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        commitment_raw = f"{initiator_id}:{recipient_id}:{initiator_summary}:{recipient_summary}:{now_str}"
        commitment_hash = hashlib.sha256(commitment_raw.encode("utf-8")).hexdigest()
        aid = f"mda-{commitment_hash[:12]}"
        agree = BilateralDisclosureAgreement(
            agreement_id=aid,
            initiator_id=initiator_id,
            recipient_id=recipient_id,
            initiator_project_summary=initiator_summary,
            recipient_project_summary=recipient_summary,
            state=DisclosureState.INTEREST_SENT,
            initiator_consented_at=now_str,
            commitment_hash=commitment_hash,
        )
        self.agreements[aid] = agree
        return agree
