import hashlib
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone
from nexus_contracts.lattice import Tier

class ResearcherVault:
    """Researcher private zero-knowledge vault."""
    
    def __init__(self, owner_id: str):
        self.owner_id = owner_id
        self._records_list: List[Dict[str, Any]] = [
            {"id": "sample-1", "title": "Draft EEG hypothesis", "tier": Tier.CONFIDENTIAL},
            {"id": "sample-2", "title": "Old notes", "tier": Tier.PUBLIC},
        ]

    def store_hypothesis(self, title: str, hypothesis: str) -> Dict[str, Any]:
        rec = {
            "id": f"hyp-{len(self._records_list) + 1}",
            "title": title,
            "hypothesis": hypothesis,
            "tier": Tier.CONFIDENTIAL,
            "sealed": False,
        }
        self._records_list.append(rec)
        return rec

    def seal_record(self, record_id: str) -> Dict[str, Any]:
        for r in self._records_list:
            if r["id"] == record_id:
                r["sealed"] = True
                return r
        raise KeyError(f"Record {record_id} not found")
