# Codex Instructions - Peec AI

You are working on the Peec AI track of Big Berlin Hack 2026.

## Your Lane

Implementation + review. You build assigned modules, write tests, do code review, and handle security hygiene.

## Reading Order

1. **[docs/SCOPE_FINAL.md](docs/SCOPE_FINAL.md) - locked scope, 6-axis model, build priority order (read first)**
2. [.agent-context/INDEX.md](.agent-context/INDEX.md) - onboarding pack
3. [AGENTS.md](AGENTS.md) - lane assignments and coordination rules
4. [../AGENT_BRIEFING.md](../AGENT_BRIEFING.md) - Peec challenge briefing
5. [../BATTLE_PLAN.md](../BATTLE_PLAN.md) - architecture, sprint plan, demo script
6. [docs/PEEC_MCP_EXPLORATION.md](docs/PEEC_MCP_EXPLORATION.md) - verified IDs, channel data, engine split
7. [docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md) - build order and data flow
8. [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md) - JSON schemas
9. [docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) - guardrail rules
10. [docs/PUBLIC_SAFETY_CHECKLIST.md](docs/PUBLIC_SAFETY_CHECKLIST.md) - pre-commit safety

## Key Rules

- Play context only. No work credentials or connectors.
- No early start: all application code created after Saturday 10:00 CEST.
- Track locked: Peec. Brand locked: Nothing Phone.
- At least 3 eligible partner technologies in real code paths. Aikido is side-only.
- Partner stack: Gemini + Tavily + Lovable. Peec MCP is required track tool.
- Check `git log` and open branches before starting a module.
- Branch naming: `codex/<topic>`. Rebase on main before PR. Squash on merge.
- Public repo + 2-minute video required. Submission deadline: Sunday 14:00 CEST.
- Run the public safety checklist before every commit. No private paths, client names, or work identifiers.

## Product

Presence Verdict Pack: evidence-graded marketing recommendations from Peec visibility data on the Nothing Phone project.
- `PRESENCE_VERDICT.md` + `ACTION_BRIEF.md` + `EVIDENCE_LEDGER.json` + `manifest.json`
- Pipeline: Peec snapshot -> Peec topics -> Tavily enrichment -> Gemini analysis -> guardrails -> artifacts
- Tagline: "Find your brand's blind spots in AI answers"

## Coordination

- Claude handles architecture + backend (pipeline, data model, guardrails, artifact generation).
- You handle implementation of assigned modules + tests + code review.
- Gemini handles Peec MCP exploration + brand data checks + cross-checks.
- Do not duplicate work another agent is already doing.
