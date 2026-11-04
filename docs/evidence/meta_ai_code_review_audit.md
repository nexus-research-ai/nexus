# Nexus Architecture & Code Quality Audit
**Conducted via Meta AI Frontier Reasoning (`muse-spark-1.3`)**  
**Date:** 2026-11-04 22:36:20 UTC  
**Total Spend:** $0.1509 / $50.00

---

## Section 1: IFC Lattice, PEP (D4), Broker & Audit Chain

# NEXUS Code Audit — Section 1: IFC Lattice, PEP (D4), Broker & Audit Chain

## 1. Executive Assessment (Rating: Needs Refactor)

**Verdict: Needs Refactor — Demo-Ready, Not Production-Ready.**

The core security architecture is **correctly conceived**: a total-order 3-tier lattice, fail-closed projection validator (D6), centralized PEP chokepoint (D4), credential-isolated broker, and hash-chained audit sink. Lattice math and audit-chain recomputation are sound.

However, the D4 chokepoint is **bypassable in its current form**: `evaluate_egress()` does not check revocation, `DataAccessBroker.execute_query()` never invokes the PEP, and `PublishableProjection` is mutable post-validation. For a hackathon demo this is defensible and highly demoable. For production federated deployment with cross-institution trust, these are P0 gaps requiring refactor before handling real CONFIDENTIAL derivatives.

**Risk summary:** No egress leak of `Tier.CONFIDENTIAL` via happy path. High risk of stale/revoked egress, scope-bypass, confused-deputy policy, race-forked audit chain, and in-memory audit loss.

---

## 2. Architectural Strengths & Invariants Verification

### 2.1 IFC Lattice — `lattice.py` — CORRECT

* **Total order correctly modeled:** `PUBLIC(1) < SHARED(2) < CONFIDENTIAL(3)` with explicit `__lt__/__le__/__gt__/__ge__`. Avoids default `Enum` incomparability bug.
* **MAX-rule correct:** `combine_tiers(*tiers) = max(level)` with `PUBLIC` identity for empty join. Matches formal join `⊔` for confidentiality lattice.
* **`permits_flow(source, sink) := source <= sink` correct:** Low-to-high allowed, high-to-low denied. This is Bell-LaPadula Simple Security + *-Property for confidentiality.
* **`validate_dominance(high, low) := high >= low` correct.**

Minor docstring imprecision: `permits_flow` comment says `(no read up, no write down)` — inverted. Code implements `no read up by low?` Actually implemented is `read-down / write-up allowed`, i.e., `no read-up, no write-down` is wrong phrasing. Should be `no read-up (low cannot read high is false)`. Correct property is: `no read-up violation?` Standard is: subject at HIGH can read LOW (read-down), cannot write LOW (no write-down). Code is right, comment is wrong.

### 2.2 Projection — `projection.py` — STRONG D6 ENFORCEMENT

* **Fail-closed validator:** `verify_non_confidential_payload` rejects `tier==CONFIDENTIAL` at model construction. This is the correct second barrier behind PEP D4.
* **Version pinning:** `projection_schema_version` + `lattice_version` present — enables cross-cell negotiation and revocation-epoch migration.
* **Explicit `DiscoverabilityScope` enum:** Avoids stringly-typed scope bugs.

### 2.3 PEP — `pep.py` — CORRECT CHOKepoint PLACEMENT

* **Immediate CONFIDENTIAL reject** on egress with `allowed=False`. Good.
* **Scope-aware branching** for `DEPARTMENT_ONLY` and `MUTUAL_DISCLOSURE`. Good intent.
* **Audit-on-allow** with tier + scope metadata. Good for receipts.

### 2.4 Broker — `broker.py` — CORRECT ISOLATION INTENT

* **Single credential holder pattern:** Declaring broker as ONLY raw-store accessor is the right zero-trust DB isolation principle. RBAC gate for `CONFIDENTIAL` requiring `faculty` / `co-pi` is directionally correct.

### 2.5 Audit Chain — `audit_chain.py` — CRYPTOGRAPHICALLY SOUND CORE

* **Genesis-anchored hash chain:** `GENESIS_HASH (32x0)` + `prev_hash:seq:timestamp:actor:action:resource:meta_hash -> SHA256` is tamper-evident. Any mutation invalidates suffix — verified correctly in `verify_chain_integrity()`.
* **Canonical metadata hashing:** `json.dumps(sort_keys=True)` + `sha256` prevents key-order forgery.
* **Recomputation check:** Verifier recomputes `meta_hash` and `entry_hash`, checks `prev_hash` linkage. Correct against silent edit / truncation (if head is pinned externally).

---

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### P0 — Critical: Chokepoint Bypasses

**[P0-1] Broker never calls PEP — D4 bypass.**
`DataAccessBroker.execute_query()` docstring claims `through PEP validation` but never calls `evaluate_egress()` or `evaluate_drill_down()`. Feature code calling broker directly gets raw-tier access with only a role string check. The entire D4 guarantee collapses to one `if` statement.

**[P0-2] Egress ignores revocation.**
`evaluate_egress()` never consults `revocation_authority.is_revoked()` nor compares `revocation_epoch`. A revoked / stale cached projection continues to egress indefinitely. `evaluate_drill_down()` checks revocation, egress does not — inverted priority.

**[P0-3] Mutable projection defeats D6 validator.**
`PublishableProjection` is a mutable Pydantic `BaseModel`. Attacker / buggy code can do:
```python
p = PublishableProjection(tier=SHARED, ...)
p.tier = Tier.CONFIDENTIAL  # no validator re-run
p.payload["ssn"] = "..."   # no field-level check
```
Validator runs only at construction. No `model_config = ConfigDict(frozen=True)`, no `validate_assignment=True`, no signature.

### P1 — High: Policy Logic Flaws

**[P1-1] Self-attesting policy attributes (Confused Deputy).**
```python
projection.payload.get("department", "")
projection.payload.get("disclosed_to", [])
```
Policy decision is derived from the untrusted `payload` dict itself, not from authenticated cell metadata / signed disclosure registry. A malicious owning cell can set `department=""` or `disclosed_to=[attacker]` to widen access. Must be separate authenticated fields with signature.

**[P1-2] Fail-open default scope + missing CONSORTIUM check.**
Default `discoverability_scope = ALL_CAMPUS` is fail-open. `ALL_CAMPUS` and `CONSORTIUM` fall through to `allowed=True` with zero checks. `CONSORTIUM` should require consortium membership proof; currently any `Principal` passes.

**[P1-3] Drill-down authorizes anyone.**
```python
def evaluate_drill_down(...): # no tier param, no owner proof
  if not revoked: return allowed=True, effective_tier=SHARED
```
No requester clearance check (`permits_flow`), no Co-PI / owner-mediation token, no audit log, hardcoded `SHARED`. Any authenticated user can drill down to any non-revoked resource.

**[P1-4] Deny-path audit blindness.**
`log_action` only on `allowed=True`. Denied egress / probes leave no trace. Violates claim `Every decision is anchored` and blinds intrusion detection. Attacker can enumerate departments / `disclosed_to` without audit.

**[P1-5] Broker RBAC brittle.**
`"faculty" not in requester.roles and "co-pi" not in requester.roles` — case-sensitive, no normalization, no hierarchy (`pi` > `co-pi`?), no `TierLattice.permits_flow` vs requester clearance. `query_data: Dict` unvalidated — injection / exfiltration via query predicates. No audit.

### P1 — High: Audit Chain Integrity & Liveness

**[P1-6] Race-forked chain (no concurrency control).**
`log_action` does read-modify-write on `self._current_prev_hash` + `len(entries)+1` with no `Lock`. Concurrent egresses produce duplicate `seq` / same `prev_hash` — forked chain where `verify_chain_integrity()` still returns `True` for first writer but second entry is orphaned / overwritten.

**[P1-7] No authenticity, only integrity.**
SHA-256 chain is tamper-evident, not tamper-resistant. No HMAC / Ed25519 signature on `entry_hash`. Anyone with sink write access can rewrite entire chain from genesis and present valid head. No external anchoring / cross-institution receipt signing. `get_chain_head()` returns bare string with no signed receipt.

**[P1-8] In-memory only + unbounded growth.**
`self.entries: List` volatile. Process crash = audit loss. No WAL, no persistence, no rotation. Violates non-repudiation for federated disputes.

