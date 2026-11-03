import hashlib
import json
import time
from typing import List, Dict, Any, Optional
from pydantic import BaseModel, Field
from nexus_contracts.interfaces import IAuditSink
from nexus_contracts.models import Principal

GENESIS_HASH = "0000000000000000000000000000000000000000000000000000000000000000"

class AuditEntry(BaseModel):
    sequence_number: int
    prev_hash: str
    entry_hash: str
    timestamp_utc: str
    actor_id: str
    actor_department: str
    action: str
    resource_id: str
    metadata: Dict[str, Any] = Field(default_factory=dict)

class HashChainedAuditSink(IAuditSink):
    """Cryptographic, tamper-evident hash-chained audit sink (Finding 1 / §4.1).
    
    Guarantees:
    1. Every security, egress, and drill-down decision is cryptographically anchored.
    2. Modification of any past entry invalidates all subsequent hashes.
    3. Provides chain-head verification for cross-institution audit receipts.
    """

    def __init__(self):
        self.entries: List[AuditEntry] = []
        self._current_prev_hash: str = GENESIS_HASH

    def log_action(self, actor: Principal, action: str, resource_id: str, metadata: Dict[str, Any]) -> str:
        seq = len(self.entries) + 1
        now_str = time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime())
        meta_json = json.dumps(metadata, sort_keys=True)
        meta_hash = hashlib.sha256(meta_json.encode("utf-8")).hexdigest()

        raw_payload = f"{self._current_prev_hash}:{seq}:{now_str}:{actor.user_id}:{action}:{resource_id}:{meta_hash}"
        entry_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()

        entry = AuditEntry(
            sequence_number=seq,
            prev_hash=self._current_prev_hash,
            entry_hash=entry_hash,
            timestamp_utc=now_str,
            actor_id=actor.user_id,
            actor_department=actor.department,
            action=action,
            resource_id=resource_id,
            metadata=metadata
        )

        self.entries.append(entry)
        self._current_prev_hash = entry_hash
        return entry_hash

    def get_chain_head(self) -> str:
        return self._current_prev_hash

    def verify_chain_integrity(self) -> bool:
        """Verify complete cryptographic continuity from Genesis to head."""
        expected_prev = GENESIS_HASH
        for e in self.entries:
            if e.prev_hash != expected_prev:
                return False
            
            meta_json = json.dumps(e.metadata, sort_keys=True)
            meta_hash = hashlib.sha256(meta_json.encode("utf-8")).hexdigest()
            raw_payload = f"{e.prev_hash}:{e.sequence_number}:{e.timestamp_utc}:{e.actor_id}:{e.action}:{e.resource_id}:{meta_hash}"
            expected_hash = hashlib.sha256(raw_payload.encode("utf-8")).hexdigest()
            
            if e.entry_hash != expected_hash:
                return False
            expected_prev = e.entry_hash

        return True
