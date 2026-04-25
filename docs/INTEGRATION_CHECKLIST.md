# Integration Checklist

Active execution checklist. Maps the locked scope ([SCOPE_FINAL.md](SCOPE_FINAL.md)) to concrete checkboxes. Cross-agent source of truth for what's wired, what's pending, and what gates submission.

Track lock: **Peec (focused track)**. Brand lock: **Nothing Phone**. Deadline: **Sunday 14:00 CEST**.

## Phase 0 - Foundation (mostly done)

- [x] Peec MCP server registered in `~/.claude.json` for the big-berlin-hack project
- [x] Peec OAuth completed
- [x] Repo scaffold (README, AGENTS.md, CLAUDE.md, GEMINI.md, codex.md, .cursorrules)
- [x] Public-safe docs (13 in `docs/`)
- [x] `pm-dashboard.html` (4-tab static walkthrough, refreshed with verified MCP findings)
- [x] MCP exploration captured in `docs/PEEC_MCP_EXPLORATION.md` (project IDs, brand IDs, topic IDs, metric definitions)
- [ ] Public GitHub repo created via `gh-play` and `git remote` wired
- [ ] Confirm partner-tech eligibility with organisers (does Peec MCP count toward the 3?)
- [ ] Verify the Discord submission form link
- [x] Reconcile product naming: locked on **Presence Rx** (renamed from Proof of Presence per D-014) for the product, **Presence Verdict** (artifact name `PRESENCE_VERDICT.md`) for the deliverable, **Diagnose. Prescribe. Refuse.** as primary tagline. All in-repo docs reconciled to this naming.

## Phase 1 - Peec Data Audit

Project inventory complete. See `docs/PEEC_MCP_EXPLORATION.md` for full output.