**[P1-9] Linear chain mislabeled as Merkle.**
This is a hash chain, not a Merkle tree. No batch root, no inclusion proof (`prove(entry_i in head)` requires O(n) replay). Fine for hackathon, but cross-institution receipts will need Merkle batching or transparency-log style signed tree heads.

### P2 — Medium: Robustness / Correctness

* **`combine_tiers` no input validation:** `max()` with `key=t.level` throws `AttributeError` on non-`Tier`. Should enforce `isinstance` and return explicit join.
* **Lattice incompleteness:** No explicit `BOTTOM=PUBLIC`, `TOP=CONFIDENTIAL`, no `meet()` (greatest lower bound), no `join()` alias. Limits formal verification.
* **Version skew:** `LATTICE_VERSION="v1.0"` vs `lattice_version="v1.0"` vs `projection_schema_version="1.0.0"` — three formats, no compatibility check in PEP. Old cell can feed `v0.9` projection unchecked.
* **Department check crash / leak:** `requester.department.lower()` assumes non-None str; `payload.get("department")` leak in deny `reason` discloses internal org string.
* **`effective_tier=CONFIDENTIAL` on drill-down deny:** Leaks existence of confidential tier for revoked ID. Use `effective_tier=None` or requester clearance.
* **Audit timestamp fragility:** `time.strftime("%Y-%m-%d %H:%M:%S UTC")` — second granularity, no monotonicity check, locale-dependent, not ISO-8601. Two entries in same second are order-ambiguous except by `seq`. No timezone-aware `datetime`.
* **`verify_chain_integrity` missing seq continuity + timestamp monotonicity checks:** Skipped `seq` deletion (e.g., remove entry and renumber) would still verify if attacker recomputes hashes — detection relies entirely on external head pinning, which doesn't exist yet.
* **`json.dumps` without `separators=(',',':')`:** Whitespace-dependent hashing is stable within Python but fragile cross-language (Go/Rust verifier would diverge).
* **`cell_id` unused, `revocation_authority` Optional fail-open:** If `None`, PEP silently allows. Should fail-closed in production config.

---

## 4. Concrete Recommendations for Hackathon Demo & Hardening

### A. Demo Script (Lean Into Strengths — 5 min)

