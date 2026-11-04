# Meta AI Strategic Advisory: The Living Campus Graph & Serendipity Engine

- **Evaluator Model:** `muse-wonder-1.0` (Meta AI Frontier Reasoning)
- **Token Usage:** {"completion_tokens": 4500, "prompt_tokens": 464, "total_tokens": 4964, "completion_tokens_details": {"reasoning_tokens": 3306}, "prompt_tokens_details": {"cached_tokens": 0}}
- **Topic:** Campus Research Visibility, Student Project Ingestion & Serendipity Matchmaking

You are not building a directory. LinkedIn already won directories.

You are building the **pre-publication graph of a university** — what is being built *right now*, in dorms, classrooms, and labs, before it becomes a paper on Google Scholar. That graph doesn't exist anywhere. That's your moat.

Reframe for the judges: **Google Scholar knows what was published. LinkedIn knows what you did. Nexus knows what you're working on and what you need next.**

Here is how to build and pitch it.

### 1. The Living Campus Graph: Cleanest Architecture

Don't run 3 disconnected databases for a hackathon. Use Postgres as the source of truth, with vectors and graph edges inside it, and sync to a graph view for visualization.

**Stack for 48h:** Next.js + Supabase (Postgres + pgvector + Auth with .edu SSO) + Muse Wonder 1.0 for extraction/reasoning + React Force Graph / Neo4j Aura for the demo visual.

#### Core Principle: Zero Manual Data Fatigue

No student will fill out 40 tags. The rule is: **Ingest, AI Drafts, User Approves in 10 seconds.**

Connectors (build GitHub + PDF upload, mock the rest):
GitHub repo, arXiv / PDF preprint, Overleaf, Google Scholar, Notion, Canvas course project

Pipeline:
`Artifact Upload -> Parse Text -> Muse Wonder Extraction -> Entity Resolution -> Dual Embedding -> Graph Edge Creation -> Trigger Match Job`

#### Schema

```sql
users (
  id, edu_email, name, role, -- undergrad/ms/phd/professor
  department, lab_id,
  offers_embedding vector(1536), -- what I can provide
  needs_embedding vector(1536)   -- what I'm looking for
)

projects (
  id, owner_id, title,
  teaser TEXT, -- public, safe version
  vault TEXT,  -- private details, encrypted
  stage, -- idea, prototype, experiment, writing
  visibility, -- public / campus / match_only
  content_hash, -- SHA256 for priority proof
  created_at
)

artifacts (
  id, project_id, type, -- paper/repo/dataset/code
  source_url, raw_text, hash, embedding vector(1536)
)

concepts ( id, name, canonical_embedding vector(1536) ) -- e.g. Pose Estimation, Low-Resource NLP

project_concepts (
  project_id, concept_id,
  role, -- USES / OFFERS / NEEDS
  confidence FLOAT
)

graph_edges (
  source_id, source_type, target_id, target_type,
  relation, -- WORKS_ON, NEEDS, OFFERS, COMPLEMENTS, AUTHORED
  weight, provenance_artifact_id, created_by_ai BOOLEAN
)
```

The graph view is just nodes from `users/projects/concepts/labs` and edges from `graph_edges`. You get Neo4j-style traversal without Neo4j ops pain.

#### The Key Innovation: Dual Embeddings

Don't embed just the project. Embed two things separately:

1.  **Offer Vector:** Skills, data, methods, equipment I *have*
2.  **Need Vector:** Skills, data, methods, collaborators I *lack*

Muse Wonder extraction prompt returns this as JSON:

```json
{
  "topics": ["sign language translation"],
  "methods_used": ["MediaPipe", "transformers"],
  "offers": ["collected 10hrs ASL video dataset", "native ASL interviews"],
  "needs": ["real-time pose estimation model", "edge deployment help"],
  "stage": "prototype",
  "teaser": "Building a glove-free ASL translator. Looking for ML help on pose tracking."
}
```

Then canonicalize concepts: search `concepts` by vector >0.92 similarity = merge, else create new. This is how the graph grows cleanly without 500 versions of "LLM / LLMs / Large Language Models."

Every new ingestion doesn't just add a profile. It adds nodes and edges for everyone else.

### 2. High-Precision Serendipity via Muse Wonder 1.0

Keyword matching creates spam and echo chambers. Two identical NLP projects don't need each other — they compete. Complementary projects create 1+1=3.

Use a 2-stage system:

**Stage 1: Recall (Cheap, Fast)**
Find candidates not by `cosine(ProjectA, ProjectB)`, but by asymmetric complementarity:

`Score = cosine(Need_A, Offer_B) + cosine(Need_B, Offer_A) + 2-hop graph proximity`

Pull top 30 candidates from pgvector + graph traversal.

**Stage 2: Precision (Muse Wonder CoT Reranker)**
This is where you win. Muse reasons, it doesn't just score.

Give it both teasers, offers/needs, stage, department, and ask it to evaluate:

1.  **Topical Adjacency:** Close enough to understand each other, not identical?
2.  **Complementarity:** Does A fill a *specific* gap in B and vice-versa?
3.  **Reciprocity:** Is this mutual, or one-sided begging?
4.  **Feasibility:** Same stage/timeline? Undergrad + Prof lab fit?
5.  **Redundancy Risk:** Are they direct competitors / scooping risk?

Output only if it can write the bridge:

```json
{
  "overall": 88,
  "complementarity": 94,
  "redundancy_risk": 12,
  "should_notify": true,
  "bridge_sentence": "Maya has the ASL dataset and user access Arjun's pose model lacks, and Arjun provides the real-time neural pose tracking architecture Maya requires for clinical validation."
}
```