# Presence Rx

> **Diagnose. Prescribe. Refuse.**
> *Find your brand's blind spots in AI answers — and prescribe what to fix, what to test, and what not to claim.*

Big Berlin Hack 2026 implementation repo. Track: **Peec AI (locked)**. Briefing: [../AGENT_BRIEFING.md](../AGENT_BRIEFING.md). Battle plan: [../BATTLE_PLAN.md](../BATTLE_PLAN.md).

## Status

**MVP pipeline complete.** Track locked, brand locked on **Nothing Phone** (the Invisible Champion: best position 2.4, 20% overall visibility, 4 of 5 topics with blind spots). Full 9-step pipeline executing end-to-end: Peec ingest, Tavily enrichment (40 live web sources), Gemini perception analysis, 3-signal gap classification (all 4 confirmed at STRONG evidence level), claim-checked evidence ledger, priority signals, competitor landscape, action plan, and interactive dashboard.

## Quick Start

```bash
uv sync --dev              # install dependencies
make run                   # run full pipeline (outputs: artifacts/local/)
make test                  # 172 tests
make lint                  # ruff check
```

Or step-by-step:

```bash
uv run presence-rx-ingest-peec --seed nothing-phone --out data/generated
uv run presence-rx-enrich-tavily --study data/generated/study_ssot.json --manifest data/generated/manifest.json --out data/generated --live --yes-confirm-billing
uv run presence-rx-run-mvp --generated-dir data/generated --dashboard-dir artifacts/local
```

## Tech Stack

- **Python 3.11+** with Pydantic (strict contracts), Typer (CLI), Rich (console)
- **google-genai 1.73.1** (Gemini API for perception analysis)
- **tavily-python 0.7.23** (public web evidence search)
- **Plotly.js** (client-side charts in dashboard)
- **Peec MCP** (source of truth for AI visibility data)

## Goal

Presence Verdict Pack via Peec MCP: multi-method analysis, claim checks, gap-type classifier, action brief.

**Primary tagline:** Diagnose. Prescribe. Refuse.
**Sub-tagline:** Find your brand's blind spots in AI answers.

## Solution Flow

```mermaid
flowchart TD
    A[Peec MCP Snapshot<br/>Nothing Phone] --> B[1. Ingest<br/>brand · topic · domain · URL · chat reports]
    B --> C[2. Tavily Enrichment<br/>public proof · editorial gaps]
    C --> D[3. Priority Signals<br/>intent fit · citation authority · evidence coverage<br/>signal alignment · action priority]
    D --> E[4. Competitor Landscape<br/>combined-metric ownership map]
    E --> F[5. Gap-Type Classifier<br/>perception · indexing · volume_frequency]
    F --> G[Claim Check<br/>3-signal verification · evidence levels · claims to avoid]
    G --> H[6. Action Brief<br/>PRESENCE_VERDICT · ACTION_BRIEF<br/>EVIDENCE_LEDGER · manifest]
    H --> I[Monitoring Setup<br/>create_prompt · create_tag · create_topic]
    I --> J[Lovable Webapp<br/>aligned with Peec design philosophy]
    H -.->|sneak peek<br/>concept only| K[/future-directions<br/>Channel Activation · Lift · Spend<br/>Static · Permissioned data outside repo/]

    classDef sharp fill:#fdcb6e,stroke:#e17055,stroke-width:2px,color:#2d3436
    classDef future fill:#dfe6e9,stroke:#636e72,stroke-dasharray: 5 5,color:#2d3436
    class F sharp
    class K future
```

The **gap-type classifier** (orange, step 5) is the new sharp moment: every blind spot carries a `perception` / `indexing` / `volume_frequency` label that triggers a different intervention class. The **Future Directions** node (dotted, step K) is concept-only on the public surface; the actual channel-activation prototype lives outside this repo (see [FUTURE_DIRECTIONS.md](docs/FUTURE_DIRECTIONS.md)).

## Core Artifacts

- `PRESENCE_VERDICT.md` - evidence-grade visibility diagnosis with gap-type classification
- `ACTION_BRIEF.md` - marketer actions grouped by intervention class, with "Claims To Avoid"
- `EVIDENCE_LEDGER.json` - every claim mapped to sources with blocked claims register
- `manifest.json` - snapshot metadata, taxonomy versions, pipeline summary, freshness

