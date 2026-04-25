# Prior Analytics Patterns To Rebuild For Peec

This repo must stay public-safe: no private credentials, private datasets, internal paths, client names, or proprietary code. The useful import is the operating pattern: evidence-backed packs with clear routing, claim boundaries, and proof steps.

## Product Upgrades To Bring In

### 1. Evidence-Backed Study Pack

Turn the Peec output into a sealed study pack, not just a generated report.

Artifacts:

- `PRESENCE_VERDICT.md` - narrative diagnosis.
- `ACTION_BRIEF.md` - executive action plan.
- `EVIDENCE_LEDGER.json` - every claim mapped to Peec, Tavily, and Gemini evidence.
- `manifest.json` - source counts, confidence tiers, generated artifacts, and freshness timestamp.

Demo value:

- Pick one recommendation and jump from recommendation -> claim -> evidence row -> source reference.
- This makes the marketing output feel auditable instead of generic.

### 2. Claim Ledger And Guardrails

Every generated claim should carry a status:

- `actionable` - enough Peec observations and at least two methods agree.
- `directional` - signal exists but coverage or method agreement is incomplete.
- `insufficient_evidence` - too few observations, no Peec support, or conflicting sources.
- `blocked` - attractive claim that should not be used in the action brief.

Minimum fields:

```json
{
  "claim_id": "claim:nothing-phone:minimalist-hardware:001",
  "claim": "Nothing Phone is absent from Minimalist Hardware prompts despite being a minimalist brand.",
  "status": "directional",
  "cluster_id": "cluster:minimalist-hardware",
  "methods": ["peec_visibility", "gemini_perception", "tavily_public_evidence"],
  "evidence_refs": ["peec:prompt:014", "tavily:source:003"],
  "why_not_stronger": "Only three Peec observations in this cluster."
}
```

Demo value:

- Show one claim being downgraded or blocked.
- Judges see discipline before storytelling.

### 3. Prompt Universe Routing

Borrow the context-pack idea of task-scoped navigation. For Peec, route all analysis through a visible prompt universe before writing recommendations.

Suggested prompt groups:

- `category` - "best CRM for startups"
- `competitor` - "Nothing Phone vs Apple"
- `buying_intent` - "I need a CRM that..."
- `problem_aware` - "CRM that does not require an admin"
- `analyst_review` - "CRM market 2026"

Minimum fields:

```json
{
  "cluster_id": "cluster:wireless-audio",
  "stage": "consideration",
  "prompt_type": "problem_aware",
  "prompts": [],
  "target_brand": "Nothing Phone",
  "competitors": ["Apple", "Samsung"]
}
```

Demo value:

- Recommendations are visibly grounded in buying-journey prompts.
- Avoids a generic "content ideas" feel.

### 4. Three-Track Framing For The Pitch

Use a three-track framing, adapted to AI distribution:

- `Navigation` - which prompt clusters matter and which to ignore.
- `Harness` - how LLM answer surfaces describe the brand today.
- `Engineering` - repeatable evidence ledger, manifest, and guardrail rules.

Pitch line:

> Peec shows where the brand appears. This pack turns that into an auditable action system: prompt navigation, model-surface diagnosis, and evidence-backed marketing moves.

### 5. Proof Step In The Demo

The demo should not stop at the polished brief. It should include a proof step:

1. Open `ACTION_BRIEF.md`.
2. Pick the top recommended move.
3. Open `PRESENCE_VERDICT.md` to the related verdict.
4. Open `EVIDENCE_LEDGER.json` to show Peec/Tavily/Gemini evidence refs.
5. Show one blocked claim so the system is not blindly optimistic.

This is the strongest reusable pattern: narrative plus proof, not narrative alone.

## What Not To Bring In

- Do not copy private project text into product artifacts.
- Do not depend on private repositories at runtime.
- Do not use private credentials, private connectors, client names, or private datasets.
- Do not claim Peec findings are statistically definitive unless the prompt coverage supports it.

## Peec MVP Shape

Protect this vertical slice:

```text
Peec MCP snapshot
  -> prompt clusters
  -> method scores
  -> Tavily evidence appendix
  -> Gemini analysis
  -> claim ledger + guardrails
  -> PRESENCE_VERDICT.md
  -> ACTION_BRIEF.md
  -> manifest.json
```

If there is time for UI, the dashboard should show:

- prompt cluster coverage
- competitor ownership
- top action brief items
- blocked/downgraded claims
- evidence refs for the selected claim

## Highest-Leverage Addition

Add `EVIDENCE_LEDGER.json` and make it part of the demo. It adds technical depth, partner-tech proof, and trustworthiness without requiring a large frontend.
