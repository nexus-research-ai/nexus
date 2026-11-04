# Meta AI (Muse Wonder 1.0) Architecture & Hackathon Review

- **Evaluator Model:** `muse-wonder-1.0` (Meta AI Frontier Reasoning)
- **Token Usage:** `{"completion_tokens": 2500, "prompt_tokens": 361, "total_tokens": 2861, "completion_tokens_details": {"reasoning_tokens": 2178}, "prompt_tokens_details": {"cached_tokens": 0}}`

Nexus is a Grand Prize contender *if* you make one shift in positioning: Don't sell it as "AI writes grants." Every team will claim that. Sell it as **"AI that can prove every claim it makes, back to the exact pixel in the source paper."**

That's what faculty, NSF/NIH reviewers, and Meta judges will trust. Here's how to get there:

### 1. Architectural Optimization: SAM 3.1 -> Muse Wonder 1.0

Don't feed Muse raw masks or full-page screenshots. You'll lose numbers, axes, and legends. Use this hybrid chain:

**a) Deterministic PDF layer first, SAM second**
Extract the native text layer, embedded images, and vector graphics with PyMuPDF/pdfplumber first. It's perfect and free. Use SAM 3.1 *only* for what PDFs can't give you: composite figures, scanned charts, architecture diagrams, and sub-figure separation.

This will 10x your speed on those 2,932 PDFs and judges will see you understand SAM's real strength.

**b) Prompt SAM like a scientist, not generically**
Run the SAM image encoder once per page at 300 DPI, then run cheap text-prompted decodes in parallel:
`"bar chart"`, `"line graph with log scale"`, `"ablation table"`, `"neural network block diagram"`, `"subfigure a"`

Then decompose: Figure 1 -> 1a, 1b, 1c as separate masks. Keep a mask overlay, cropped PNG bounding box, and the extracted numeric vector together in the evidence record for Muse Wonder verification.

### 2. Live Micro-Verification Flow

1. Researcher highlights a claim in the editor.
2. System fetches candidate passages from Chroma and vector indices.
3. Muse Wonder cross-checks the claim against both the text and visual figure bounding boxes.
4. Generates a signed citation proof with a visual anchor in the Evidence Board.
