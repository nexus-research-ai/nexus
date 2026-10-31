import os
import json
import urllib.request
from typing import Dict, Any, Optional

# Static mock completion dictionary
MOCK_COMPLETIONS = {
    "nsf_summary": "We propose a zero-knowledge confidential research pod architecture establishing provable information flow control across federated academic boundaries.",
    "nsf_impacts": "The proposed research directly impacts privacy-preserving collaboration between universities, clinical hospitals, and national laboratories.",
    "nih_aims": "Specific Aim 1: Validate differential privacy on multi-site clinical EEG arrays without compromising high-frequency biomarker fidelity.",
    "nih_significance": "Overcoming institutional sharing friction enables unprecedented statistical power for rare neurological pathology detection.",
    "doe_abstract": "High-throughput edge neural signal processing leveraging neuromorphic compute primitives under strict information-theoretic boundary constraints.",
    "darpa_challenge": "Resilient decentralized synchronization of multi-agent academic intelligence swarms in adversarial zero-trust environments.",
    "figure_caption": "Figure 1: Spatial manifold alignment of cross-cohort neural telemetry features using optimal transport with differential privacy guarantees.",
    "default": "Synthesized scientific analysis with verified citation anchors and cryptographically audited provenance trail.",
}

class MetaClient:
    """Client for Meta LLaMA 3.3 and Muse reasoning models."""
    def __init__(self, api_key: Optional[str] = None):
        self.api_key = api_key or os.getenv("META_API_KEY", "")
        self.endpoint = "https://api.meta.ai/v1/chat/completions"

    def generate(self, prompt: str, max_tokens: int = 100, mock: bool = False) -> Dict[str, Any]:
        if mock or not self.api_key:
            reply = MOCK_COMPLETIONS.get("default", "")
            return {
                "text": reply,
                "model": "meta/llama-3.3-70b-instruct",
                "usage": {"prompt_tokens": len(prompt.split()), "completion_tokens": len(reply.split()), "cost_usd": 0.0005},
            }
        req = urllib.request.Request(
            self.endpoint,
            data=json.dumps({"prompt": prompt, "max_tokens": max_tokens}).encode("utf-8"),
            headers={"Authorization": f"Bearer {self.api_key}", "Content-Type": "application/json"}
        )
        with urllib.request.urlopen(req) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            return {"text": data.get("content", ""), "usage": data.get("usage", {})}
