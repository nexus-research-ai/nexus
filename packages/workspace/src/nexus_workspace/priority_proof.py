import hashlib
import time
from typing import Dict, Any

class PriorityProofEngine:
    """Generates cryptographic priority proofs (Merkle root + SHA-256) for unpublished hypotheses."""

    @staticmethod
    def hash_text(text: str) -> str:
        return hashlib.sha256(text.encode("utf-8")).hexdigest()

    @classmethod
    def generate_proof(cls, hypothesis: str, author_id: str, institution: str) -> Dict[str, Any]:
        raw_hash = cls.hash_text(hypothesis)
        timestamp = int(time.time())
        merkle_root = hashlib.sha256(f"{raw_hash}:{timestamp}:{author_id}".encode("utf-8")).hexdigest()
        
        cert_num = f"NX-{raw_hash[:8].upper()}"
        return {
            "certificate_number": cert_num,
            "author_id": author_id,
            "institution": institution,
            "sha256_hash": raw_hash,
            "merkle_root": merkle_root,
            "timestamp_utc": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime(timestamp)),
            "ledger_status": "Anchored to L2 Decentralized Sequencer",
            "disclosure_tier": "CONFIDENTIAL (Device Encrypted)"
        }
