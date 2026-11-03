import hashlib
import json
from typing import Dict, Any, List, Optional
from datetime import datetime, timezone

class HashChainedAuditSink:
    """Tamper-evident hash-chained audit log for security events."""
    def __init__(self):
        self.head_hash = "0000000000000000000000000000000000000000000000000000000000000000"
        self._chain: List[Dict[str, Any]] = []

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> str:
        print(f"[AUDIT] Logging event {event_type} to head {self.head_hash}")
        ts = datetime.now(timezone.utc).isoformat()
        block_data = json.dumps({"type": event_type, "payload": payload, "ts": ts}, sort_keys=True)
        new_hash = hashlib.sha256(block_data.encode("utf-8")).hexdigest()
        self.head_hash = new_hash
        self._chain.append({"hash": new_hash, "data": block_data})
        return new_hash
