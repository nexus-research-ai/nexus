# Meta AI Advisory: Anti-Scooping Privacy & The Winning Campus Pitch

- **Evaluator Model:** `muse-wonder-1.0`
- **Token Usage:** {"completion_tokens": 5424, "prompt_tokens": 173, "total_tokens": 5597, "completion_tokens_details": {"reasoning_tokens": 3454}, "prompt_tokens_details": {"cached_tokens": 0}}

As Chief Strategist, here's my critical advice: **Your Privacy UX is not a feature. It's your supply engine.**

Without trust, no student posts an unpublished idea. Without unpublished ideas, you have no Living Campus Graph. Without that graph, you're just LinkedIn for labs.

You have to sell safety in the product *and* in the pitch, in this exact order: **Seal -> Tease -> Reveal.**

### 1. ANTI-SCOOPING & PRIVACY UX

Design for paranoia. A PhD student thinks everyone will steal their idea. Make the default paranoid.

#### The 3 Tiers - Field by Field

Don't give them a Public/Private toggle. Give them 3 named modes with clear human promises:

**1. VAULT - "Only you. Not even we can read it."**
Default for a raw hypothesis.
Visible to others: *Nothing.* Not title, not name, not department.
Visible to Nexus server: *Only a hash.*
What it does: Proof of Priority + optional Ghost Matching.
UX Copy: `Sealed locally on your device. If our servers were hacked tomorrow, attackers get useless numbers.`

**2. TEASER - "They see the shape, not the secret."**
This should be your DEFAULT recommended mode. This is where matching happens.
Visible: Verified level + broad field only - e.g. "Verified MSCS '27, Computational Biology" - NO name, NO lab, NO PI.
Visible: Abstracted NEEDS and OFFERS only.
Hidden & Sealed: Exact hypothesis, method, target protein/gene/dataset, results.

Example of your LLM Abstraction Engine - show this side-by-side and let the user EDIT before posting. This human-in-the-loop moment creates 100% trust:

> **Your Raw (Sealed):** "Using diffusion models to predict misfolding of TDP-43 in ALS to find cryptic pockets"
> **Public Teaser (You Approve):** "Computational modeling of protein misfolding in neurodegenerative disease. OFFER: Diffusion models / ML pipelines. NEED: Wet-lab validation & protein assays."

Never embed the raw Vault text server-side. Only embed the approved abstracted Teaser, and embed it twice: one vector for `OFFER`, one for `NEED`. That's your Dual Embedding moat.

**3. PUBLIC - "Open science. Recruit the campus."**
Visible: Everything, name, lab, full abstract, looking-for list.
For projects already submitted, published, or recruiting hackathon teammates.

Add one killer UX control on every project page: **[ Preview As: Stranger | Professor | Match ]** toggle. When they see literally nothing sensitive as a Stranger, anxiety drops.

#### Cryptographic Proof of Priority: The Commit-Reveal Protocol

Implement this exactly with Web Crypto API - it's buildable in a hackathon and judges will get it instantly.

1.  **Local Hashing:** In the browser, generate a random 256-bit salt. Compute:
    `SHA-256( canonical_text + attachments_text + author_id + salt )`
    Show an animation of their text scrambling into: `9f86d081884c7d659a2feaa0c55ad015...` Judges need to *see* privacy.
    The salt prevents someone guessing their hypothesis and brute-forcing the hash.

2.  **Server Receipt:** Send ONLY the hash to Nexus. Server returns a signed receipt: `Sign_server( hash + timestamp )` with Ed25519.

3.  **Public Anchoring:** Once a day, take all hashes, build a Merkle Tree, anchor the Merkle Root to Base (cheap L2). For the demo, anchor live to Base Sepolia and show the Etherscan link.

4.  **The Certificate:** Success screen is not a toast. It's a downloadable certificate:
    ```
    NEXUS PROOF OF PRIORITY #NX-8492
    Sealed: May 9, 2026 - 14:32:07 UTC
    Fingerprint: 9f86d081...
    Anchored: Base Block #18473920
    Verify at: nexus.app/verify/8492
    ```
    Anyone can later verify: User reveals original text + salt -> recompute hash -> matches anchored hash from *before* the scooper's paper.

