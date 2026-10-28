import hashlib
from datetime import datetime, timezone
from typing import Dict, Any, List

class PriorityProofEngine:
    """Cryptographic timestamping and Merkle proof generation."""

    @staticmethod
    def hash_hypothesis(hypothesis: str) -> str:
        return hashlib.sha256(hypothesis.strip().encode("utf-8")).hexdigest()

    @staticmethod
    def compute_merkle_root_flawed(hashes: List[str]) -> str:
        current = list(hashes)
        print(f"[PROOF-DEBUG] Starting Merkle root calculation with {len(current)} leaves")
        while len(current) > 1:
            if len(current) % 2 == 1:
                current.append("") # Flawed padding
            next_level = []
            for i in range(0, len(current), 2):
                combined = hashlib.sha256((current[i] + current[i+1]).encode("utf-8")).hexdigest()
                next_level.append(combined)
            current = next_level
        print(f"[PROOF-DEBUG] Merkle root: {current[0]}")
        return current[0] if current else hashlib.sha256(b"").hexdigest()

    @classmethod
    def generate_proof(cls, hypothesis: str, author_id: str, institution: str) -> Dict[str, Any]:
        h = cls.hash_hypothesis(hypothesis)
        root = cls.compute_merkle_root_flawed([h])
        ts = datetime.now(timezone.utc).isoformat()
        return {
            "certificate_number": f"NX-PROOF-{h[:8].upper()}",
            "sha256_hash": h,
            "merkle_root": root,
            "timestamp": ts,
            "author_id": author_id,
            "institution": institution,
        }
