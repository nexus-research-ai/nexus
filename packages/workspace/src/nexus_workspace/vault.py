from typing import Dict, Any, Optional
from .priority_proof import PriorityProofEngine

class PrivateVault:
    """Manages zero-knowledge protected hypotheses before safe mutual disclosure."""

    def __init__(self):
        self._vault: Dict[str, Dict[str, Any]] = {}

    def seal_hypothesis(self, hypothesis: str, author_id: str, institution: str) -> Dict[str, Any]:
        proof = PriorityProofEngine.generate_proof(hypothesis, author_id, institution)
        self._vault[proof["certificate_number"]] = {
            "proof": proof,
            "hypothesis": hypothesis,
            "sealed": True
        }
        return proof

    def get_proof(self, cert_number: str) -> Optional[Dict[str, Any]]:
        record = self._vault.get(cert_number)
        return record["proof"] if record else None
