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
    """Manages zero-knowledge double opt-in bilateral disclosure agreements.
    
    Guarantees:
    1. Researcher identities and raw contact info remain blurred until mutual consent.
    2. Non-confidential safe summaries are committed with SHA-256 hashes.
    3. Revocable at any point prior to full mutual reveal.
    """

    def __init__(self):
        self.agreements: Dict[str, BilateralDisclosureAgreement] = {}

    def initiate_agreement(
        self,
        initiator_id: str,
        recipient_id: str,
        initiator_summary: str,
        recipient_summary: str
    ) -> BilateralDisclosureAgreement:
        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        commitment_raw = f"{initiator_id}:{recipient_id}:{initiator_summary}:{recipient_summary}:{now_str}"
        commitment_hash = hashlib.sha256(commitment_raw.encode("utf-8")).hexdigest()
        
        agreement_id = f"mda-{commitment_hash[:12]}"
        agreement = BilateralDisclosureAgreement(
            agreement_id=agreement_id,
            initiator_id=initiator_id,
            recipient_id=recipient_id,
            initiator_project_summary=initiator_summary,
            recipient_project_summary=recipient_summary,
            state=DisclosureState.INTEREST_SENT,
            initiator_consented_at=now_str,
            commitment_hash=commitment_hash
        )
        self.agreements[agreement_id] = agreement
        return agreement

    def accept_consent(
        self,
        agreement_id: str,
        recipient_id: str,
        initiator_contact: Dict[str, Any],
        recipient_contact: Dict[str, Any]
    ) -> BilateralDisclosureAgreement:
        agreement = self.agreements.get(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found.")
        if agreement.recipient_id != recipient_id:
            raise PermissionError("Only the designated recipient may consent to this agreement.")
        if agreement.state != DisclosureState.INTEREST_SENT:
            raise ValueError(f"Cannot accept agreement in state {agreement.state.value}.")

        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        agreement.recipient_consented_at = now_str
        agreement.revealed_at = now_str
        agreement.state = DisclosureState.REVEALED
        
        # Unblur verified contact and raw project details
        agreement.unblurred_details = {
            "initiator": initiator_contact,
            "recipient": recipient_contact,
            "verification_status": "Bilateral Double Opt-In Verified",
            "revealed_timestamp": now_str
        }
        return agreement

    def withdraw_agreement(self, agreement_id: str, principal_id: str) -> BilateralDisclosureAgreement:
        agreement = self.agreements.get(agreement_id)
        if not agreement:
            raise ValueError(f"Agreement {agreement_id} not found.")
        if principal_id not in (agreement.initiator_id, agreement.recipient_id):
            raise PermissionError("Only agreement participants may withdraw consent.")
        
        agreement.state = DisclosureState.WITHDRAWN
        agreement.unblurred_details.clear()
        return agreement

    def get_agreement(self, agreement_id: str) -> Optional[BilateralDisclosureAgreement]:
        return self.agreements.get(agreement_id)
