# Lanes - Who Builds What

Find your lane below. Read the lane-specific reading list and start there.

## Lane Assignments

| Agent | Lane | Primary responsibility | Reading list |
| --- | --- | --- | --- |
| **Claude (this session)** | Architecture + backend | Pipeline shape, data model, guardrail engine, integration glue, artifact generation. Writes the orchestration code. | INDEX -> OVERVIEW -> DECISIONS -> GROUND_TRUTH -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) -> [../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md) -> [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md) -> [../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) |
| **Codex** | Implementation + review | Implements assigned modules, writes tests, does code review. | INDEX -> OVERVIEW -> [../codex.md](../codex.md) -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) -> [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md) -> [../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) -> [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) |
| **Gemini** | Research + validation | Peec MCP exploration (Phase 1 residuals), brand data validation, Gemini API integration for perception themes, partner-tech cross-checks. | INDEX -> OVERVIEW -> [../GEMINI.md](../GEMINI.md) -> GROUND_TRUTH -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) -> [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md) -> [../docs/PEEC_MCP_TOOL_MAP.md](../docs/PEEC_MCP_TOOL_MAP.md) -> [../docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md](../docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md) |
| **Claude (design)** | Frontend / UX | Lovable dashboard surface (eligibility-critical) or Entire fallback. Webapp must follow Peec design philosophy (D-013) — capture design tokens before visual work lands. Also builds the static `/future-directions` page from FUTURE_DIRECTIONS.md (Tier 4 #21). Activated Sunday or on demand. | INDEX -> OVERVIEW -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) Tier 4 #20 + #21 -> [../docs/DESIGN_TOKENS.md](../docs/DESIGN_TOKENS.md) -> [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md) -> [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md) (study_ssot, hero_cards, pipeline_funnel) -> [../pm-dashboard.html](../pm-dashboard.html) for layout reference |
| **Cursor / Composer** | External QA | Pull-based skeptical review at gates. Verifies evidence refs, guardrail decisions, blocked-claims register, and partner-tech honesty. Runs the public-safety scan on every generated artifact. | INDEX -> [../.cursorrules](../.cursorrules) -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) -> [../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) -> [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) |
| **Human (Amit)** | Decisions + pitch | Track lock (done), brand lock (done), mentor / organiser questions, demo recording, finalist pitch, final submission. Resolves open questions Q-001 through Q-004 in [DECISIONS.md](DECISIONS.md). | INDEX -> OVERVIEW -> DECISIONS -> [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) |

## Branching Convention

- Default branch: `main`.
- Feature branches: `<lane>/<topic>` - e.g. `claude/ingestion`, `codex/guardrails`, `gemini/perception`.
- Rebase on `main` before opening a PR. Squash on merge.
- Before starting a module, check `git log` and open branches; another agent may have built it.

## Coordination Rules

- **Parallel-safe modules:** Peec ingestion (Claude) / Gemini API (Gemini lane) / Tavily integration (any lane) / dashboard (Claude design or Lovable lane) / DESIGN_TOKENS capture from peec.ai (Claude design, parallel to backend) - all independent until they read from the shared `study_ssot.json`.
- **Serial-required:** Gap-type classifier (Tier 1.5) consumes Peec + Tavily + Gemini outputs and feeds the guardrail engine; build it after ingestion + enrichment, before guardrails. Guardrail engine must exist before artifact generation. Artifact generation must exist before dashboard wiring. Design tokens must be captured before any Lovable visual work lands.
- **Hand-off shape:** every module reads from JSON contracts ([../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md)) and writes to JSON contracts. Markdown is regenerable from JSON; do not hand-edit Markdown artifacts.
- **No partner drift:** if you change which partner tech is called from a code path, update the README + [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) eligibility lane immediately.
- **No silent blanks:** every missing metric uses `null` plus `unavailable_reason`, never `0` or empty string.

## Decision Gates

| Gate | When | Owner | Action |
| --- | --- | --- | --- |
| Lovable feasibility | Saturday 17:00 CEST | Dashboard lane | If Lovable not pushing data, swap to Entire (D-005, D-009) |
| Pre-submission readiness | Sunday 12:00 CEST | All lanes | Self-check against [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md) submission gates |
| Public-safety scan | Before every push | Cursor / Composer | Run [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) grep on every generated artifact |
| Submission | Sunday 14:00 CEST | Amit | Public repo URL + 2-min video link via verified form |

## What Not to Do

- Do not build features outside [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md). Scope creep is the #1 risk.
- Do not commit secrets, private paths, or work-side identifiers. Run public-safety scan first.
- Do not delete anything in Peec MCP (no `delete_*` calls).
- Do not refactor working demo-ready code. Polish only after end-to-end pipeline runs once.
- Do not promote a partner tech claim without a real code path or visible workflow.

## When to Update

Add a lane when a new agent joins. Update reading lists when [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) sequence changes.
