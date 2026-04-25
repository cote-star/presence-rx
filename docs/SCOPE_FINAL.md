# Presence Rx — Final Scope

**Locked:** 2026-04-25 (renamed from "Proof of Presence" per D-014, late afternoon)
**Brand:** Nothing Phone  
**Concept:** The Invisible Champion  
**Primary tagline:** Diagnose. Prescribe. Refuse.
**Sub-tagline:** Find your brand's blind spots in AI answers.  
**Deliverable:** Presence Verdict Pack  

---

## Scope Philosophy

The existing Peec data is the **diagnosis** (50 prompts, 5 topics, 10 brands, 3 engines, US market).  
Our pipeline adds the **analysis** (guardrails, evidence chain, blocked claims).  
Our MCP writes add the **prescription** (new prompts, topics, tags, geos to close the gaps).

The demo shows the full loop: blind spot found → evidence graded → action recommended → monitoring created.

---

## Real Data We Have (Verified via MCP)

### Brand Visibility
| Metric | Value |
|--------|-------|
| Overall visibility | 20% (147 of 729 chats) |
| Overall position | 2.4 (#1 when mentioned) |
| Overall SoV | 8% |
| Overall sentiment | 64 |
| Brands tracked | 10 (Nothing Phone + 9 competitors). Note: Pixel and Google are separate Peec entries even though Pixel is a Google sub-brand — narrate Pixel as Google's hardware line to avoid double-counting in the demo. |

### Topic Breakdown
| Topic | Visibility | SoV | Position | Verdict |
|-------|-----------|-----|----------|---------|
| Smartphone Design | 72% | 85% | 1.9 | STRONGHOLD |
| Mobile Ecosystem | 12% | 7% | 3.8 | Blind spot |
| Consumer Tech Innovation | 10% | 5% | 3.7 | Blind spot |
| Minimalist Hardware | 6% | 2% | 4.1 | IRONIC GAP |
| Wireless Audio | 1% | 0% | 2.0 | INVISIBLE |

### Engine Breakdown
| Engine | Visibility | SoV | Position | Sentiment |
|--------|-----------|-----|----------|-----------|
| Gemini | 26% | 36% | 2.5 | 56 |
| ChatGPT | 18% | 39% | 2.5 | 66 |
| Google AI Overview | 17% | 25% | 2.1 | 71 |

### Channel Profile
| Channel Type | Top Domains | Nothing Phone Present? |
|---|---|---|
| UGC | YouTube (522), Reddit (313), Medium (144) | Yes — community strength |
| Editorial | rtings (89), pcmag (83), techradar (78) | Mixed — major gaps |
| Reference | Wikipedia (63) | Yes |
| Own | nothing.community (64, citation rate 1.21) | Yes — high authority |

### Gap Domains (competitors cited, Nothing Phone absent)
rtings.com, whathifi.com, samsung.com, zdnet.com, wallpaper.com, dezeen.com, yankodesign.com

### Gap URLs (high-citation pages missing Nothing Phone)
- LISTICLE: "best smartphone OS ranked", "best smartphones for photographers 2026", "10 best gadgets"
- COMPARISON: "Android vs iOS", "which brands best value for money"
- Design outlets: dezeen.com CES gadgets, yankodesign.com Gen Z gadgets

### Geography
Current: US only. Expandable via create_prompt with DE, GB, IN, etc.

---

## Scope — Rated and Locked

Rating: **Build** = fully ship with real data | **Partial** = demo-ready with some scaffolding | **Setup** = create the infrastructure, show the capability

> **Eligibility-critical lane (must ship, no exceptions):** items #13 (Gemini), #14 (Tavily), and #20 (Lovable, with Entire as fallback if not integrated by Saturday 17:00) are the three eligible partner technologies required by the hackathon rules. They are tagged across multiple tiers below for organizational reasons, but all three must ship in real code paths or the submission risks disqualification.

### TIER 1: Core Demo (must-ship)

| # | Feature | Rating | Feasibility | Impact | What it does |
|---|---------|--------|-------------|--------|-------------|
| 1 | Topic blind spot map | **Build** | 10 | 10 | 5-topic heatmap: 72% stronghold, 6% ironic gap, 1% invisible. Real Peec data. |
| 2 | Blocked claim + safe rewrite | **Build** | 10 | 10 | "Nothing Phone is the minimalist leader" → BLOCKED. Rules engine, not AI. Demo centerpiece. Data already supports the verdict (6% vs Apple 39%). |
| 3 | Proof chain | **Build** | 8 | 10 | Recommendation → claim → Peec evidence → public proof → guardrail decision. Every link has a source of record. |
| 4 | Channel gap analysis | **Build** | 9 | 9 | Editorial vs UGC split. rtings/whathifi/zdnet gaps. "Community loves you, review sites don't." |
| 5 | AI engine split | **Build** | 9 | 8 | Gemini 26%, ChatGPT 18%, Google AI Overview 17%. Engine-specific visibility story. Sub-finding: Gemini sentiment 56 vs Google AI Overview 71 — a 15-point framing gap, free differentiation. |
| 6 | Content type gaps | **Build** | 8 | 8 | LISTICLE and COMPARISON pages cite Apple/Samsung, not Nothing Phone. Specific URL evidence. |
| 7 | Action brief (PRESENCE_VERDICT.md) | **Build** | 8 | 9 | Structured markdown: topic actions, channel actions, engine actions, blocked claims, monitoring plan. |
| 8 | Executive snapshot | **Build** | 9 | 8 | Hero cards with real numbers. pm-dashboard.html already has the shell. |
| 9 | Evidence ledger (JSON) | **Build** | 7 | 8 | Every claim → claim_id, source refs, evidence tier, guardrail decision. Machine-readable. |

### TIER 1.5: Gap-Type Classifier (must-ship — the new sharp moment)

> **Why this tier exists:** Tier 1 diagnoses *where* the brand is invisible (topic / channel / engine / content type). Tier 1.5 classifies *what kind of fix* each blind spot needs. Without it, every blind spot looks the same and the action brief reads generic. With it, every recommendation carries an intervention type that judges grok in 5 seconds.

| # | Feature | Rating | Feasibility | Impact | What it does |
|---|---------|--------|-------------|--------|-------------|
| 9b | Gap-type classifier | **Build** | 8 | 10 | Every blind-spot finding gets a `gap_type` field — `perception` / `indexing` / `volume_frequency` — with a confidence tier. Buildable from Peec + Tavily + Gemini outputs already in the pipeline. |

**Gap types (definitions and Nothing Phone examples):**

| Gap type | Definition | Detection signals | Nothing Phone example | Intervention class |
|---|---|---|---|---|
| **Perception** | Brand wants to be known for X; AI doesn't perceive it that way. Content exists, citations exist, but the *association* is missing. | Brand profile vs Gemini perception themes diverge; competitor owns the trait language; Tavily public-proof shows competitor dominance on the trait | Minimalist Hardware: 6% vs Apple 39%. Brand built on minimalism, AI associates "minimalist" with Apple. | Positioning + messaging correction; reframing content with explicit trait language |
| **Indexing** | Content exists on owned domains, but isn't surfacing in AI answers. Retrieval ≠ citation. | Owned domain retrieved but citation rate low; Peec `get_url_report` shows retrieval without citation; structured-data signals missing | nothing.tech retrieved but cited at 1.21 — high authority, underused. Some pages indexed but not surfaced for relevant prompts. | Schema markup, structured data, AI-citation optimization, source-of-truth canonicalization |
| **Volume / frequency** | Content is sparse or absent on the topic entirely. Brand has the product/proof point but no public surface area. | Low Peec `get_domain_report` signal across all owned/earned channels; competitor dominates with sustained editorial + UGC volume | Wireless Audio at 1%. Nothing Ear product exists, but near-zero presence in the category. Apple at 53%. | Content creation + distribution + amplification; sustained editorial outreach; UGC seeding |

**Output:** `gap_type` field on every blind-spot row in `study_ssot.json`, surfaced in `PRESENCE_VERDICT.md` ("Blind Spots by Gap Type" section) and `ACTION_BRIEF.md` (intervention class per recommendation). Confidence tier follows the same evidence ladder as the rest of the guardrail engine.

**Demo moment:** *"Nothing Phone has four blind spots. But not all blind spots are the same — Minimalist Hardware is a perception problem, Mobile Ecosystem is an indexing problem, Wireless Audio is a volume problem. Each needs a different fix. Here's the action brief, keyed by gap type."*

### TIER 2: Differentiators (should-ship)

| # | Feature | Rating | Feasibility | Impact | What it does |
|---|---------|--------|-------------|--------|-------------|
| 10 | Chat-level evidence (receipts) | **Partial** | 6 | 9 | Pull 3-5 actual AI responses via list_chats + get_chat. Show "ChatGPT was asked X, responded with Y, Nothing Phone absent." Ultimate receipt. |
| 11 | Peec actions comparison | **Build** | 8 | 7 | Peec's own get_actions recommendations vs our guardrailed version. "We add the no." |
| 12 | Citation vs retrieval authority | **Partial** | 6 | 7 | nothing.tech retrieved but not cited = content found, not trusted. Needs analysis to surface. |
| 13 | Gemini perception analysis | **Build (ELIGIBILITY)** | 7 | 9 | Feed Peec topics + blind spots to Gemini API. Get perception themes, missing associations. **Eligible partner tech #1 — must ship.** Promoted from Tier 2 Partial. |
| 14 | Tavily public evidence | **Build (ELIGIBILITY)** | 7 | 9 | Search "Nothing Phone minimalist hardware" on Tavily. Find proof gaps for editorial-channel domains (rtings, whathifi, dezeen). **Eligible partner tech #2 — must ship.** Promoted from Tier 2 Partial. |

### TIER 3: Prescription Layer (the MCP write loop)

> **Tier 3 framing:** these features show the *setup moment* — the API write succeeds, the prompt/tag/topic is registered in the Peec project. Data populates only after Peec's next daily run, which is post-demo. The proof point is **loop closure** ("we just told Peec what to monitor"), not new metrics. The 2-minute storyboard segment 1:15-1:35 reflects this.

| # | Feature | Rating | Feasibility | Impact | What it does |
|---|---------|--------|-------------|--------|-------------|
| 15 | Geo expansion prompts | **Setup** | 8 | 8 | Create prompts with DE, GB, IN country codes for blind spot topics. Show: "We set up monitoring for your EU market." |
| 16 | Monitoring prompts for gaps | **Setup** | 8 | 8 | Create new prompts targeting Minimalist Hardware and Wireless Audio gaps. Show: "These will track your recovery." |
| 17 | Custom tags for campaigns | **Setup** | 8 | 6 | Create tags like `pop-minimalist`, `pop-wireless-audio`, `pop-engine-chatgpt`. Campaign taxonomy as Peec tags. |
| 18 | New topics for sub-themes | **Setup** | 7 | 6 | Split Minimalist Hardware into sub-topics (desk setups, sustainable tech, transparent design). More granular tracking. |
| 19 | Campaign taxonomy mapping | **Partial** | 5 | 6 | Peec topics → parent themes → campaign types. Rules-based. Adds intellectual depth. |

### TIER 4: Surface Layer

| # | Feature | Rating | Feasibility | Impact | What it does |
|---|---------|--------|-------------|--------|-------------|
| 20 | Lovable dashboard | **Build (ELIGIBILITY)** | 6 | 8 | **Eligible partner tech #3 — must ship in a real code path.** Push generated data to a Lovable project (code `COMM-BIG-PVDK`) for an interactive executive view. Visual style **must follow Peec AI's design philosophy** — clean, data-driven, executive-readable, color/typography aligned with the live peec.ai interface (see [DESIGN_TOKENS.md](DESIGN_TOKENS.md)). **Hard fallback:** if Lovable is not integrated by Saturday 17:00, swap to Entire (review/sign-off workflow over blocked claims) as the third eligible partner tech. `pm-dashboard.html` is the local shell, not a substitute for partner-tech eligibility. |
| 21 | Future Directions static page | **Build** | 9 | 7 | Separate route in the Lovable webapp (e.g., `/future-directions`) showing the channel-activation roadmap. Concept-only content: architecture diagram, illustrative allocation table, methodology description. **No real Pathmatics/MC data, no source names, no Pathmatics-shaped tables.** Banner at top: *"Future Direction — Static Preview. Built externally with permissioned industry benchmark data; not redistributable."* Source content lives in [FUTURE_DIRECTIONS.md](FUTURE_DIRECTIONS.md). |
| 22 | Temporal trend analysis | **Partial** | 5 | 5 | Date dimension for surge/slow-burn detection. Single-market limits story but proves capability. |
| 23 | Multi-brand generalizability | **Setup** | 3 | 5 | Run same pipeline for Attio or BYD. Proves it works for any brand. Doubles scope. |

---

## The Demo Story (2 minutes)

### 0:00-0:15 — The Invisible Champion
"Nothing Phone ranks #1 when AI mentions it — but 80% of AI answers don't mention it at all."
→ Executive snapshot: 20% visibility, 2.4 position, 50 prompts, 5 topics, 10 brands.

### 0:15-0:30 — The Blind Spots (multi-dimensional)
"We found blind spots across four dimensions."
→ Topic map: 72% in Smartphone Design, 6% in Minimalist Hardware (ironic gap)
→ Channel gap: editorial review sites don't cite Nothing Phone
→ Engine split: Gemini 26%, ChatGPT 18%
→ Content type: LISTICLE and COMPARISON pages cite Apple, not Nothing Phone

### 0:30-0:50 — Gap-Type Classifier (the new sharp moment)
"But not all blind spots are the same — each needs a different fix."
→ **Perception** gap (Minimalist Hardware): brand identity vs AI association mismatch — fix with positioning + reframing
→ **Indexing** gap (Mobile Ecosystem): nothing.tech retrieved but underused — fix with schema + structured data
→ **Volume / frequency** gap (Wireless Audio): Nothing Ear exists, presence is near-zero — fix with content creation + amplification
→ Every recommendation in the action brief carries a gap type. Each gap type triggers a different intervention class.

### 0:50-1:10 — The Proof Chain
"Every finding has receipts."
→ Peec: 6% visibility in Minimalist Hardware. Apple at 39%.
→ Tavily: Apple dominates public minimalist content. Editorial gap on rtings/whathifi/dezeen.
→ Gemini: "minimalist" is associated with Apple, not Nothing Phone.
→ Guardrail: methods agree, evidence tier strong, gap type = perception.

### 1:10-1:25 — The Blocked Claim
"The system also says no."
→ "Nothing Phone is the go-to minimalist tech brand" — BLOCKED
→ Safe rewrite provided
→ Next evidence to collect specified

### 1:25-1:40 — The Prescription (loop closure)
"We don't just diagnose — we prescribe and write back into Peec."
→ Action brief: create minimalist content, target ChatGPT, register monitoring prompts
→ `create_prompt` for DE/GB and gap topics, `create_tag` for campaigns
→ Setup, not new metrics — Peec runs daily

### 1:40-1:50 — The Output
"The deliverable is a Presence Verdict Pack."
→ PRESENCE_VERDICT.md, ACTION_BRIEF.md, EVIDENCE_LEDGER.json, manifest.json
→ Every recommendation traceable. Every blocked claim justified.

### 1:50-2:00 — Sneak Peek: Future Direction
"Where this goes next: channel activation."
→ Brief teaser: gap diagnosis → channel scoring → spend recommendation
→ Title card: *"Future direction. Calibrated against external industry benchmarks (held under license, not redistributable)."*
→ "Live in the Lovable dashboard at /future-directions — static preview, separate from the diagnostic pipeline above."

---

## Partner Tech Integration

| Partner | Role | Min integration | Where in pipeline |
|---------|------|----------------|-------------------|
| **Peec MCP** | Required track tool. Source of truth for visibility. | read + write tools | Ingest + prescribe |
| **Gemini** | Eligible partner #1. Analysis engine. | API call for perception themes | Analyze step |
| **Tavily** | Eligible partner #2. Public evidence. | API call for proof search | Enrich step |
| **Lovable** | Eligible partner #3. Dashboard surface. | Push data to Lovable | Surface step |

---

## Artifacts to Ship

| Artifact | Format | Source |
|----------|--------|--------|
| PRESENCE_VERDICT.md | Markdown | Generated from study SSOT |
| ACTION_BRIEF.md | Markdown | Generated from study SSOT |
| EVIDENCE_LEDGER.json | JSON | Every claim + source refs + tiers |
| manifest.json | JSON | Peec snapshot ID, taxonomy version, generated timestamp |
| Dashboard | HTML or Lovable | Executive view of all findings |

---

## Build Priority Order

1. **Peec ingestion** — pull all data into normalized structures
2. **Topic + channel + engine analysis** — generate blind spot map
3. **Gemini integration** — perception themes for each blind spot (eligibility-critical, not optional)
4. **Tavily integration** — public evidence search for gap topics (eligibility-critical, not optional)
5. **Gap-type classifier** — `perception` / `indexing` / `volume_frequency` field on every blind spot row (Tier 1.5, demo centerpiece)
6. **Guardrail engine** — evidence tiers, blocked claims, safe rewrites; consume gap_type as input
7. **Proof chain** — link every finding to sources, including gap type
8. **Action brief generation** — structured markdown from SSOT, recommendations grouped by gap type
9. **Prescription layer** — create monitoring prompts, tags, geo expansion in Peec
10. **Capture Peec design tokens** — pull color, typography, surface-style references from the live peec.ai interface; document in [DESIGN_TOKENS.md](DESIGN_TOKENS.md). Required before Lovable build kicks off.
11. **Dashboard surface (Lovable)** — push data to a Lovable project (eligibility-critical). Visual style must match Peec design tokens. Decision gate at Saturday 17:00: if not integrated, swap to Entire as the third eligible partner tech.
12. **Future Directions static page** — separate route in the Lovable webapp with concept-only content, banner, and architecture diagram. Source content from [FUTURE_DIRECTIONS.md](FUTURE_DIRECTIONS.md). No real Pathmatics/MC data, no source names.
13. **Chat-level evidence** — sample actual AI responses as receipts
14. **Public GitHub repo** — create via `gh-play`, push current scaffold + generated artifacts. Repo must be public.
15. **README finalization** — list every API, framework, and tool actually used. Submission requirement.
16. **Public-safety scan** — run the leak grep from `PUBLIC_SAFETY_CHECKLIST.md` on every generated artifact and the full repo before pushing public. Sanitize any path or private identifier hits. Verify zero source-name fingerprints (no "Morning Consult", "Pathmatics", agency names) in any committed file.
17. **Submission form verification** — confirm the final form link on the hackathon Discord; the pre-event link may be stale.
18. **Video recording** — 2-minute demo (Loom or equivalent), live walkthrough of proof chain + blocked claim + gap-type classifier + prescription loop closure + future-directions sneak peek.
19. **Submit** — public repo URL + video link via the verified submission form, before Sunday 14:00 CEST.

Optional (only if P0 stable by Sunday 12:00):

20. **Aikido side challenge** — connect public repo, capture security report screenshot.

Post-submission (only if advancing to live finalist pitch):

21. **Private demo build** — Sunday afternoon. Channel-activation layer using one-time-permissioned external benchmark data, calibrated to Nothing Phone gaps. Lives outside the public repo. Closes the live pitch.

---

## What This Looks Like to Judges

Most teams: "Here's a dashboard showing your AI visibility."  
Us: "Here's a multi-dimensional diagnosis of your AI blind spots, an evidence-graded action brief with blocked claims, and a monitoring setup already created in Peec to track recovery — with receipts at every step."

The difference: discipline, not flash.
