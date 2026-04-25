# Artifacts Map

Where every doc, file, and generated artifact lives in this repo. Use this as a directory.

## Repo Root (`challenges/peec/repo/`)

| File | Purpose |
| --- | --- |
| [../README.md](../README.md) | Public-facing repo entry point. SCOPE_FINAL is the first link. |
| [../AGENTS.md](../AGENTS.md) | Lane assignments and coordination rules at the repo level. |
| [../CLAUDE.md](../CLAUDE.md) | Claude-specific reading order. |
| [../GEMINI.md](../GEMINI.md) | Gemini-specific lane and Phase 1 residuals. |
| [../codex.md](../codex.md) | Codex-specific lane and reading order. |
| [../.cursorrules](../.cursorrules) | Cursor / Composer external-QA role and reading order. |
| [../LICENSE](../LICENSE) | Open-source license for the public repo. |
| [../.editorconfig](../.editorconfig) | Editor config for consistent formatting. |
| [../.env.example](../.env.example) | Template for local credentials (Gemini, Tavily, Lovable). Never commit `.env`. |
| [../.gitignore](../.gitignore) | Ignored files including `data/local/`, `.agent-chorus/sessions/`, `.env`. |
| [../pm-dashboard.html](../pm-dashboard.html) | Self-contained 4-tab visual walkthrough of the product. Local shell, NOT a partner-tech eligibility substitute. |

## Active Plan (`docs/`)

| File | Purpose |
| --- | --- |
| [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) | **THE LOCKED PLAN.** 22 features in 4 tiers, 6-axis blind-spot model, eligibility lane, 16-step build priority order with submission gates. Read first. |
| [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md) | Phase-by-phase build checklist mapping SCOPE_FINAL to concrete checkboxes. |
| [../docs/VALIDATION_REPORT.md](../docs/VALIDATION_REPORT.md) | Current verified state, gaps, next implementation cut. |

## Reference - MCP and Data (`docs/`)

| File | Purpose |
| --- | --- |
| [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md) | Verified MCP exploration: project + brand + topic IDs, channel data, engine split, gap URLs, metric definitions, pipeline mapping. |
| [../docs/PEEC_MCP_TOOL_MAP.md](../docs/PEEC_MCP_TOOL_MAP.md) | Tool-by-tool mapping of Peec MCP read and write tools to our pipeline stages. Includes write-tool constraints (no `create_project`). |

## Reference - Methodology (`docs/`)

| File | Purpose |
| --- | --- |
| [../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md) | Pipeline narrative, file tree, dashboard wireframes, 2-minute demo storyboard. Includes the 6-axis blind-spot model. |
| [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md) | JSON schemas for every artifact (prompt_universe, study_ssot, EVIDENCE_LEDGER, manifest, parent_topics, method_comparison, pipeline_funnel, source_of_record, hero_cards, ...). Examples polished to Nothing Phone. |
| [../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) | Method ladder, three-field guardrail, evidence tiers, claim language rules, blocked-claims register. |
| [../docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md](../docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md) | 4 categories x 10 types x 14 visibility topics. Nothing Phone starter mapping. Fallback granularity rules. |
| [../docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md](../docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md) | Two-stage topic system: candidate -> filter -> classify -> fallback tiers -> coverage audit. Nothing Phone parent themes. |
| [../docs/ANALYTICS_PATTERNS_FOR_PEEC.md](../docs/ANALYTICS_PATTERNS_FOR_PEEC.md) | Public-safe analytics patterns: evidence ledger, claim ledger, prompt-universe routing, three-track framing, demo proof step. |
| [../docs/TREND_ECON_PATTERNS.md](../docs/TREND_ECON_PATTERNS.md) | Trend-style mechanics adapted: prompt clusters as trend objects, surge vs slow-burn, quality flags, SSOT, strategic quadrant, decision buckets. |
| [../docs/PLANNING_AND_MEASUREMENT_PATTERNS.md](../docs/PLANNING_AND_MEASUREMENT_PATTERNS.md) | Scenario-planning, reporting, readiness gates, visible assumptions, sparse-data behavior. |

## Reference - Communication (`docs/`)

| File | Purpose |
| --- | --- |
| [../docs/PEEC_PM_VISUAL_BOARD.md](../docs/PEEC_PM_VISUAL_BOARD.md) | Fast walkthrough for the Peec PM. Validation questions for partner-tech eligibility and demo fit. |
| [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) | Pre-commit, pre-push, pre-record safety rules. Run before every public release. |
| [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md) | Channel-activation roadmap. Concept-only. Sources the static `/future-directions` page in the Lovable webapp. Generic vendor references (Morning Consult, Pathmatics, brand-lift methodology) are fine. No agency attribution, no specific client engagement, no engagement-bound data. |
| [../docs/DESIGN_TOKENS.md](../docs/DESIGN_TOKENS.md) | Lovable webapp design constraint (D-013): the webapp must follow Peec AI's visual philosophy. Tokens captured from the live peec.ai interface — checklist to fill in before the Lovable lane lands visual work. |