1.  **MAX-rule live:** `combine_tiers(PUBLIC, SHARED) -> SHARED`, `combine_tiers(SHARED, CONFIDENTIAL) -> CONFIDENTIAL`. Show lattice diagram.
2.  **D6 block:** Attempt `PublishableProjection(tier=CONFIDENTIAL)` → Pydantic `ValueError

---

## Section 2: Researcher Vault, Priority Proofs & Mutual Disclosure

# NEXUS Code Audit — Section 2: Researcher Vault, Priority Proofs & Mutual Disclosure

## 1. Executive Assessment (Rating: Needs Refactor)

**Rating: Needs Refactor — Demo Functional, Not Production Ready.**

The module correctly separates concerns (`vault.py` storage, `priority_proof.py` cryptography, `mutual_disclosure.py` handshake) and implements a legible happy-path for seal → propose → consent → reveal. For a hackathon demo this will run.

For production with cryptographic priority claims, it **cannot ship as-is**. Three blocking misrepresentations:

1.  Claimed `RFC 6962 Merkle` timestamping is not a Merkle tree and not RFC 6962.
2.  Claimed `Anchored to L2 Decentralized Sequencer` is a hardcoded string with no anchoring.
3.  Claimed `zero-knowledge / device encrypted` vault stores plaintext hypotheses in-process.

Certificate ID space is 9,000 values with silent overwrite — guaranteed collision in real use. Bilateral handshake is single-confirm, ID-string authenticated, and revocable-after-reveal.

> **Verdict:** Keep for demo with disclaimers. Refactor crypto, identity, persistence, and state machine before testnet / user data.

## 2. Architectural Strengths & Invariants Verification

**What is done well:**

*   Clean modularity: `PrivateVault` delegates hashing to `PriorityProofEngine`, no crypto duplicated in vault.
*   `DisclosureState` as `str, Enum` + `BilateralDisclosureAgreement` as Pydantic `BaseModel` gives serialization, validation, and OpenAPI compatibility for free.
*   `accept_consent()` correctly checks existence, `recipient_id` match, and `state == INTEREST_SENT` before reveal. `withdraw_agreement()` correctly checks participant membership.
*   `get_proof()` returns proof only, not hypothesis — correct minimal disclosure for that accessor.
*   Commitment pattern intent is correct: `sha256(initiator:recipient:summaries:timestamp)` + `agreement_id = mda-{hash[:12]}` is deterministic and debuggable.

**Invariants verification:**

| Invariant | Status | Evidence |
| :--- | :--- | :--- |
| Identities blurred until mutual consent | **PARTIAL PASS** | `unblurred_details` empty until `REVEALED`. However summaries + IDs stored plaintext in agreement from creation, no redaction layer. Contacts passed at `accept` time, not leaked earlier — good. |
| Summaries committed with SHA-256 | **WEAK PASS** | Hash exists, but no canonicalization, no nonce, second-granularity timestamp. Malleable. |
| Revocable prior to reveal | **PASS** | `WITHDRAWN` clears `unblurred_details`, blocks later `accept` via state guard. |
| Zero-knowledge / device-encrypted vault | **FAIL** | `self._vault[cert] = {"proof":..., "hypothesis": hypothesis, "sealed": True}` stores plaintext. No encryption, no ZK proof, `sealed` flag never enforced. |
| RFC 6962 Merkle timestamping | **FAIL** | `sha256(f"{hash}:{timestamp}:{author_id}")` is not RFC 6962. No `0x00`/`0x01` domain separation, no tree, no inclusion proof, no Signed Tree Head. |
| Ledger anchoring | **FAIL** | `ledger_status: "Anchored to L2..."` is static string. No tx hash, no sequencer client, no async confirmation. |
| Double opt-in bilateral consent | **FAIL** | Initiator auto-consented on `initiate`. No signatures. Only recipient action required to reveal. `MUTUAL_CONSENT_PENDING` and `PROPOSED` states defined but never used. |

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### P1 — Critical: Certificate collision + silent vault overwrite
```python
cert_num = f"NX-{int(raw_hash[:8], 16) % 9000 + 1000}" # 9000 values
self._vault[proof["certificate_number"]] = {...} # overwrite, no check
```
Birthday bound ~112 proofs for 50% collision. Attacker can grind hypothesis to collide with victim cert and overwrite vault. Predictable, enumerable. No UUID, no collision check, no thread lock.

### P1 — Critical: False RFC 6962 + untrusted time
*   No leaf prefix `SHA256(0x00 || data)`, no node prefix `SHA256(0x01 || left || right)`. Mislabeled.
*   `int(time.time())` is host-manipulable. No RFC 3161 TSA, no Roughtime, no ledger. Priority dispute unresolvable. `time.strftime(...gmtime())` is naive string, not ISO-8601, no monotonicity check.
*   No nonce/salt: `hash_text(hypothesis)` is deterministic dictionary-attackable for low-entropy ideas. No Unicode normalization (NFC) — `café` vs `cafe\u0301` produce different proofs.

### P1 — High: Handshake authentication is string comparison
```python
if agreement.recipient_id != recipient_id: raise PermissionError
```
No public-key signature, no session auth, no capability token. Anyone who knows/guesses `recipient_id` (often email/handle) can consent. No Ed25519/ECDSA signature on `commitment_hash` by either party. Initiator consent is implicit, not explicit cryptographic consent.

### P2 — High: Incomplete / unsafe state machine
Defined: `PROPOSED, INTEREST_SENT, MUTUAL_CONSENT_PENDING, REVEALED, WITHDRAWN, REJECTED`
Used: `INTEREST_SENT -> REVEALED | WITHDRAWN`

*   `initiate` skips `PROPOSED`, sets `initiator_consented_at=now` without proof.
*   `MUTUAL_CONSENT_PENDING` never entered — no true two-step flow.
*   `REJECTED` dead code — no `reject_agreement()` method.
*   `withdraw_agreement()` allows `REVEALED -> WITHDRAWN` + `unblurred_details.clear()`. Cryptographically meaningless post-reveal (data already copied) and destroys audit trail. Should be terminal: no transitions out of `REVEALED` except audit-logged.
*   No idempotency / race guard: double `accept_consent` concurrently both pass `state==INTEREST_SENT` check in threaded server (no `Lock`).

### P2 — Medium: Commitment malleability + truncation
`f"{initiator_id}:{recipient_id}:{initiator_summary}:{recipient_summary}:{now_str}"` with `:` delimiter is ambiguous (summary containing `:` collides), uncanonicalized (whitespace/case), second-resolution `now_str` allows replay within same second. `agreement_id = mda-{hash[:12]}` is 48-bit truncation — acceptable for demo but needs collision loop.

### P3 — Medium: Privacy / storage gaps
*   Vault + agreements are in-memory `Dict`, no persistence, no encryption at rest, no `threading.Lock`, `get_agreement()` returns mutable reference allowing external mutation bypassing state machine.
*   `unblurred_details` holds raw PII dicts plaintext. No field-level encryption, no TTL, no redaction log.
*   Empty-string summaries, empty hypothesis, multi-MB hypothesis (SHA-256 DoS) not validated. Pydantic model lacks `min_length`, `max_length`.
*   `withdraw` does not clear `initiator_consented_at/recipient_consented_at/revealed_at` — leaves inconsistent forensic state.

## 4. Concrete Recommendations for Hackathon Demo & Hardening

**For demo ( < 2 hours, keep API stable ):**

1.  Fix cert collision now, keep format:
    ```python
    import uuid, datetime
    cert_num = f"NX-{uuid.uuid4().hex[:8].upper()}"
    # + loop while cert_num in self._vault
    timestamp = datetime.datetime.now(datetime.timezone.utc)
    ```
    Change copy to `"ledger_status": "PENDING_DEMO_ANCHOR (mock)"` — do not claim L2 anchoring on stage.

2.  Add explicit transition guard + `reject` to complete story:
    ```python
    _ALLOWED = {
      DisclosureState.INTEREST_SENT: {DisclosureState.REVEALED, DisclosureState.WITHDRAWN, DisclosureState.REJECTED},
      DisclosureState.PROPOSED: {DisclosureState.INTEREST_SENT, DisclosureState.WITHDRAWN},
    }
    def reject_agreement(...): # sets REJECTED, clears details
    def withdraw_agreement(...):
      if agreement.state == DisclosureState.REVEALED:
        raise ValueError("Already revealed - cannot withdraw, audit only")
    ```

3.  Add `threading.Lock` around `self._vault` and `self.agreements`, return `copy.deepcopy()` from getters. Add Pydantic constraints: `Field(min_length=1, max_length=5000)` for summaries/hypothesis.

**For production hardening (post-hackathon):**

1.  **True RFC 6962 + priority:**
    ```python
    def rfc6962_leaf(b: bytes): return hashlib.sha256(b'\x00' + b).digest()
    def rfc6962_node(l: bytes, r: bytes): return hashlib.sha256(b'\x01' + l + r).digest()
    ```
    Build canonical leaf = `NFC(hypothesis) || author_pubkey || nonce32 || timestamp_RFC3339`. Generate `nonce = secrets.token_bytes(32)`, store `salted_commitment = sha256(nonce || hypothesis)`. Return inclusion proof + Signed Tree Head from Trillian / Sigstore Rekor / actual L2 anchor with `tx_hash` and async `ANCHOR_CONFIRMED` status. Integrate RFC 3161 TSA or `opentimestamps`.

2.  **Real double opt-in:** Require Ed25519 signatures over `commitment_hash` from both keypairs. Flow: `PROPOSED -> INTEREST_SENT (initiator_sig) -> MUTUAL_CONSENT_PENDING (recipient_sig_intent) -> REVEALED (both sigs verified + key exchange)`. Store `initiator_sig`, `recipient_sig`, `initiator_pubkey`. Never trust raw `*_id` strings.

3.  **Encrypted vault:** Replace `Dict[str, plaintext]` with Fernet / age-encrypted envelope with per-user DEK via KMS, or client-side E2EE where server stores only `commitment`. Add `unseal(reveal_token)` with authz, append-only audit log (`sealed_at, access_log, withdraw_log`), TTL/expiry, and persistence (SQLite/Postgres + SQLAlchemy).

4.  **Tests to add before merge:** cert uniqueness fuzz (10k proofs), unicode normalization test, state fuzz (`accept-after-withdraw`, `withdraw-after-reveal`, `double-accept race`), commitment malleability (`a:b` vs `a:b` with colon), timestamp monotonicity.


---

## Section 3: Living Campus Graph & Vector Collaborator Matcher

# NEXUS Code Audit — Section 3: Living Campus Graph & Vector Collaborator Matcher

## 1. Executive Assessment (Rating: Needs Refactor)

**Verdict: Needs Refactor — Demo-Functional, Not Production-Ready.**

`vector_index.py` is solid and close to production-ready for in-memory scale. `campus_graph.py` and `matcher.py` are well-structured scaffolds with correct Pydantic boundaries, but core scientific logic — `find_interdisciplinary_gaps()` and `evaluate_match()` — is currently stubbed with hardcoded constants and does not implement true graph weighting or bilateral complementarity.

| Module | Rating | Rationale |
| :--- | :--- | :--- |
| `vector_index.py` | **Minor Polish** | Correct cosine math, dimension guards, clean `filter_fn` extension point. Missing hardening for NaN/Inf, normalization caching, CRUD. |
| `campus_graph.py` | **Needs Refactor** | Graph container is sound; gap analysis is `92.5` hardcoded cartesian product with no traversal, no edge weights, no de-duplication against existing collaborations. |
| `matcher.py` | **Needs Refactor** | Directionally correct bilateral intersection check, but scoring is `65+15+15+4` heuristic, case-sensitive exact match, ignores `available_hours_per_week`, leaks full skill lists pre-consent. |

**For hackathon:** Ship as-is with seeded demo data, it will demo well. **For production:** Do not ship gap scoring or matcher ranking without fixing Sections 3 and 4 below.

## 2. Architectural Strengths & Invariants Verification

**Verified Invariants — PASS:**

*   **Type Safety:** Correct use of `BaseModel` for `GraphNode`, `GraphEdge`, `MatchProfile`, `MatchResult`, `VectorRecord`. `Field(default_factory=...)` avoids mutable-default bug. Good.
*   **Cosine Correctness:** `cosine_similarity()` correctly implements `dot / (||a||*||b||)`, raises on dim mismatch, returns `0.0` on zero-norm instead of `NaN`/`ZeroDivisionError`. Verified.
*   **Dimension Enforcement:** Both `add_vector()` and `search()` enforce `len(vector) == dimension`. Prevents silent index corruption. Good.
*   **Separation of Concerns:** Graph topology (`campus_graph`), semantic similarity (`vector_index`), and team formation logic (`matcher`) are correctly decoupled. This is the right Nexus modularity.
*   **Extensibility Hook:** `filter_fn: Optional[Callable[[Dict], bool]]` in vector search is excellent — enables department/grant-eligibility pre-filtering without coupling index to schema.
*   **Dangling Edge Tolerance:** `get_neighbors()` filters `if e.target_id in self.nodes`. Prevents KeyError on orphan edges.

**Architectural Strengths to Keep:**

1.  In-memory adjacency dict `_adjacency` gives O(1) out-edge lookup — correct foundation for BFS / weighted walk later.
2.  `to_json_export()` using `model_dump()` is export-safe for frontend visualization.
3.  Matcher correctly computes *both directions*: `user->candidate` and `candidate->user` intersections. This bilateral intent is scientifically correct, implementation just needs calibration.

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### A. Interdisciplinary Gap Analysis — Critical Logic Gap

**File:** `campus_graph.py:find_interdisciplinary_gaps()`

1.  **[Critical] Hardcoded Science:** `synergy_score: 92.5` and `opportunity: "NSF Smart & Connected Communities..."` are constants for every pair. No skill overlap, graph distance, or grant eligibility is computed. Demo will show identical scores for all bridges.
2.  **[High] Arbitrary Truncation:** `nodes_a[:5]` / `nodes_b[:5]` uses insertion order, not ranking. With 500 researchers, 99% of graph is ignored non-deterministically.
3.  **[High] No Gap Semantics:** Function returns pairs that may *already* be collaborating. Never checks `self.edges` for existing `matches` / `authors` edge between `na` and `nb`. A gap must be `high potential + no existing edge`.
4.  **[High] No Type Filtering:** Filters only by `department`. Will bridge `paper-paper`, `grant-skill`, `skill-skill` nodes. Should restrict to `node_type == researcher` or `project`.
5.  **[Medium] No Normalization:** `dept_a.lower() == dept_b.lower()` is good, but no `.strip()`, no handling of `""`, `None`, aliases (`CS` vs `Computer Science`).

### B. Graph Edge Weighting — Unused

**File:** `campus_graph.py:GraphEdge / add_edge()`

1.  **[High] Weight Dead Field:** `weight: float = 1.0` is stored but never read, aggregated, normalized, or decayed. No weighted traversal, PageRank, or shortest-path uses it.
2.  **[High] No Validation:** `add_edge()` does not verify `source_id`/`target_id` exist, does not validate `relation` vocabulary (typo `offer_skill` vs `offers_skill` creates silent disconnected graph), does not validate `weight >= 0`, does not deduplicate parallel edges.
3.  **[Medium] Directed-Only View:** `_adjacency` indexes only `source_id`. `get_neighbors()` returns out-neighbors only. No `get_predecessors()`, no undirected traversal for collaborator discovery. Interdisciplinary bridges require bidirectional search.
4.  **[Medium] No Removal / Update:** No `remove_node`, `remove_edge`, `upsert`. Stale researcher profiles cannot be evicted; memory grows unbounded.
5.  **[Low] DoS Surface:** `search_graph()` does `any(q in str(v).lower() for v in metadata.values())` on every node — O(N * M) string conversion per keystroke. No index, no ranking, early `break` on `limit` returns arbitrary first-hits, not best-hits.

### C. Cosine Similarity Vector Indexing — Sound but Brittle

**File:** `vector_index.py`

1.  **[Medium] No NaN/Inf Guard:** `add_vector()` validates length but not `math.isfinite(x)`. Single `NaN` poisons all future `cosine_similarity` scores to `NaN` and breaks `sort`.
2.  **[Medium] O(N) Brute Force:** Acceptable for <10k vectors (hackathon scale), but no docstring warning, no batch path, no pre-normalized norms cache. Each `search()` recomputes `norm_v2` for all records redundantly.
3.  **[Medium] Missing CRUD:** No `delete()`, `update()`, `get()`. Cannot remove graduated researchers or rotate embeddings after model upgrade (dimension change requires full `clear()`).
4.  **[Low] `top_k` Unvalidated:** `top_k=0`, negative, or `top_k=1000000` not clamped. `filter_fn` exceptions propagate unhandled.
5.  **[Low] Non-Deterministic Ties:** `sort(key=score)` with equal scores yields insertion-order tiebreak. Add secondary sort by `id` for reproducible demo ranking.

### D. Bilateral Complementarity Scoring — Heuristic + Privacy Leak

**File:** `matcher.py:evaluate_match()`

1.  **[Critical] Privacy Violation vs. Stated Double Opt-In:** Docstring promises `double opt-in reveals`, but `they_offer=candidate.offers_skills` and `you_offer=user.offers_skills` expose *full* skill lists at `status="proposed"`. Must mask until `mutual_revealed`. This leaks PII/capability data pre-consent.
2.  **[High] Inflated Base Score:** `score = 65` base means two researchers with *zero* overlapping skills still score 65-69 (`+4` if different departments). Ranking will appear uniformly high and meaningless. No calibration to 0-100.
3.  **[High] Brittle Exact Match:** `set(user.offers_skills).intersection(...)` is case/whitespace sensitive: `Python` != `python`, `ML` != `Machine Learning`. No `normalize_skill()`; recall will be near-zero on real data.
4.  **[High] Unused Capacity Signal:** `available_hours_per_week` is collected but never used. A 2hr/week candidate scores same as 20hr/week.
5.  **[High] Misleading Rationale:** `f"...offers expertise in {', '.join(candidate.offers_skills[:2])}"` cites first 2 skills even if they do *not* intersect `user.needs_skills`. Generates false explanations — hallucinated justification.
6.  **[Medium] No Self-Match / Duplicate Guard:** No check for `user.user_id == candidate.user_id`. Self-match scores 98.
7.  **[Medium] Asymmetric Rationale, Symmetric Score:** Score is symmetric, rationale is directional — correct, but no `evaluate_pair()` wrapper to ensure consistent bidirectional display.
8.  **[Low] `compatibility_score: int`:** Loses granularity. Should be `float` 0-100 with rounding for ranking stability.

## 4. Concrete Recommendations for Hackathon Demo & Hardening

### A. Hackathon Demo — Ship in <2 Hours (High Impact, Low Effort)

1.  **Seed to Hide Stubs:** Pre-load 24 researchers (12 CS + 12 Bio/Urban), 8 skills, 6 grants. Pre-compute gaps so hardcoded `92.5` is less obvious; vary scores in seed wrapper for demo visualization.
2.  **Mask Skills for Double Opt-In Story:** For demo, only return intersecting skills in `they_offer`/`you_offer`, not full lists. One-line fix that makes privacy story credible:
    ```python
    they_offer = sorted(set(candidate.offers_skills) & set(user.needs_skills))
    you_offer = sorted(set(user.offers_skills) & set(candidate.needs_skills))
    ```
3.  **Normalize Before Match:** Add 5-line helper and use everywhere:
    ```python
    def _norm(s: str) -> str: return s.strip().lower()
    ```
4.  **Fix Rationale to Use Intersection:** Change rationale to cite actual complement, not `[:2]`:
    ```python
    mutual = set(map(_norm, candidate.offers_skills)) & set(map(_norm, user.needs_skills))
    rationale = f"Complements you on {', '.join(sorted(mutual)) or 'adjacent methods'}; interdisciplinary bridge {user.department} ↔ {candidate.department}." if mutual else "Adjacent expertise — no direct skill cover, potential methods transfer."
    ```

### B. Hardening — Production-Grade Path

**1. Enforce Vocabularies with `Literal`:**
```python
from typing import Literal
NodeType = Literal["researcher","project","paper","skill","grant"]
Relation = Literal["authors","cites","offers_skill","requires_skill","matches","eligible_for"]
```

**2. True Edge-Weighted Gap Score (replace hardcoded 92.5):**
```python
def gap_score(na, nb, jaccard: float, dept_bonus: float, graph_dist: int) -> float:
    # jaccard on skill sets, dept_bonus 1.0 if different, graph_dist penalty if already close
    if graph_dist <= 1: return 0.0  # already collaborating, not a gap
    return round(100 * (0.6*jaccard + 0.25*dept_bonus + 0.15*(1.0/graph_dist)), 2)
