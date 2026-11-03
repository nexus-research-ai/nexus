import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class HashChainedAuditSink:
    """Tamper-evident hash-chained audit log for security events."""
    def __init__(self):
        self.head_hash = "GENESIS_NEXUS_AUDIT_LOG_2026"
        self._chain: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        ts = datetime.now(timezone.utc).isoformat()
        block_data = json.dumps({
            "prev_hash": self.head_hash,
            "type": event_type,
            "payload": payload,
            "ts": ts
        }, sort_keys=True)
        new_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        self.head_hash = new_hash
        self._chain.append({"hash": new_hash, "data": block_data})
        print(f"[AUDIT-CHAIN] Chained {event_type} -> {new_hash[:12]}")
        return new_hash