- [x] `list_projects` - 4 projects discovered, IDs captured
- [x] `list_brands(Nothing Phone)` - 10 brands resolved (Nothing Phone + 9 competitors with full metrics), IDs captured
- [x] `list_topics(Nothing Phone)` - 5 topics resolved with per-topic visibility / SoV / position, IDs captured
- [x] `list_prompts(Nothing Phone)` - 50 prompts surveyed across the 5 topics
- [x] `get_brand_report(Nothing Phone, dimensions=["topic_id"])` - 5-topic visibility detail captured (72% / 12% / 10% / 6% / 1%)
- [x] `get_brand_report(Nothing Phone, dimensions=["model_id"])` - 3 engines captured (Gemini 26%, ChatGPT 18%, Google AI Overview 17%)
- [x] `get_actions(Nothing Phone)` - opportunity-scored recommendations pulled; we ingest as input and layer guardrails on top
- [x] `get_domain_report(Nothing Phone)` with gap filter - editorial gap domains identified (rtings, whathifi, zdnet, samsung.com, wallpaper.com, dezeen, yankodesign)
- [x] `get_url_report(Nothing Phone)` with gap filter - LISTICLE / COMPARISON gap URLs identified
- [ ] `list_chats` + `get_chat` for 3-5 high-traffic prompts - sample actual AI responses to use as receipts (Tier 2 #10)

## Phase 2 - Brand Strategy: Existing vs Custom Project

**Locked: Strategy A on Nothing Phone.** Other teams will default to Attio - we win uniqueness, the "Invisible Champion" data story, and a stronger ironic-blind-spot demo moment (6% in Minimalist Hardware vs Apple's 39%).

### A. Sample-anchored (LOCKED)
Run the full pipeline against the Nothing Phone project. 10 brands, 5 topics, 50 prompts already populated. No snapshot-timing risk.

- [x] Project: **Nothing Phone** (`or_faaa7625-bc84-4f64-a754-a412d423c641`)
- [x] Own brand: **Nothing Phone** (`kw_d9414ede-8870-47a8-b377-14f887986e67`)
- [x] Competitors: Apple, Google, Samsung, Pixel, Sony, Bose, Xiaomi, OnePlus, Logitech (IDs in `PEEC_MCP_EXPLORATION.md`)
- [x] Topics: Smartphone Design (stronghold), Mobile Ecosystem, Consumer Tech Innovation, Minimalist Hardware (ironic gap), Wireless Audio (IDs captured)
- [x] Baseline metrics captured: 20% overall visibility, 8% SoV, position 2.4, 4/5 topics with blind spots
- [ ] Capture brand-report breakdowns by date and model_id once Phase 1 residuals are pulled

**MCP constraint discovered:** there is no `create_project` tool. We can `create_brand` / `create_prompt` / `create_topic` inside existing projects, but new prompts need daily runs to populate data. This rules out Strategy B (full custom project) and reshapes Strategy C.

### B. Custom project (NOT AVAILABLE)
Peec MCP has no `create_project` tool. This strategy is closed off.

### C. Extension-within-project (optional sidebar)
Add new brands or prompts to the **existing Nothing Phone project** via `create_brand` / `create_prompt` / `create_topic`. New prompts only populate after daily runs, so use this for a "we can extend coverage on demand" sidebar, not as a critical path.

- [x] Phase 2A complete on Nothing Phone
- [ ] Optional: `create_prompt` on the Nothing Phone project to seed a coverage gap (e.g. minimalist-desk prompts) - acknowledge data won't be live for the demo, but the API call itself is the proof point
- [ ] Demo storyboard updated to show 1:30 on Nothing Phone data, 0:30 on the feedback-loop output (`prompts_to_add.json` from value-add #1)

### Public-safety rules for any brand input
- Use only public brand names (no private clients, no internal org names, no work-context teams)
- Prompts must read like real public buyer queries; no internal taxonomy, ticket IDs, or private-source language
- Re-run the public-safety scan after any custom-project edit

### Write-tool guardrails
- Never call delete tools on existing Peec projects/brands/prompts
- Use `create_*` only; if a mistake is made, recreate rather than delete
- Tag every custom artifact with a clear `bbh-2026-` prefix where supported, so it's easy to identify post-hackathon

## Phase 3 - Partner Wiring (P0 build)

Each partner must sit on a real code path before it can be claimed. Aikido is side-only.

### Peec MCP - data ingestion
- [ ] `src/ingest_peec.ts` - normalize Peec MCP output into `prompt_universe.json`
- [ ] Capture `peec_snapshot_id`, prompt text, brands_mentioned, sources, position, model
- [ ] Carry Peec evidence refs (`peec:prompt:NNN`, `peec:chat:NNN`) through every downstream artifact

### Gemini - analysis
- [ ] `src/analyze_gemini.ts` with `GEMINI_API_KEY` from `.env`
- [ ] Implementations: parent-topic classification, perception themes, missing associations, scenario wording
- [ ] Output goes into `parent_topics.json`, `study_ssot.json` (perception_*), and narrative cards
- [ ] Source-of-record: Gemini owns analysis only, never visibility metrics

### Tavily - public evidence
- [ ] `src/enrich_tavily.ts` with `TAVILY_API_KEY` (overflow code `TVLY-DLEE5IJU` if needed)
- [ ] Use for competitor proof, public proof gaps, source-appendix evidence refs
- [ ] Output goes into `EVIDENCE_LEDGER.json` evidence array

### Lovable - dashboard
- [ ] Build a Lovable project at lovable.dev with code `COMM-BIG-PVDK` (Pro Plan 1, monthly)
- [ ] Read `study_ssot.json`, `hero_cards.json`, `pipeline_funnel.json`, `source_of_record.json`
- [ ] Mirror at minimum: hero cards, prompt cluster table, proof chain panel, blocked-claims panel
- [ ] Fallback if Lovable stalls: Entire CLI for review/signoff workflow, or local static dashboard (we already have `pm-dashboard.html` as a model)

## Phase 4 - Pipeline Build (P0)

Per `END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md`:

- [ ] `src/types.ts` - shared types matching artifact contracts
- [ ] `src/ingest_peec.ts` - Peec snapshot to normalized observations
- [ ] `src/cluster.ts` - rule grouping + Gemini theme labels for prompt clusters
- [ ] `src/enrich_tavily.ts` - public evidence collection
- [ ] `src/analyze_gemini.ts` - parent topics + perception + scenarios
- [ ] `src/guardrails.ts` - three-field check (`input_gate_status`, `evidence_tier`, `publication_status`)
- [ ] `src/generate_artifacts.ts` - emit all artifacts
- [ ] One end-to-end run from real Peec snapshot to all artifacts, no manual edits

## Phase 5 - Artifacts (must exist before demo)

Required:
- [ ] `data/generated/prompt_universe.json`
- [ ] `data/generated/study_ssot.json`
- [ ] `data/generated/EVIDENCE_LEDGER.json` (with at least one blocked claim)
- [ ] `data/generated/manifest.json` (with snapshot_id, taxonomy_version, freshness, comparability)
- [ ] `data/generated/PRESENCE_VERDICT.md`
- [ ] `data/generated/ACTION_BRIEF.md` (with `CLAIMS_TO_AVOID` section)

Differentiators (do if P0 is repeatable):
- [ ] `data/generated/parent_topics.json`
- [ ] `data/generated/topic_coverage_audit.json`
- [ ] `data/generated/method_comparison.json`
- [ ] `data/generated/cluster_diagnostics.json`
- [ ] `data/generated/pipeline_funnel.json`
- [ ] `data/generated/source_of_record.json`
- [ ] `data/generated/hero_cards.json`
- [ ] `data/generated/scenario_assumptions.json`
- [ ] `data/generated/stage_readiness.json`

## Phase 6 - Demo Proof Path

The demo must walk one recommendation from action -> claim -> evidence -> source -> guardrail, and show one blocked claim. Per `END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md` storyboard:

- [ ] Executive snapshot view (hero cards)
- [ ] Pipeline funnel screen
- [ ] Prompt cluster map
- [ ] Proof chain on one selected recommendation
- [ ] Blocked-claim screen with reason + safe rewrite
- [ ] Action brief screen
- [ ] (Hybrid only) custom-brand extensibility sidebar

## Phase 7 - Submission Gates

- [ ] Public GitHub repo created via `gh-play`, code pushed
- [ ] README lists every API, framework, and tool actually used (no planned-only claims)
- [ ] Public-safety scan clean on the repo and on every generated artifact
- [ ] Any internal-only file is gitignored or sanitized (no `/Users/...` paths, no work-side identifiers)
- [ ] 2-minute video recorded on Loom or equivalent, walkthrough matches real behavior
- [ ] Submission form link verified on Discord
- [ ] Form submitted before Sunday 14:00 CEST

## Phase 8 - Side Challenge (optional, only if P0 stable)

- [ ] Aikido: connect public repo, take security report screenshot, capture before final crunch
- [ ] Skip Pioneer / Gradium unless main demo is rock-solid

## Cross-cutting Verification (run before submission)

- [ ] Every recommendation in `ACTION_BRIEF.md` has `claim_id`, `cluster_id`, `evidence_refs`, `confidence_tier`, `publication_status`, `allowed_language`
- [ ] Every missing metric in any artifact uses `null` + `unavailable_reason`, not silent blanks
- [ ] At least one claim is `blocked` or `directional` and visibly downgraded
- [ ] Source-of-record map matches the actual generator (Peec=visibility, Gemini=analysis, Tavily=public-proof, derived=guardrails)
- [ ] `manifest.json` includes `peec_snapshot_id`, `artifact_version`, `topic_taxonomy_version`, `campaign_type_mapping_version`, `freshness`, `comparability`
- [ ] Three eligible partner technologies have visible, real code paths (not "in the README only")