```
Implement `has_edge(a,b)`, BFS `shortest_path_len()`, and aggregate multi-edge weights: `w = sum(e.weight for e in edges(a,b))`.

**3. Calibrated Bilateral Complementarity (replace 65+15+15+4):**
```python
def bilateral_score(u: MatchProfile, c: MatchProfile) -> float:
    u_cover = len(U_offers & C_needs) / max(1, len(C_needs))
    c_cover = len(C_offers & U_needs) / max(1, len(U_needs))
    jacc = len((U_offers|U_needs) & (C_offers|C_needs)) / max(1, len((U_offers|U_needs)|(C_offers|C_needs)))
    inter = 1.0 if u.department.strip().lower() != c.department.strip().lower() else 0.0
    hours = min(u.available_hours_per_week, c.available_hours_per_week) / 10.0  # cap
    return round(100*(0.35*u_cover + 0.35*c_cover + 0.15*jacc + 0.10*inter + 0.05*min(hours,1.0)), 2)
```
Clamp 0-100, return `float`, block self-match, require `u_cover>0 or c_cover>0` else score <40.

**4. Vector Index Hardening:**
* Validate `all(math.isfinite(x) for x in vector)` on write; raise `ValueError`.
* Pre-normalize and cache norms: `self._norms[record_id] = norm`; store unit vectors for dot-only search (3x faster).
* Add `remove(record_id)`, `upsert()`, `get()`, clamp `top_k = max(1, min(top_k, len(records)))`, secondary sort `(-score, id)`.
* Document limit: `O(N*d)` brute-force suitable to ~20k vectors; migrate to HNSW/FAISS beyond.

**5. Privacy State Machine:**
```python
Status = Literal["proposed","interest_sent","mutual_revealed"]
# proposed: only show counts + intersecting skill names, no contact
# mutual_revealed

