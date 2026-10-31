import json
import urllib.request
import os
from typing import Optional, Dict, Any

class MetaMuseClient:
    """Client for Meta AI Frontier Models (Muse Wonder 1.0 & Muse Spark 1.3).
    
    Correctly manages reasoning tokens and content extraction.
    """

    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.meta.ai/v1"):
        self.api_key = api_key or os.environ.get("MODEL_API_KEY") or os.environ.get("META_API_KEY")
        self.base_url = base_url.rstrip("/")

    def complete(self, prompt: str, model: str = "muse-wonder-1.0", max_tokens: int = 2500, temperature: float = 0.2) -> Dict[str, Any]:
        if not self.api_key:
            raise ValueError("Meta API Key is required.")

        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        # In Meta Muse models, effective tokens must accommodate both reasoning and generation
        effective_tokens = max(max_tokens, 1500)
        payload = {
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": effective_tokens,
            "temperature": temperature
        }

        req = urllib.request.Request(
            f"{self.base_url}/chat/completions",
            data=json.dumps(payload).encode("utf-8"),
            headers=headers
        )
        with urllib.request.urlopen(req, timeout=60) as resp:
            data = json.loads(resp.read().decode("utf-8"))
            choice = data["choices"][0]
            return {
                "text": choice["message"].get("content") or "",
                "usage": data.get("usage", {}),
                "finish_reason": choice.get("finish_reason")
            }