Optional artifacts: `pipeline_funnel.json`, `source_of_record.json`, `hero_cards.json`, `study_ssot.json`, `cluster_diagnostics.json`

## Partner Stack

- Gemini
- Tavily
- Lovable (dashboard surface)
- Peec MCP is the required track tool; eligibility toward the 3-partner minimum must be confirmed with organisers

## Submission

- Public GitHub repo + 2-minute video by Sunday 14:00 CEST.

## Multi-Agent

See [AGENTS.md](AGENTS.md) for lane assignments and coordination rules.

## Reusable Patterns

See [docs/ANALYTICS_PATTERNS_FOR_PEEC.md](docs/ANALYTICS_PATTERNS_FOR_PEEC.md) for public-safe analytics patterns: evidence ledger, claim checks, prompt universe routing, and the demo proof step.

See [docs/TREND_ECON_PATTERNS.md](docs/TREND_ECON_PATTERNS.md) for trend-analytics details: prompt clusters as trend objects, surge vs slow-burn, quality flags, SSOT, and strategic quadrants.

See [docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md](docs/PARENT_TOPIC_AND_UNSUPERVISED_PATTERNS.md) for parent-topic and unsupervised-topic mechanics: candidate topics, confidence filtering, parent themes, fallback topic sources, and coverage audits.

See [docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md](docs/CAMPAIGN_TAXONOMY_FOR_PEEC.md) for the campaign category/type hierarchy that turns prompt-cluster findings into marketer-facing plays.

See [docs/PLANNING_AND_MEASUREMENT_PATTERNS.md](docs/PLANNING_AND_MEASUREMENT_PATTERNS.md) for scenario-planning, reporting, readiness gates, visible assumptions, and sparse-data behavior.

See [docs/METHOD_GUARDRAILS_AND_EVIDENCE.md](docs/METHOD_GUARDRAILS_AND_EVIDENCE.md) for method ladders, evidence strength tiers, signal alignment, and claim language rules.

See [docs/TERMINOLOGY.md](docs/TERMINOLOGY.md) for the public terminology map used by the dashboard, markdown deliverables, and current documentation.

See [docs/ARTIFACT_CONTRACTS.md](docs/ARTIFACT_CONTRACTS.md) for the initial JSON artifact contracts.

See [docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md](docs/END_TO_END_BUILD_GUIDE_AND_STORYBOARD.md) for the complete build order, data flow, dashboard wireframes, and 2-minute demo storyboard.

See [docs/VALIDATION_REPORT.md](docs/VALIDATION_REPORT.md) for the original validation snapshot; use [docs/PROGRESS.md](docs/PROGRESS.md) and [docs/_STATUS.md](docs/_STATUS.md) for current validation status.

See **[docs/SCOPE_FINAL.md](docs/SCOPE_FINAL.md)** — the locked, rated scope for the build. 22 features across 4 tiers, 6-axis blind-spot model (Topic / Channel / Engine / Geography / Authority / Evidence), eligibility-critical lane explicit, build priority order with submission gates. **Read this first.**

See [docs/INTEGRATION_CHECKLIST.md](docs/INTEGRATION_CHECKLIST.md) for the active integration checklist (auth, brand strategy including custom-project workflow, partner wiring, pipeline build, submission gates).

See [docs/PEEC_MCP_EXPLORATION.md](docs/PEEC_MCP_EXPLORATION.md) for the verified MCP exploration output: project inventory, brand IDs, topic IDs, prompt summary, channel and engine breakdowns, gap URLs, metric definitions, and tool-to-pipeline mapping.

See [docs/FUTURE_DIRECTIONS.md](docs/FUTURE_DIRECTIONS.md) for the channel-activation roadmap (concept-only, sources the static `/future-directions` page in the Lovable webapp).

See [docs/design.md](docs/design.md) for the Peec AI design style guide (tokens captured 2026-04-25) that the Lovable webapp must follow.

See [docs/PUBLIC_SAFETY_CHECKLIST.md](docs/PUBLIC_SAFETY_CHECKLIST.md) before committing, pushing, recording, or making the repo public.
