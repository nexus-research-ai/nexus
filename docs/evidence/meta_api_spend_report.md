# Meta API Spend Ledger & Financial Audit Report

## 1. Executive Summary

This report documents the empirical spend, token consumption, and model utilization of the Meta API during the development and benchmark evaluation of the Nexus scientific research platform. All requests are monitored in real time and recorded in `meta_spend_ledger.json` with strict budget clamping.

---

## 2. API Financial Ledger Breakdown

- **Allocated Hackathon Budget Ceiling:** $50.00 USD
- **Cumulative Production Spend to Date:** $0.045164 USD
- **Remaining Available Budget:** $49.954836 USD
- **Total API Invocations:** 8 requests
- **Total Ingested Tokens:** 15,886 tokens
  - Prompt tokens: 1,247 tokens
  - Output / Completion tokens: 14,639 tokens
  - Embedded Reasoning tokens: 14,407 tokens (98.4% reasoning density)

---

## 3. Rate Schedule & Pricing Models

| Model Architecture | Primary Task | Prompt Rate (per 1M) | Completion Rate (per 1M) |
|---|---|---|---|
| **Meta Muse Spark 1.3** | High-velocity grant synthesis & citation verification | $1.00 USD | $3.00 USD |
| **Meta Muse Wonder 1.0** | Deep-reasoning interdisciplinary gap detection & complex proofs | $5.00 USD | $15.00 USD |

---

## 4. Itemized Query Audit Trail

| Query # | Timestamp (UTC) | Model | Prompt Tokens | Completion Tokens | Reasoning Tokens | Latency (s) | Cost (USD) | Cumulative (USD) |
|---|---|---|---|---|---|---|---|---|
| **REQ-001** | 2026-11-04 20:12:05 | muse-spark-1.3 | 74 | 820 | 620 | 8.95s | $0.002534 | $0.002534 |
| **REQ-002** | 2026-11-04 20:13:35 | muse-spark-1.3 | 245 | 2,200 | 2,198 | 20.68s | $0.006845 | $0.009379 |
| **REQ-003** | 2026-11-04 20:13:59 | muse-spark-1.3 | 149 | 2,200 | 2,198 | 23.82s | $0.006749 | $0.016128 |
| **REQ-004** | 2026-11-04 20:14:22 | muse-spark-1.3 | 176 | 2,200 | 2,198 | 23.28s | $0.006776 | $0.022904 |
| **REQ-005** | 2026-11-04 20:14:46 | muse-spark-1.3 | 153 | 2,200 | 2,198 | 23.88s | $0.006753 | $0.029657 |
| **REQ-006** | 2026-11-04 20:15:11 | muse-spark-1.3 | 194 | 2,200 | 2,198 | 24.64s | $0.006794 | $0.036451 |
| **REQ-007** | 2026-11-04 20:58:35 | muse-spark-1.3 | 177 | 2,000 | 1,998 | 22.48s | $0.006177 | $0.042628 |
| **REQ-008** | 2026-11-04 22:27:30 | muse-spark-1.3 | 79 | 819 | 799 | 10.27s | $0.002536 | $0.045164 |

---

## 5. Automated Guardrails & Budget Enforcement

1. **Pre-flight Privacy Guard:** Every prompt payload is sanitized through regex validation prior to network dispatch to prevent confidential entity leakage.
2. **Hard Ceiling Clamp:** If `cumulative_spend_usd + estimated_cost > MAX_SPEND_LIMIT_USD ($50.00)`, the client immediately throws `BudgetExceededError` and reverts to local deterministic fixture inference.
3. **Reasoning Token Floor:** Configured minimum floor of 2,000 reasoning tokens on complex synthesis tasks to prevent truncated deduction chains while maintaining cost efficiency.