5.  **The Reveal Event:** Matching is double opt-in, like a blind date.
    Both click "Request Reveal" -> Both sign a 1-click Mutual Non-Disclosure log -> Names/labs unblur -> The revealed PDF is watermarked per-viewer with their ID + timestamp + canary fingerprint. If it leaks, you know who.
    Every view is in an audit log the owner can see.

Add this final safety net: **Scoop Alert.** When a new Public project is posted, if its embedding cosine >0.92 to an older Sealed Teaser and its timestamp is later, alert the original owner with an Evidence Packet (their certificate + similarity report). You just became their insurance policy.

Ghost Matching for Vault users: Let a Vault participate anonymously. They only get: "You have a 94% complementary match 0.4 miles away." Neither side learns anything until both upgrade to Teaser and reveal. Magic without risk.

### 2. THE WINNING 3-MINUTE PITCH SCRIPT

Judges at Cerebral Valley will forget features. They will remember one student and one magic match. 450 words max. Memorize the first 15 seconds and last 15 seconds word-for-word.

**[0:00 - 0:25 | SLIDE: Dark campus map, all buildings dark]**
> "Universities spend a trillion dollars a year on research, yet nobody knows what anyone else is working on — until it's published, twelve months too late. Google Scholar indexes the past of a university. Nexus indexes its future."

**[0:25 - 0:55 | SLIDE: Photo of a student alone in library]**
> "This is Maya. She arrived last fall for her MSCS, obsessed with using AI for neurodegenerative disease. She had a hypothesis, and she needed one thing she didn't have: a wet lab to validate it. So she did what we all do. She read 200 papers. She cold-emailed 14 professors. She got zero replies. Three months later, at a poster session, she found a biology postdoc — two buildings away — who had been stuck for six months needing *exactly* her ML skills. They were perfect for each other. They were just invisible to each other."

**[0:55 - 1:10 | PAUSE]**
> "That's not a networking problem. That's a blind spot built into every campus. And students won't fix it by posting publicly, because they're terrified of getting scooped."

**[1:10 - 2:00 | LIVE DEMO - Do not use slides here]**
> "So Maya opens Nexus. First, she seals her raw hypothesis in her Vault."
> [CLICK Seal - show text scramble into hash live]
> "It's hashed locally, timestamped, and anchored. Not even we can read it, but she now owns mathematical proof she had it first. Now she posts a Teaser — just the shape. Her OFFER is diffusion models. Her NEED is wet-lab validation."
> [CLICK Find Matches]
> "In eight seconds, Nexus doesn't find people *similar* to Maya. It finds people *complementary* to her. This is our Dual Embedding Graph: we match my Need vector to your Offer vector. Top match: 96%. A verified Chemical Biology postdoc, 0.4 miles away. His Offer is protein assays. His Need is computational modeling. Double opt-in... [CLICK Reveal] ...and they meet. That collaboration started today, not next year."

**[2:00 - 2:35 | SLIDE: Graph lighting up building to building]**
> "Under the hood, we're building the Living Campus Graph — the first pre-publication graph of who knows what, who needs what, and who is working on what *right now*. Every Sealed idea, every Teaser, makes the graph smarter. This data set doesn't exist anywhere else. ResearchGate can't copy it, because they never earned the trust to collect it."

**[2:35 - 3:00 | SLIDE: One campus fully lit, then 4,000 campuses]**
> "Start with one campus. Expand to 4,000 universities. Sell departments the intelligence layer they've never had. We are not building LinkedIn for academia. We are building the nervous system for human discovery. Help us light up the first campus."

**Delivery Rules:**
1.  Seal BEFORE Match in the demo. Trust first, magic second.
2.  Have a 50-second recorded backup of the demo. Live demos die.
3.  If asked "Why will students post?" answer: "Because we don't ask them to post. We ask them to seal and insure an idea they already have, and matching is the free bonus."
4.  If asked "Why not similarity search?" answer: "Similar people compete. Complementary people collaborate. That's why we built two embeddings, not one."

Your closing line judges will repeat to each other: **Scholar indexes what was discovered 12 months ago. Nexus indexes what will be discovered 12 months from now.**

That's a $1M insight.