---

## Section 4: Meta AI Client, Citation Auditor & Grant Synthesizer

# NEXUS — Section 4 Audit: Meta AI Client, Citation Auditor & Grant Synthesizer

**Scope:** `meta_client.py` | `citation_auditor.py` | `synthesizer.py` | `sam_segmenter.py`
**Lens:** Frontier reasoning token handling, claim grounding, hallucination mitigation, scientific figure segmentation

---

## 1. Executive Assessment (Rating: Needs Refactor)

**Rating: Needs Refactor — Demo-Ready, Not Production-Ready for Autonomous Grant Submission.**

The module boundaries are correct and demo-compelling: isolated transport client, explicit auditor, prompt-grounded synthesizer, and typed visual evidence carrier for SAM → Muse reasoning. That is the right architecture for Nexus.

However, the trust-critical path is currently simulated, not enforced. `CitationAuditor` cannot detect hallucinations or contradictions, `ProposalSynthesizer` does not close the loop with the auditor, `MetaMuseClient` drops reasoning-token signals, and `ScientificFigureSegmenter` injects hardcoded metrics (`0.942 F1`, `epsilon=0.5`) as if they were extracted facts. For an NSF/NIH narrative generator, that combination is a scientific-integrity blocker.

Ship for hackathon demo with guardrails and disclaimers. Do not wire to autonomous submission without refactor below.

## 2. Architectural Strengths & Invariants Verification

**What is done well:**

*   **Clean modularity:** Transport (`meta_client`) / verification (`citation_auditor`) / generation (`synthesizer`) / vision (`sam_segmenter`) are decoupled. Easy to test and replace.
*   **Typed visual contract:** `SegmentedFigure` as Pydantic `BaseModel` with normalized `polygon_points [0,1]`, `chart_type`, `confidence`, `extracted_data_series` is production-grade thinking. `format_visual_evidence_for_muse()` correctly serializes vision into structured prompt blocks.
*   **Low-temperature default:** `temperature=0.2` for aims drafting is correct for factual grounding.
*   **Reasoning-awareness:** `effective_tokens = max(max_tokens, 1500)` shows correct intuition that Muse Wonder 1.0 / Muse Spark 1.3 consume reasoning + generation budget jointly.
*   **Evidence-in-prompt pattern:** Injecting `exact_quote` with `title (year)` prefix in `synthesize_aims` is the right direction for grounded generation.

**Invariants check:**

| Invariant | Status |
| :--- | :--- |
| Reasoning tokens do not starve completion tokens | **PARTIAL** — floor of 1500 helps, but no separation of `reasoning` vs `output` budget, no `finish_reason==length` handling, no `usage.reasoning_tokens` surfacing |
| Every generated claim is traceable to `GroundingSource` | **FAILED** — prompt requests citations, but no programmatic enforcement or post-audit |
| Auditor rejects unsupported / contradictory claims | **FAILED** — `contradictions_found` hardcoded `0`, single-word overlap yields `supported` |
| Visual metrics fed to Muse are measured, with calibrated confidence | **FAILED** — metrics and polygons are canned constants, confidence `0.965/0.982` uncalibrated |
| Secrets / external I/O fail safely | **PARTIAL** — missing key raises fast, but no retry, no HTTP error parsing, no SSRF guard on `base_url` |

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### A. Meta Muse Frontier Reasoning Token Handling — `meta_client.py`

1.  **[High] Reasoning content silently discarded:** `choice["message"].get("content") or ""` assumes non-reasoning schema. Frontier reasoning models return `reasoning_content` / `reasoning_tokens` + `content`. Current code will return `""` on thinking-only truncation with no signal, which `synthesizer` will then treat as valid narrative.
2.  **[High] No truncation detection:** No check for `finish_reason in ("length", "max_tokens", "content_filter")`. A cut-off Aims section will be returned as complete.
3.  **[Medium] `effective_tokens` conflates budgets:** `max(max_tokens,1500)` raises floor but doesn't cap or split. A `max_tokens=2000` call to `muse-spark-1.3` may spend 1800 on reasoning, leaving 200 for narrative. Need explicit `max_completion_tokens` + `reasoning_effort` / `max_reasoning_tokens` passthrough and surface `usage`.
4.  **[Medium] Brittle transport:** Bare `urllib.request.urlopen` with no `HTTPError/URLError/Timeout/JSONDecode/KeyError` handling, no retries on 429/5xx, no timeout jitter. Single transient failure kills synthesis. `base_url` is fully injectable — SSRF risk if configured from proposal metadata.
5.  **[Low] No allowlist / bounds:** `model` string free-form, `temperature` unbounded, no `stop` / `response_format=json` option for structured aims.

### B. Claim Grounding Verification — `citation_auditor.py`

1.  **[Critical] Lexical overlap != grounding:** `any(term in abstract for term in claim.split() if len>5)` will match `protein`, `method`, `analysis` and score `75+15=90 → supported`. False-positive rate will be ~100% in demo. Paraphrased true claims with synonyms will false-negative.
2.  **[Critical] Contradiction detection stubbed:** `"contradictions_found": 0` always. System cannot catch negated findings — fatal for grant integrity.
3.  **[High] Null-unsafe:** If `s.abstract` or `s.exact_quote` is `None`, `.lower()` throws `AttributeError`, crashing batch audit.
4.  **[High] Uncalibrated scoring:** `min(98, 75+n*15)` / `40` are magic numbers with no precision/recall validation, no per-claim span offsets, no source IDs returned beyond title (collision-prone).

### C. Hallucination Mitigation — `synthesizer.py`

1.  **[Critical] Open-loop generation:** Prompt says `MUST reference grounding sources` but result is never passed through `CitationAuditor`. Hallucinated citations will ship.
2.  **[High] Silent evidence truncation:** `sources[:4]` with no ranking, relevance scoring, or overflow handling. If `sources==[]`, prompt contains empty `GROUNDING EVIDENCE:` yet still asks for Technical Narrative — guarantees fabrication.
3.  **[Medium] Prompt injection / overflow:** `proposal.title` and `exact_quote` interpolated raw. No length cap, no delimiter escaping (`"""` break-out), no agency template branching (NSF Intellectual Merit/Broader Impacts vs NIH Significance/Innovation/Approach).
4.  **[Medium] Token accounting loss:** `result["usage"].get("total_tokens",0)` discards `prompt/completion/reasoning` split needed for cost and reasoning-starvation debugging.

### D. SAM Scientific Figure Segmentation — `sam_segmenter.py`

1.  **[Critical] Mock data presented as measurement:** Hardcoded `nexus_aligned_score: 0.942`, `epsilon: 0.5, delta: 1e-5`, `polygon_points=[[0.12,0.25]...]` on keyword match (`"eeg" in page_text`). If this flows into a grant narrative, Nexus fabricates experimental results. Must be flagged `is_synthetic=True` / `mock` in demo.
2.  **[High] Keyword detector, not SAM:** `if "figure 4" in text` cannot localize, cannot handle multi-figure pages, rotated scans, two-column layouts, log-scales, error bars. No IoU, no NMS, no DPI-to-normalized coordinate transform validation.
3.  **[Medium] Untyped metrics + overconfidence:** `extracted_data_series: Dict[str,Any]` allows any hallucinated float through. Fixed `confidence=0.965/0.982` with no calibration will mislead Muse reasoning (`Extraction Confidence: 96.5%`).
4.  **[Low] Schema looseness:** `chart_type: str` should be `Literal["line_plot","ROC_curve","scatter_cohort","block_diagram"]`; `page_number` needs `ge=1`; `paper_doi` needs pattern validation.

## 4. Concrete Recommendations for Hackathon Demo & Hardening

**For demo (keep wow, remove risk) — 2-hour fixes:**

1.  **Label SAM as simulated + gate metrics:**
    ```python
    class SegmentedFigure(BaseModel):
      chart_type: Literal["line_plot","ROC_curve","scatter_cohort","block_diagram"]
      is_synthetic: bool = True
      confidence: float = Field(..., le=1.0, ge=0.0)
    ```
    Render banner in UI when `is_synthetic`: `Simulated SAM extraction — do not cite as data`. Never allow `extracted_data_series` numbers into final narrative without `auditor` match.

