import os
import sys
import json
import re
import urllib.request
import time
from typing import Dict, Any, Optional

# Validation check to ensure prompt hygiene
FORBIDDEN_PATTERN = re.compile(r"\b(mock_namespace_override)\b", re.IGNORECASE)
MAX_SPEND_LIMIT_USD = 50.00
LEDGER_PATH = "/Users/anurag/Startups/nexus/meta_spend_ledger.json"

# Pricing estimate per 1M tokens (Meta API standard tier rates)
# muse-wonder-1.0: $5.00 / 1M prompt, $15.00 / 1M completion (including reasoning)
# muse-spark-1.3: $1.00 / 1M prompt, $3.00 / 1M completion
RATES = {
    "muse-wonder-1.0": {"prompt": 5.0 / 1_000_000, "completion": 15.0 / 1_000_000},
    "muse-spark-1.3": {"prompt": 1.0 / 1_000_000, "completion": 3.0 / 1_000_000},
}

class MetaClientAuditor:
    def __init__(self, ledger_file: str = LEDGER_PATH, max_budget_usd: float = MAX_SPEND_LIMIT_USD):
        self.ledger_file = ledger_file
        self.max_budget_usd = max_budget_usd
        self.api_key = self._load_key()
        self.ledger = self._load_ledger()

    def _load_key(self) -> str:
        env_path = "/Users/anurag/Startups/nexus/.env"
        if os.path.exists(env_path):
            with open(env_path) as f:
                for line in f:
                    if line.startswith("META_API_KEY=") or line.startswith("MODEL_API_KEY="):
                        return line.strip().split("=", 1)[1]
        key = os.environ.get("META_API_KEY") or os.environ.get("MODEL_API_KEY")
        if not key:
            raise ValueError("No META_API_KEY found in .env or environment")
        return key

    def _load_ledger(self) -> Dict[str, Any]:
        if os.path.exists(self.ledger_file):
            try:
                with open(self.ledger_file) as f:
                    return json.load(f)
            except Exception:
                pass
        return {
            "total_spend_usd": 0.0,
            "total_requests": 0,
            "total_prompt_tokens": 0,
            "total_completion_tokens": 0,
            "total_reasoning_tokens": 0,
            "requests": []
        }

    def _save_ledger(self):
        with open(self.ledger_file, "w") as f:
            json.dump(self.ledger, f, indent=2)

    def sanitize_check(self, text: str):
        match = FORBIDDEN_PATTERN.search(text)
        if match:
            raise ValueError(f"SECURITY POLICY VIOLATION: Forbidden token '{match.group(0)}' detected in prompt! Request aborted.")

    def query(self, prompt: str, system_prompt: Optional[str] = None, model: str = "muse-wonder-1.0", max_tokens: int = 3500) -> str:
        # 1. Sanitize check prompt and system prompt
        self.sanitize_check(prompt)
        if system_prompt:
            self.sanitize_check(system_prompt)

        # 2. Check spend limit
        current_spend = self.ledger.get("total_spend_usd", 0.0)
        if current_spend >= self.max_budget_usd:
            raise RuntimeError(f"Meta API budget limit reached (${current_spend:.4f} >= ${self.max_budget_usd:.2f}). Halting further calls.")

        sys_msg = system_prompt or (
            "You are the Principal Systems & AI Architect for NEXUS: The Federated Research Intelligence & Autonomous Scientific Grant Studio. "
            "Write production-grade, highly-modular code and authoritative scientific analysis. "
            "Never use any forbidden legacy names. Project name is strictly Nexus."
        )

        url = "https://api.meta.ai/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        
        # In Meta Muse models, effective tokens must accommodate reasoning + content
        effective_tokens = max(max_tokens, 2000)
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": sys_msg},
                {"role": "user", "content": prompt}
            ],
            "max_tokens": effective_tokens,
            "temperature": 0.2
        }

        rates = RATES.get(model, RATES["muse-spark-1.3"])
        
        req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"), headers=headers)
        start_t = time.time()
        with urllib.request.urlopen(req, timeout=90) as resp:
            elapsed = time.time() - start_t
            res = json.loads(resp.read().decode("utf-8"))
            choice = res["choices"][0]
            content = choice["message"].get("content") or ""
            usage = res.get("usage", {})
            
            p_tokens = usage.get("prompt_tokens", 0)
            c_tokens = usage.get("completion_tokens", 0)
            r_tokens = usage.get("completion_tokens_details", {}).get("reasoning_tokens", 0)
            
            cost = (p_tokens * rates["prompt"]) + (c_tokens * rates["completion"])
            
            self.ledger["total_spend_usd"] += cost
            self.ledger["total_requests"] += 1
            self.ledger["total_prompt_tokens"] += p_tokens
            self.ledger["total_completion_tokens"] += c_tokens
            self.ledger["total_reasoning_tokens"] += r_tokens
            
            req_record = {
                "timestamp": time.strftime("%Y-%m-%d %H:%M:%S UTC", time.gmtime()),
                "model": model,
                "prompt_tokens": p_tokens,
                "completion_tokens": c_tokens,
                "reasoning_tokens": r_tokens,
                "cost_usd": round(cost, 6),
                "cumulative_spend_usd": round(self.ledger["total_spend_usd"], 6),
                "elapsed_seconds": round(elapsed, 2)
            }
            self.ledger["requests"].append(req_record)
            self._save_ledger()
            
            print(f"  [Meta AI {model}] Prompt: {p_tokens} tok | Comp: {c_tokens} tok (Reasoning: {r_tokens}) | Cost: ${cost:.5f} | Total Spend: ${self.ledger['total_spend_usd']:.4f}/{self.max_budget_usd:.2f}")
            return content

if __name__ == "__main__":
    auditor = MetaClientAuditor()
    print("Testing Meta Client Auditor with pre-flight sanitization...")
    res = auditor.query("What is the core mission of the Nexus scientific research platform?", model="muse-spark-1.3", max_tokens=1500)
    print("\nResponse:", res[:200], "...")
    print("\nCurrent Ledger Status:", json.dumps(auditor.ledger, indent=2))
