from typing import Dict, Any, Optional
from datetime import datetime, timezone

class MutualDisclosureBroker:
    """Brokers bilateral mutual disclosure agreements between pods."""
    
    def __init__(self):
        self._agreements: Dict[str, Dict[str, Any]] = {}

    def request_disclosure(self, from_user: str, to_user: str, project_id: str) -> Dict[str, Any]:
        aid = f"{from_user}:{to_user}:{project_id}"
        agree = {
            "agreement_id": aid,
            "party_a": from_user,
            "party_b": to_user,
            "project_id": project_id,
            "party_a_consented": True,
            "party_b_consented": False,
            "status": "pending_b",
        }
        self._agreements[aid] = agree
        return agree