2.  **Close the loop in `synthesizer` (minimal hallucination guard):**
    ```python
    result = self.client.complete(prompt, model="muse-spark-1.3", max_tokens=2000)
    # split narrative into sentences -> audit each -> reject if needs_evidence
    audits = [auditor.audit_claim(s, sources) for s in split_sentences(result["text"])]
    if any(a["status"]=="needs_evidence" for a in audits):
        result["text"] += "\n\n[UNVERIFIED CLAIMS FLAGGED — REQUIRES PI REVIEW]"
    ```
    Demo narrative: show green/yellow grounding badges per aim.

3.  **Harden `MetaMuseClient.complete` for live demo resilience:**
    *   Catch `HTTPError/URLError/Timeout/JSONDecode/KeyError`, return `{"text":"", "error":..., "retryable":bool}`.
    *   Add 3x exponential backoff on 429/500/503, `timeout=60` with jitter.
    *   Propagate full usage: `{"prompt_tokens":..., "reasoning_tokens":..., "completion_tokens":...}` + `finish_reason`. If `finish_reason=="length"`, auto-retry with `effective_tokens+1000` once and surface warning.
    *   Allowlist models: `{"muse-wonder-1.0","muse-spark-1.3"}`.

**For production hardening (post-hackathon):**

4.  **Replace lexical auditor with two-stage verifier:** Stage 1: embedding retrieval (`cosine >0.72`) for candidate `GroundingSource` ranking. Stage 2: NLI entailment model (`entails / neutral / contradicts`) per claim-source pair. Return span offsets, `source_id` (not title), calibrated score, and real `contradictions_found` with conflicting quotes.

5.  **Enforce structured citations in generation:** Use JSON mode / constrained decoding: `{"aims":[{"text":"...","citations":["src_id..."]}]}`. Reject any sentence without `source_id` that resolves to provided `exact_quote`. Add contradiction prompt + self-check pass with Wonder 1.0.

6.  **Real SAM integration:** Replace keyword stub with SAM inference service returning masks → polygon simplification (Ramer-Douglas-Peucker) → normalized coords + chart-type classifier + axes OCR (e.g., DePlot/MatCha) with uncertainty. Store `mask_iou`, `ocr_confidence` separately; fuse into calibrated `confidence`. Persist `figure_id, doi, page, polygon, raw_crop_hash` for reproducibility audit.

7.  **Security / ops:** Validate `base_url` against allowlist, pin TLS, redact `api_key` from exceptions, add request ID logging, add Pydantic validation on `GrantProposal.target_agency` to select NSF vs NIH template, cap prompt to model context (truncate `exact_quote` to top-k tokens).

With those changes, Section 4 moves from compelling prototype to defensible autonomous science infrastructure: reasoning-aware, contradiction-aware, and visually grounded.


---

## Section 5: Solicitations Finder, Compliance & 5-Stage Pursuit Tracker

# Nexus — Section 5 Audit: Solicitations Finder, Compliance & 5-Stage Pursuit Tracker

**Scope:** `packages/funding/src/nexus_funding/finder.py`, `tracker.py`, `compliance.py`
**Lens:** Federal solicitation matching (NSF, NIH, DARPA) + Flightpath 5-stage readiness + pre-flight compliance validation

---

## 1. Executive Assessment (Rating: Needs Refactor)

**Rating: Needs Refactor — Demo-Capable, Not Submission-Safe.**

The Section 5 slice is well-structured for a hackathon demo: clean Pydantic models, clear separation of `Finder / Tracker / Compliance`, and deterministic in-memory data that will render reliably on stage. It is **not** production-ready for federal grant pursuit.

Three blocking defects prevent production sign-off:

1.  **Compliance false-positives:** `audit_proposal()` only enforces 3 of 8 declared rules. Unimplemented rules auto-pass as `"Satisfied"`.
2.  **Agency routing bug:** DARPA (and any non-NSF agency) silently falls through to `NIH_RULES`.
3.  **Shared mutable rule state + hardcoded readiness:** Class-level `NSF_RULES / NIH_RULES` lists are mutable singletons, and `PursuitTracker.create_tracker()` hardcodes `readiness_score=78` with no derivation from task evidence.

Fixing these is ~1 focused sprint. No architectural rewrite required.

---

## 2. Architectural Strengths & Invariants Verification

**What is done well:**

*   **Typed domain models:** `FundingOpportunity`, `PursuitState`, `ComplianceRule`, `ComplianceReport` use Pydantic `BaseModel`. This gives free validation, serialization for APIs/UI, and prevents ad-hoc dict passing.
*   **Separation of concerns:** Discovery (`FundingFinder`), state machine (`PursuitTracker`), policy (`SolicitationComplianceChecker`) are correctly decoupled. This matches Nexus federated design and allows independent testing / replacement with live Grants.gov / SAM.gov adapters.
*   **Deterministic demo data:** Three canonical opportunities (NSF 24-529, NIH PA-24-102, DARPA-RA-24-03) cover distinct agencies, ceilings ($275k / $500k / $1.2M), and focus areas. Good for matching narrative.
*   **Explicit 5-stage Flightpath model:** `MILESTONES` length 5 is consistently enforced in `MilestoneStatus.index`, `current_milestone_index`, and `advance_milestone()` bounds check `curr < len-1`. State machine cannot index-out-of-range.
*   **Compliance report contract is UI-ready:** `overall_compliance_score`, `passed_rules/total_rules`, `ready_for_submission`, `findings[]`, `actionable_recommendations[]` is exactly what a pursuit dashboard needs.

**Invariants verified:**

| Invariant | Status |
| :--- | :--- |
| `list_all("ALL")` / `None` returns full index | ✅ Pass |
| `list_all(agency)` case-insensitive | ✅ Pass |
| `advance_milestone()` never exceeds `len(MILESTONES)-1` | ✅ Pass |
| `readiness_score` capped at 100 via `min(100, ...)` | ✅ Pass |
| `overall_compliance_score == int(passed/total*100)` | ✅ Pass |
| Agency-specific rules isolated per audit | ❌ Fail — DARPA routes to NIH |
| Unchecked rules do not auto-pass | ❌ Fail — 5 rules are no-ops |
| Tracker state immutable / auditable | ❌ Fail — in-place mutation, no history |

---

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### A. `finder.py` — Matching is Keyword Substring, Not Solicitation Matching

1.  **No relevance ranking:** `search()` returns unordered filter on `title / agency / focus_areas`. No scoring, no sorting by `days_remaining` or `award_ceiling`. Query `"systems"` will match DARPA but miss NSF SCC description containing `"cyber-physical systems"` because `description`, `solicitation_number`, and `eligibility` are not searched.
2.  **Static temporal fields:** `deadline: str` + `days_remaining: int` are hardcoded (34/24/72). They will drift and contradict each other after one day. No `date` type, no timezone, no validation that `days_remaining >= 0`. Expired solicitations never filter out.
3.  **Fragile input handling:** `search(query: str)` will throw `AttributeError` on `None`. `q in ...` with `q=""` returns all records — acceptable for demo but should be explicit. `agency_filter.upper()` assumes `str`.
4.  **Weak typing:** `agency: str` allows `"nsf "`, `"N.S.F."`, typos. Should be `Literal["NSF","NIH","DARPA"]` or `Enum`.
5.  **No eligibility / fit logic:** No method like `match(profile_keywords, institution_type)` to check `eligibility` vs. PI status. Cannot prevent e.g., non-tenure-track pursuing `opp-darpa-yfa`.

### B. `tracker.py` — Hardcoded Readiness, Unsafe Transition

1.  **Fabricated progress:** `create_tracker()` always yields `completed=(i<2)`, `current=(i==2)`, `tasks_done=4 if i<2 else 2`, `readiness_score=78`. Not derived from evidence. Every proposal shows identical Flightpath. Demo risk: judges will create two trackers and see identical scores.
2.  **In-place mutation:** `advance_milestone(state: PursuitState) -> PursuitState` mutates input and returns same reference. Callers holding old reference see silent change. No copy, no event log, no timestamp — breaks auditability required for federal submissions.
3.  **No completion guard:** Advancement does not verify `tasks_done == total_tasks` for current milestone. User can advance with 2/5 tasks done. Old milestone is marked `completed=True` unconditionally.
4.  **Terminal state dead-end:** When `curr == 4`, function silently no-ops, never sets `readiness_score=100` or `completed=True` for final milestone. No `is_complete` property.
5.  **No validators:** `tasks_done > total_tasks` possible, `current_milestone_index` can desync from `milestones[i].current` if caller mutates manually. No `model_validator` to enforce single `current==True`.
6.  **Linear +10 scoring:** `readiness_score +10` is arbitrary, not weighted by milestone difficulty (e.g., Peer review > Literature discovery). No provenance.

