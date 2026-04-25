# Method Guardrails And Evidence Rules

These rules keep the Peec study from overclaiming. They adapt general evidence-quality and method-comparison patterns into public-safe hackathon mechanics.

## Method Ladder

Use the strongest available evidence path and label the claim accordingly:

| method | use when | allowed language |
| --- | --- | --- |
| `peec_confirmed` | Peec observations are sufficient and agree with Gemini/Tavily evidence. | "Prioritize this action." |
| `method_consensus` | Two methods agree, but Peec coverage is moderate. | "Test this action." |
| `fallback_directional` | Peec is thin, but public evidence and Gemini analysis suggest a plausible direction. | "Explore this hypothesis." |
| `insufficient_evidence` | Coverage is too sparse, contradictory, or not tied to Peec. | "Do not claim this yet." |

## Global Gating Rules

Before a recommendation enters `ACTION_BRIEF.md`, it must have:

- an explicit prompt cluster
- a competitor owner or clear no-owner state
- at least one Peec evidence ref
- a parent topic or declared fallback topic source
- a campaign type or declared campaign-category fallback
- a guardrail status
- a monitoring prompt

If any of these are missing, keep it in the study appendix instead of the action brief.

Before any scenario output is displayed, it must also show:

- `assumption_text`
- `assumption_source`
- `confidence_tier`
- `evidence_refs`
- `unavailable_reason` when the recommendation is disabled or downgraded

Do not hide missing data. Use stable unavailable-reason codes such as `NO_PEEC_EVIDENCE`, `SPARSE_CLUSTER`, `TAXONOMY_FALLBACK`, `METHOD_CONFLICT`, or `OVERCLAIM_RISK`.

## Three-Field Separation

Distinguish between input eligibility, evidence strength, and final publication status. A finding can have moderate evidence but still be held for monitoring if freshness, comparability, or source-of-record checks fail.

| field | purpose | values |
| --- | --- | --- |
| `input_gate_status` | Can this finding enter the analysis? | `passed`, `failed`, `skipped` |
| `evidence_tier` | How strong is the evidence? | `strong`, `moderate`, `limited`, `blocked` |
| `publication_status` | Can this appear in executive output? | `publishable`, `directional_with_caveat`, `diagnostics_only`, `blocked` |

```json
{
  "input_gate_status": "passed",
  "evidence_tier": "moderate",
  "publication_status": "diagnostics_only",
  "publication_reason": "Peec and public evidence agree, but prompt count is below strong threshold."
}
```

A finding with `evidence_tier = "moderate"` and `publication_status = "diagnostics_only"` stays in the study but does not reach the action brief.

## Evidence Strength Tiers

| tier | rule |
| --- | --- |
| `strong` | 5+ Peec observations, 2+ methods agree, no conflict, parent topic accepted. |
| `moderate` | 2-4 Peec observations, 2 methods agree, no hard conflict. |
| `limited` | 1 Peec observation or only fallback topic support. |
| `blocked` | No Peec support, contradictory evidence, or claim is stronger than the data. |

For compatibility, `high`, `medium`, and `low` can be emitted as display aliases for `strong`, `moderate`, and `limited`.

## Method Agreement

Track agreement across:

- `peec_visibility`: target brand appears, rank, share, competitor owner.
- `gemini_perception`: themes, missing associations, likely buyer interpretation.
- `tavily_public_evidence`: public proof, competitor messaging, proof gaps.
- `topic_taxonomy`: accepted parent topic or fallback topic source.
- `campaign_taxonomy`: campaign type or campaign-category fallback.

Agreement score:

- `3-4`: strong alignment
- `2`: directional alignment
- `0-1`: weak or unsupported

## Claim Language Rules

- `strong`: "Prioritize", "lead with", "monitor weekly."
- `moderate`: "Test", "pilot", "validate."
- `limited`: "Explore", "watch", "collect more evidence."
- `blocked`: "Do not claim", "do not use in outbound messaging."

Do not use causal language. The study is about AI answer visibility and evidence-backed marketing actions, not proof that an action will change future model behavior.

Avoid "optimal" language unless the artifact is clearly labeled as a scenario and all assumptions are visible. Prefer "recommended next test" or "highest-supported action in this snapshot."

## Recommendation Availability

Track whether each action is actually available:

```json
{
  "recommendation_available": false,
  "unavailable_reason": "SPARSE_CLUSTER",
  "next_evidence_to_collect": "Run more implementation-support prompts across competitor and category prompt types."
}
```

Unavailable recommendations can still be valuable in the demo when they show the exact evidence gap.

## Method Comparison Artifact

Add `method_comparison.json` if time allows:

```json
{
  "claims": [
    {
      "claim_id": "claim:nothing-phone:minimalist-hardware:001",
      "cluster_id": "cluster:minimalist-hardware",
      "peec_visibility": "directional",
      "gemini_perception": "supports",
      "tavily_public_evidence": "supports",
      "topic_taxonomy": "accepted_parent_topic",
      "campaign_taxonomy": "campaign_type",
      "agreement_score": 3,
      "evidence_tier": "strong",
      "recommendation_available": true,
      "unavailable_reason": null,
      "allowed_language": "Prioritize this action."
    }
  ]
}
```

## Evidence Power

Each cluster should carry an honest statement of what the available data can detect. Weak samples are not treated as negative proof.

```json
{
  "evidence_power": {
    "minimum_prompt_count_for_strong": 5,
    "actual_prompt_count": 2,
    "power_label": "underpowered",
    "interpretation": "Absence of visibility is not evidence of absence."
  }
}
```

Power labels: `strong`, `adequate`, `underpowered`, `insufficient`.

## Claim Blocking Register

Attractive findings must be explicitly blocked before they reach executive copy. The blocked claim and reason are preserved for audit and for the demo proof step.

```json
{
  "blocked_claims": [
    {
      "claim": "The target brand owns implementation support.",
      "blocked_reason": "METHOD_CONFLICT",
      "safe_rewrite": "Implementation support appears as a contested prompt cluster.",
      "next_evidence_to_collect": "Run more implementation prompts and find public proof."
    }
  ]
}
```

Add a `CLAIMS_TO_AVOID` section in `ACTION_BRIEF.md` sourced from this register. In the demo, show one claim being blocked - this is more credible than showing only positive recommendations.

## Dashboard Panels

If a UI is built, start with four hero cards before the findings table:

```json
{
  "hero_cards": {
    "guardrail_pass_rate_pct": 67,
    "cluster_pass_rate_pct": 50,
    "actionable_recommendations": 3,
    "method_conflict_count": 2
  }
}
```

Then prioritize these panels:

- Executive snapshot: best-supported actions plus blocked count.
- Evidence readiness: prompt count, source count, method agreement, freshness.
- Method agreement: Peec vs Gemini vs Tavily vs taxonomy.
- Source-of-record map: which source owns each metric.
- Funnel audit: prompts to clusters to claims to actions.
- Blocked claims: strong-looking statements that were downgraded or blocked, with exact reason.
- Prompt cluster table: owner, parent topic, confidence, decision bucket, action.

## Demo Moment

Show a large-sounding claim that fails the method ladder. Then show the system downgrading it to "collect more evidence" or "do not claim." This is more credible than showing only positive recommendations.
