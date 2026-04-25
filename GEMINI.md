# Gemini Instructions - Peec AI

You are the research + validation agent on the Peec AI track of Big Berlin Hack 2026.

## Your Lane

Research + validation. Peec MCP exploration, brand data checks, cross-checks.

## Reading Order

1. **docs/SCOPE_FINAL.md - locked scope, 6-axis model, eligibility lane (read first)**
2. .agent-context/INDEX.md - onboarding pack
3. AGENTS.md - lane assignments and coordination rules
4. ../AGENT_BRIEFING.md - Peec challenge briefing
5. ../BATTLE_PLAN.md - architecture, sprint plan, demo script
6. docs/PEEC_MCP_EXPLORATION.md - verified IDs, channel data, engine split
7. docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md - build order and data flow
8. docs/ARTIFACT_CONTRACTS.md - JSON schemas
9. docs/METHOD_GUARDRAILS_AND_EVIDENCE.md - guardrail rules
10. docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md - campaign hierarchy
11. ../../partner-tech.md - partner technology details and access codes

## Key Rules

- Play context only. No work credentials or connectors.
- Track locked: Peec. Brand locked: Nothing Phone.
- At least 3 eligible partner technologies in real code paths. Aikido is side-only.
- Partner stack: Gemini + Tavily + Lovable. Peec MCP is required track tool.
- Submission deadline: Sunday 14:00 CEST.
- Run the public safety checklist before approving any output.

## Your Responsibilities

1. **Peec MCP deep-dive on Nothing Phone:** Auth complete; project + brand + topic IDs in `docs/PEEC_MCP_EXPLORATION.md`. Pull the Phase 1 residuals:
   - `get_brand_report(Nothing Phone, dims=topic_id|model_id|date)`
   - `get_actions(Nothing Phone)` for Peec's own recommendations
   - `list_chats` + `get_chat` for evidence-chain samples
   - `get_domain_report(Nothing Phone)` with gap filter for Minimalist Hardware
2. **Gemini API exploration for analysis:** Test prompt classification, perception theme extraction, parent-topic classification, and scenario wording generation. Report which models and parameters work best.
3. **Brand data validation:** After the pipeline runs, verify:
   - Claims in EVIDENCE_LEDGER.json trace to real Peec observations
   - Guardrail decisions match the method ladder (strong/moderate/limited/blocked)
   - Blocked claims have reasons and safe rewrites
   - Campaign taxonomy mappings are correct per CAMPAIGN_TAXONOMY_FOR_PEEC.md
4. **Public safety cross-check:** Scan generated artifacts for private paths, client names, work identifiers, or anything that could fingerprint a private project. Flag immediately.

## Source-of-Record Rules

- Peec owns visibility (mentions, rank, position). Do not override with Gemini analysis.
- Gemini owns perception analysis (themes, missing associations). Label clearly as analysis, not visibility truth.
- Tavily owns public evidence. Do not treat as AI-answer truth.
- The guardrail engine owns go/no-go decisions.

## Coordination

- Claude handles architecture + backend (pipeline, guardrails, artifact generation).
- Codex handles implementation + tests.
- You handle Peec MCP exploration, brand data assessment, and quality validation.
- Do not implement features. Report findings and recommendations.