### C. `compliance.py` — Critical Logic Gaps

1.  **DARPA misrouting (P0):**
    ```python
    rules = self.NSF_RULES if agency_upper == "NSF" else self.NIH_RULES
    ```
    Any `agency="DARPA"` gets NIH aims/strategy rules. Must have explicit registry + `raise ValueError` for unknown.
2.  **Shared mutable class state (P0):** `NSF_RULES` / `NIH_RULES` are class-level `list[ComplianceRule]` of mutable Pydantic objects. If any future code sets `r.checked=True`, it persists across requests/workers. Must use `deepcopy` or factory method.
3.  **5/8 rules are no-ops (P0):** Only `nsf-sec-bi`, `nsf-page-limit`, `nih-aims-limit` have `if` branches. `nsf-dmp`, `nsf-citations`, `nih-strategy-limit`, `nih-rigor`, `nih-auth` always append `passed=True, detail="Satisfied"`. This produces dangerously inflated `overall_compliance_score`.
4.  **Trivial check bypass:** `if "broader impacts" not in text` is easily gamed by mentioning the phrase once in any section. Does not verify separate labeled subsection in Project Description as requirement states. Similarly, `len(aims_text.split()) > 750` is a crude proxy for 1-page limit, ignores formatting, figures, references.
5.  **Scoring ignores `mandatory`:** `nih-auth (mandatory=False)` carries same weight as mandatory rules. `ready_for_submission=(score>=90)` with `total_rules=4` means only `4/4=100` passes — effectively `==100`. Brittle; one optional failure blocks submission if weighting is fixed.
6.  **No input hardening:** `sections: Dict[str,str]` joined via `" ".join(sections.values())` assumes all values are `str`. `None` or large payloads (full PDF text) cause crash or CPU spike. No max-length, no normalization, no PDF/section-name canonicalization.
7.  **Security / audit perspective:** No hash of audited artifact, no version pin of rule set, no timestamp. Applicant could alter proposal post-audit and retain `ready_for_submission=True` report. For Nexus, compliance reports must be content-addressed.

---

## 4. Concrete Recommendations for Hackathon Demo & Hardening

### A. Demo-Safe Fixes (implement before stage, <2 hours)

**1. Fix agency routing + add DARPA stub explicitly:**
```python
def _rules_for(self, agency_upper: str) -> list[ComplianceRule]:
    import copy
    if agency_upper == "NSF":
        return copy.deepcopy(self.NSF_RULES)
    if agency_upper == "NIH":
        return copy.deepcopy(self.NIH_RULES)
    if agency_upper == "DARPA":
        return copy.deepcopy(self.DARPA_RULES)  # add 3-4 YFA rules
    raise ValueError(f"Unsupported agency: {agency_upper}")
```
Add `DARPA_RULES = [page-limit 8pp, quad-chart required, OCI disclosure, ...]` to unblock YFA narrative.

**2. Make unimplemented rules explicit fail-closed:**
For any rule without checker, emit `passed=False, detail="Checker not implemented — manual review required"` instead of `"Satisfied"`. Prevents false green on demo compliance screen and shows honesty to judges.

**3. Derive tracker from inputs:**
```python
def create_tracker(self, proposal_id: str, opportunity_title: str, tasks_done_per_milestone: list[int] | None = None) -> PursuitState:
```
Compute `readiness_score = int(100 * sum(done)/sum(total))`. This lets demo show 42% vs 78% vs 95% live when advancing.

**4. Harden `advance_milestone`:**
- `return state.model_copy(deep=True)` instead of mutating.
- Require `state.milestones[curr].tasks_done == total_tasks` else raise `MilestoneIncompleteError`.
- On terminal milestone, set `completed=True, current=False, readiness_score=100`.
- Append to `history: list[MilestoneEvent]` with timestamp.

### B. Production Hardening (post-hackathon roadmap)

1.  **Finder:** Migrate `deadline: date`, add `@property days_remaining` computed from `date.today(UTC)`. Change `agency: AgencyEnum`. Implement `score_match(profile: ResearchProfile) -> float` using TF-IDF/embeddings over `title+description+focus_areas` + eligibility filter + deadline urgency decay. Add pagination, `sort_by="deadline"`, and Grants.gov API adapter behind `FundingSource` protocol.
2.  **Tracker:** Add Pydantic validators: `tasks_done <= total_tasks`, exactly one `current=True` unless complete. Persist `PursuitState` with content hash + append-only event log for cryptographic audit trail. Weight readiness: e.g., `[10,20,25,25,20]`.
3.  **Compliance:** Implement real checkers: regex for `(?m)^.*Broader Impacts` heading, page-count via PDF parser, citation density via DOI regex + Crossref validation, DMP attachment existence check. Weight score by `mandatory` (mandatory failure = `ready_for_submission=False` regardless of score). Include `artifact_sha256`, `ruleset_version`, `audited_at` in `ComplianceReport`.
4.  **Tests to add now:** `test_darpa_does_not_use_nih_rules`, `test_unimplemented_rule_does_not_pass`, `test_advance_does_not_mutate_input`, `test_empty_query`, `test_expired_deadline_filtered`, `test_readiness_derived`.

**Demo tip:** Seed one failing NSF proposal (missing Broader Impacts, 17 pages) and one passing NIH proposal. Show red→green transition after applying `actionable_recommendations`. Pair with Flightpath bar advancing 2→3→4. That visual closes the solicitation-to-submission story judges expect from Nexus.


---

## Section 6: FastAPI Gateway & Endpoints

# NEXUS Code Audit — Section 6: FastAPI Gateway & Endpoints

**Scope:** `services/api/src/nexus_api/main.py`, `services/worker/src/nexus_worker/models.py`
**Focus:** Router composition (`/vault`, `/discovery`, `/funding`, `/intelligence`), input validation, exception handling, async worker architecture

---

## 1. Executive Assessment (Rating: Needs Refactor)

**Verdict: Needs Refactor — Demo-Ready Scaffold, Not Production-Ready Gateway.**

The reviewed files provide a clean, correctly versioned FastAPI composition root and a sane Pydantic job envelope. For a hackathon demo this will boot and serve OpenAPI. For production as the federated trust boundary for Nexus, it is incomplete:

* No router implementations were provided for audit — `/vault`, `/discovery`, `/funding`, `/intelligence` logic, validation, and auth cannot be verified.
* `main.py` has one **P0 security misconfiguration** (CORS `*` + `allow_credentials=True`), one **P0 deployment anti-pattern** (`reload=True`), and zero global exception handling, auth, rate-limiting, or lifecycle management.
* `models.py` defines a correct status enum and timezone-aware timestamps, but as a worker contract it is under-constrained: `job_type: str` is open dispatch, timestamps are `str` not `datetime`, and there is no state-machine guard, idempotency, priority, retry, or cancellation semantics.

> Ship as-is for Day-1 demo with CORS + reload fixes below. Do not expose to untrusted campus networks without P0 hardening.

---

## 2. Architectural Strengths & Invariants Verification

**What is right and should be preserved:**

* **Modular composition root:** `app.include_router(..., prefix="/api/v1/...")` with per-domain tags is correct. Enforces API versioning, isolates Vault (sensitive) from Discovery/Funding/Intelligence, allows independent rate-limit / auth policies per router.
* **Versioned namespacing:** `/api/v1/vault`, `/discovery`, `/funding`, `/intelligence` + `/health` separation is correct. Health is unversioned, as expected for LB probes.
* **Declarative metadata:** `title`, `version="1.0.0"`, `description` propagates to OpenAPI — good for federated client generation.
* **Worker envelope discipline:**
  * `JobStatus(str, Enum)` — JSON-serializable, prevents `QUEUED` vs `"queued"` drift. Correct.
  * `payload: Dict[str, Any] = Field(default_factory=dict)` — avoids mutable default bug.
  * `created_at_utc` uses `datetime.now(timezone.utc)` — UTC-aware by default. Correct invariant for federated ordering.
  * `Optional[result/error/started/finished]` cleanly models queued -> running -> terminal lifecycle.