## Onboarding Pack (this folder, `.agent-context/`)

| File | Purpose |
| --- | --- |
| [INDEX.md](INDEX.md) | Entry point for any new agent. Reading order. |
| [OVERVIEW.md](OVERVIEW.md) | What we're building and why. |
| [DECISIONS.md](DECISIONS.md) | Locked decisions with rationale + open questions. |
| [GROUND_TRUTH.md](GROUND_TRUTH.md) | Real Peec data and IDs to copy-paste into code. |
| [GLOSSARY.md](GLOSSARY.md) | Terminology canon. |
| [LANES.md](LANES.md) | Who builds what. |
| [ARTIFACTS.md](ARTIFACTS.md) | This file. |
| [ONBOARDING.md](ONBOARDING.md) | Your first 30 minutes after reading the pack. |

## Generated Artifacts (`data/generated/`, not yet created)

These are the files the pipeline will produce. None exist yet.

### Required (Tier 1 / submission-critical)

| File | Source | Status |
| --- | --- | --- |
| `data/generated/prompt_universe.json` | Peec MCP ingestion | Not built |
| `data/generated/study_ssot.json` | Pipeline analysis | Not built |
| `data/generated/EVIDENCE_LEDGER.json` | Guardrail engine output | Not built |
| `data/generated/PRESENCE_VERDICT.md` | Generated from study_ssot | Not built |
| `data/generated/ACTION_BRIEF.md` | Generated from study_ssot | Not built |
| `data/generated/manifest.json` | Pipeline orchestrator | Not built |

### Differentiator (Tier 2)

| File | Source | Status |
| --- | --- | --- |
| `data/generated/parent_topics.json` | Gemini parent-topic classification | Not built |
| `data/generated/topic_coverage_audit.json` | Coverage audit | Not built |
| `data/generated/method_comparison.json` | Cross-method agreement | Not built |
| `data/generated/cluster_diagnostics.json` | Cluster QA | Not built |
| `data/generated/pipeline_funnel.json` | Pipeline stage counts | Not built |
| `data/generated/source_of_record.json` | Source ownership map | Not built |
| `data/generated/hero_cards.json` | Dashboard hero cards | Not built |

### Prescription (Tier 3, post-write)

| File | Source | Status |
| --- | --- | --- |
| `data/generated/prompts_to_add.json` | Feedback-loop generator | Not built |
| `data/generated/scenario_assumptions.json` | Scenario planner | Not built |
| `data/generated/stage_readiness.json` | Workflow status | Not built |

## Source Code (`src/`, not yet created)

Per the build guide:

| File | Purpose | Status |
| --- | --- | --- |
| `src/types.ts` | Shared types matching artifact contracts | Not built |
| `src/ingest_peec.ts` | Peec MCP ingestion (all 6 axes) | Not built |
| `src/cluster.ts` | Topic mapping + parent topic classification | Not built |
| `src/enrich_tavily.ts` | Tavily public evidence search | Not built |
| `src/analyze_gemini.ts` | Gemini perception + scenario analysis | Not built |
| `src/guardrails.ts` | Three-field check + decision buckets + blocked claims | Not built |
| `src/generate_artifacts.ts` | Emit Markdown + JSON artifacts | Not built |
| `src/prescribe.ts` | MCP write tools (create_prompt, create_tag, create_topic) | Not built |

## Parent Challenge Files (`challenges/peec/`)

| File | Purpose |
| --- | --- |
| [../../AGENT_BRIEFING.md](../../AGENT_BRIEFING.md) | Peec challenge briefing. Points to SCOPE_FINAL and this onboarding pack. |
| [../../BATTLE_PLAN.md](../../BATTLE_PLAN.md) | Sprint plan and demo script. Annotated as superseded by SCOPE_FINAL for execution. |

## Big Berlin Hack Root (`big-berlin-hack/`)

| File | Purpose |
| --- | --- |
| [../../../../README.md](../../../../README.md) | Root hackathon HQ index. |
| [../../../../AGENT_BRIEFING.md](../../../../AGENT_BRIEFING.md) | Cross-track shared rules and coordination. |
| [../../../../TRACK_DECISION.md](../../../../TRACK_DECISION.md) | Annotated as LOCKED ON PEEC AI. |
| [../../../../partner-tech.md](../../../../partner-tech.md) | Eligible partner technologies + access codes. |
| [../../../../rules-and-submission.md](../../../../rules-and-submission.md) | Submission requirements (public repo + 2-min video + form). |

## What Not in This Map

- `.agent-chorus/` (provider configs for chorus runtime - automatic, no manual edits expected).
- `.git/` (version control internals).
- `data/local/`, `data/private/` (gitignored, never committed).
- `node_modules/`, `.venv/` (gitignored).

## When to Update

Add a row when a new file or generated artifact lands. Move a "Not built" status to "Built" with a one-line description when generation succeeds.
