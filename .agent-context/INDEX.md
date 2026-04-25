# Agent Context — Presence Rx

Cold-start pack for any agent (Claude / Codex / Gemini / Cursor / human) joining the Peec AI track of Big Berlin Hack 2026. Read this before touching any code or doc.

> Pack version: `0.4.0` — Saturday 2026-04-25, late afternoon. Product renamed **Proof of Presence → Presence Rx** (D-014). New primary tagline: *Diagnose. Prescribe. Refuse.*
> Project: `big-berlin-hack/challenges/peec/repo` (GitHub repo will be `presence-rx` when created via `gh-play`)

## What This Pack Is

Onboarding surface for any agent joining the build. It gives you:

- The product in one paragraph
- The locked decisions and why
- Real Peec data and IDs you can copy-paste into code
- Glossary so you don't get confused by overlapping terms
- Where every artifact lives
- Your lane and what's expected
- The shortest path from cold start to first contribution

## Read in This Order

1. [OVERVIEW.md](OVERVIEW.md) — what we're building and why (5 min)
2. [DECISIONS.md](DECISIONS.md) — locked decisions + rationale + open questions (5 min)
3. [GROUND_TRUTH.md](GROUND_TRUTH.md) — real Peec data, IDs, metrics (3 min, reference)
4. [GLOSSARY.md](GLOSSARY.md) — terminology (2 min, reference)
5. [LANES.md](LANES.md) — find your lane and your reading list (3 min)
6. [ARTIFACTS.md](ARTIFACTS.md) — where every doc, file, and artifact lives (2 min, reference)
7. [ONBOARDING.md](ONBOARDING.md) — your first 30 minutes after reading the pack (3 min)

Total cold-start time: ~25 min. After that, jump to the lane-specific reading list in [LANES.md](LANES.md).

## Source-of-Truth Pointers

If anything in this pack contradicts these, **the canonical doc wins** and this pack should be patched:

| Topic | Canonical doc |
| --- | --- |
| Locked scope (what to build) | [../docs/SCOPE_FINAL.md](../docs/SCOPE_FINAL.md) |
| Real Peec data | [../docs/PEEC_MCP_EXPLORATION.md](../docs/PEEC_MCP_EXPLORATION.md) |
| Build status / submission gates | [../docs/INTEGRATION_CHECKLIST.md](../docs/INTEGRATION_CHECKLIST.md) |
| Active validation findings | [../docs/VALIDATION_REPORT.md](../docs/VALIDATION_REPORT.md) |
| Artifact JSON contracts | [../docs/ARTIFACT_CONTRACTS.md](../docs/ARTIFACT_CONTRACTS.md) |
| Guardrail rules | [../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](../docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) |
| Public-safety rules | [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) |
| End-to-end flow + 2-min storyboard | [../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](../docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md) |
| Future-directions (channel activation) concept | [../docs/FUTURE_DIRECTIONS.md](../docs/FUTURE_DIRECTIONS.md) |
| Lovable webapp design tokens (Peec alignment) | [../docs/DESIGN_TOKENS.md](../docs/DESIGN_TOKENS.md) |

## Hard Rules (Do Not Violate)

- Play context only. **No work credentials, no work connectors, no work SaaS endpoints.**
- The repo will be public. Run [../docs/PUBLIC_SAFETY_CHECKLIST.md](../docs/PUBLIC_SAFETY_CHECKLIST.md) before any push.
- A partner technology counts toward eligibility only if it sits on a **real code path or visible workflow**. No "planned-only" claims.
- Aikido is side-only and does not count toward the 3-partner minimum.
- Submission deadline is **Sunday 14:00 CEST**, not 14:01.

## Pack Maintenance

This pack is `0.4.0`. Update the relevant file when:

- A locked decision changes → update [DECISIONS.md](DECISIONS.md)
- New verified Peec data lands → update [GROUND_TRUTH.md](GROUND_TRUTH.md)
- A new doc is added or removed → update [ARTIFACTS.md](ARTIFACTS.md)
- A lane assignment changes → update [LANES.md](LANES.md)

After any update, bump the pack version in this file and note what changed.

## Changelog

- `0.4.0` (2026-04-25, late afternoon) — **Product renamed: Proof of Presence → Presence Rx (D-014).** Primary tagline locked: *Diagnose. Prescribe. Refuse.* (with *Find your brand's blind spots in AI answers* as sub-tagline). Single-pass rename touched 14 files, 30 mentions: SCOPE_FINAL, README (new diagnose/prescribe header), BATTLE_PLAN, AGENT_BRIEFING, OVERVIEW, INDEX, DECISIONS (D-003 updated + new D-014), ARTIFACTS, GLOSSARY (with new gap-type / future-directions / design terms added), LANES (Lovable lane now references DESIGN_TOKENS + Tier 4 #21 future-directions page), ONBOARDING (lane task assignments now include gap-type classifier and design-tokens capture), VALIDATION_REPORT, PEEC_MCP_EXPLORATION, PEEC_PM_VISUAL_BOARD, INTEGRATION_CHECKLIST, pm-dashboard.html. Deliverable name "Presence Verdict Pack" preserved. GitHub repo target name: `presence-rx`.
- `0.3.0` (2026-04-25, late afternoon) — Three new locked decisions: D-011 (gap-type classifier as Tier 1.5 — `perception` / `indexing` / `volume_frequency` field on every blind spot, demo centerpiece), D-012 (future-directions split: public concept-only `FUTURE_DIRECTIONS.md` + private prototype outside repo, sneak peek in submission video, full demo only at live finalist pitch), D-013 (Lovable webapp must follow Peec AI design philosophy with tokens captured in `DESIGN_TOKENS.md`). Two new docs: `FUTURE_DIRECTIONS.md`, `DESIGN_TOKENS.md`. SCOPE_FINAL build priority order extended from 16 to 19 steps + post-submission private-demo step. Demo storyboard updated to weave gap-type moment (0:30-0:50) and sneak peek (1:50-2:00).
- `0.2.0` (2026-04-25) — Post-cleanup refresh. HANDOFF.md retired; references removed from ARTIFACTS, ONBOARDING. Top-level BATTLE_PLAN slimmed to a pointer at SCOPE_FINAL. Top-level AGENT_BRIEFING tightened. pm-dashboard.html aligned with locked scope (Build Status replaces PM Questions tab; Value-Add narrowed to in-scope items).
- `0.1.0` (2026-04-25) — First version of the pack, post-scope-lock.