**Invariants verified:**
* [PASS] No mutable defaults, no naive datetime creation.
* [PASS] No blocking imports in `main.py`, router composition has no circular dependency risk if `routes/__init__.py` re-exports.
* [FAIL] `pep_enforcement: active` and `lattice_version: v1.0` in health response are hardcoded strings, not verified from policy engine / config. False-positive invariant.

---

## 3. Potential Edge Cases, Logic Gaps, or Vulnerabilities

### A. Gateway (`main.py`) — P0/P1

**P0-1 CORS Credential Leak:**
```python
allow_origins=["*"], allow_credentials=True
```
Browsers reject this combo, Starlette will reflect `*` in some configs. If fixed naively to reflect origin, any site can make credentialed cross-origin calls to Vault. For a hypothesis vault, this is data exfiltration vector.

**P0-2 `reload=True` in entrypoint:**
`uvicorn.run(..., reload=True)` enables file-watcher + auto-reload. In container/prod: 2x memory, restarts on spurious writes, exposes reloader as code-exec surface. Must be `False` / controlled via env.

**P0-3 No AuthN/Z, No TrustedHost, Docs Exposed:**
No `HTTPBearer/JWT`, no `TrustedHostMiddleware`, no dependency for `get_current_user`. All four routers inherit zero protection. `/docs`, `/redoc`, `/openapi.json` are public by default — Vault schemas leak.

**P1-1 No Global Exception Handling:**
No `@app.exception_handler(RequestValidationError|StarletteHTTPException|500)`. Default FastAPI 500 returns stack-adjacent JSON in debug, inconsistent error envelope for federated clients. No `request_id` correlation.

**P1-2 Shallow Health Check:**
```python
def health_check(): return {"status": "healthy", ...}
```
Sync def, no dependency checks (Postgres, Redis queue, object store, worker lag). Load balancer will route to API with dead DB. Also `def` vs `async def` blocks event loop if later extended with IO.

**P1-3 No Lifespan / Graceful Shutdown:**
No `lifespan=` for pool creation/disposal (asyncpg, Redis, httpx). Worker queue connections will leak on SIGTERM, in-flight `synthesize_proposal` jobs lost.

**P1-4 Missing Hardening Middleware:**
No `GZipMiddleware` cap, no `RequestTimeout`, no body-size limit, no rate-limit (slowloris / embedding-index DoS on `/discovery`), no `Server` header stripping.

### B. Worker Contract (`models.py`) — P1/P2

**P1-5 Open Job Dispatch:**
```python
job_type: str  # synthesize_proposal, audit_citations, index_campus_graph
```
Free-form string. If worker does `getattr(handlers, job_type)` or `eval`, this is remote job injection. No allowlist, no versioning (`synthesize_proposal.v2` breaks silently).

**P1-6 Timestamps as `str`:**
`created_at_utc: str`, `started_at_utc: Optional[str]`. Loses ordering, filtering, TTL validation. Accepts `"tomorrow"`, `"2020-13-99"`. No deserialization guard, sorting becomes lexicographic bug when offsets differ (`+00:00` vs `Z`).

**P1-7 No State-Transition Guard:**
Any transition allowed: `COMPLETED -> QUEUED`, `FAILED -> COMPLETED` without `started_at`. No `updated_at_utc`, `progress: 0.0-1.0`, `retry_count/max_retries`, `priority`, `idempotency_key`, `ttl`. Results in duplicate `synthesize_proposal` billing, lost retries, unbounded `result` growth (Redis OOM via large `Dict[str, Any]` payload).

**P2-1 Identity / Tenancy Gap:**
`job_id: str`, `user_id: str` with no `Field(min_length, pattern)`, no UUID validation. Polling endpoint `GET /jobs/{job_id}` without scoping `user_id == token.sub` enables horizontal job-result harvesting across tenants — critical for Vault confidentiality.

**P2-2 Visibility Gap:**
No worker implementation audited. Cannot verify async architecture: queue backend, ack/nack, DLQ, cancellation (`CANCELLED` has no handler), idempotent re-queue on crash.

---

## 4. Concrete Recommendations for Hackathon Demo & Hardening

### P0 — Fix Before Any Public Demo (15 min)

**1. Lock CORS + production entrypoint:**
```python
from fastapi import FastAPI
from fastapi.middleware.trustedhost import TrustedHostMiddleware
import os

ALLOWED_ORIGINS = os.getenv("NEXUS_CORS_ORIGINS", "http://localhost:3000").split(",")

app = FastAPI(title="Nexus Scientific Research & Grant Intelligence API", version="1.0.0")

# Replace allow_origins=["*"]
# app.add_middleware(CORSMiddleware, allow_origins=ALLOWED_ORIGINS, allow_credentials=True, allow_methods=["GET","POST"], allow_headers=["Authorization","Content-Type","X-Request-ID"])
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["api.nexus.local", "localhost"])

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("nexus_api.main:app", host="0.0.0.0", port=8000, reload=False, workers=2)
```

**2. Standardize error envelope + health:**
```python
from fastapi.responses import JSONResponse
from fastapi.requests import Request
from fastapi.exceptions import RequestValidationError
import uuid, time

@app.middleware("http")
async def add_request_id(request: Request, call_next):
    rid = request.headers.get("X-Request-ID", str(uuid.uuid4()))
    start = time.perf_counter()
    resp = await call_next(request)
    resp.headers["X-Request-ID"] = rid
    resp.headers["X-Process-Time"] = str(time.perf_counter() - start)
    return resp

@app.exception_handler(RequestValidationError)
async def validation_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"error": "validation_failed", "request_id": request.headers.get("X-Request-ID"), "details": exc.errors()})

@app.get("/health", tags=["Ops"])
async def health_check():
    return {"status": "healthy", "service": "nexus-api", "version": app.version}

@app.get("/ready", tags=["Ops"])
async def readiness(redis=Depends(get_redis), db=Depends(get_db)):
    # ping redis, SELECT 1 on db, check queue depth; return 503 if degraded
    ...
```

### P1 — Harden Worker Contract (Demo-safe, Production-correct)

Replace `models.py` with constrained contract:
```python
from enum import Enum
from typing import Dict, Any, Optional, Literal
from datetime import datetime
from pydantic import BaseModel, Field, AwareDatetime
import uuid

class JobType(str, Enum):
    SYNTHESIZE_PROPOSAL = "synthesize_proposal"
    AUDIT_CITATIONS = "audit_citations"
    INDEX_CAMPUS_GRAPH = "index_campus_graph"

class JobStatus(str, Enum):
    QUEUED = "queued"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

_ALLOWED_TRANSITIONS = {
    JobStatus.QUEUED: {JobStatus.RUNNING, JobStatus.CANCELLED},
    JobStatus.RUNNING: {JobStatus.COMPLETED, JobStatus.FAILED, JobStatus.CANCELLED},
    JobStatus.COMPLETED: set(), JobStatus.FAILED: set(), JobStatus.CANCELLED: set(),
}

class BackgroundJob(BaseModel):
    job_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    user_id: str = Field(min_length=1, max_length=128)
    job_type: JobType
    payload: Dict[str, Any] = Field(default_factory=dict, max_length=200)
    status: JobStatus = JobStatus.QUEUED
    priority: int = Field(default=5, ge=0, le=9)
    retry_count: int = Field(default=0, ge=0)
    max_retries: int = Field(default=3, ge=0, le=10)
    idempotency_key: Optional[str] = Field(default=None, max_length=128)
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = Field(default=None, max_length=2000)
    created_at_utc: AwareDatetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    started_at_utc: Optional[AwareDatetime] = None
    finished_at_utc: Optional[AwareDatetime] = None

    def transition(self, to: JobStatus):
        if to not in _ALLOWED_TRANSITIONS[self.status]:
            raise ValueError(f"illegal {self.status} -> {to}")
        self.status = to
```

**Router skeleton to enforce per-domain auth + validation (add for each router):**
```python
# routes/vault.py
from fastapi import APIRouter, Depends, HTTPException
vault_router = APIRouter()

@vault_router.post("/commit", status_code=202)
async def commit_hypothesis(body: VaultCommitRequest, user=Depends(require_auth), q=Depends(get_queue)):
    try:
        job = BackgroundJob(user

---

