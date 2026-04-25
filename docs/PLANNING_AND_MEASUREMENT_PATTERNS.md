# Planning And Measurement Patterns For Peec

These patterns turn Peec visibility observations into a more useful marketer workflow. They are intentionally generic and public-safe: keep only the product mechanics, not source names, internal page titles, private examples, or proprietary infrastructure details.

## Core Product Shape

Peec should support two connected views:

- `scenario_planner` - forward-looking what-if analysis for prompt clusters, campaign types, and evidence-backed content moves.
- `reporting_dashboard` - backward-looking summary of where the brand appears, where competitors own the answer, and which claims have enough evidence to act on.

The planner should not output a recommendation unless it can show:

- the prompt cluster being changed
- the evidence source behind the assumption
- the campaign type or fallback category
- the confidence tier
- the reason any recommendation is unavailable or downgraded

## Readiness Gates

Use gates to stop the demo from overclaiming:

| gate | pass condition | fail behavior |
| --- | --- | --- |
| `evidence_gate` | At least one Peec evidence ref exists for the finding. | Move to appendix or mark `insufficient_evidence`. |
| `taxonomy_gate` | Parent topic and campaign type are assigned, or fallbacks are declared. | Keep the claim directional and record fallback reason. |
| `quality_gate` | Evidence tier is `strong` or `moderate`. | Disable optimization/recommendation language. |
| `assumption_gate` | Scenario assumptions are visible in the artifact. | Do not show scenario output. |
| `review_gate` | The claim survives contradiction and overstatement checks. | Mark `blocked` with a concrete reason. |

This lets the product say "not enough evidence yet" as a feature, not a failure.

## Visible Assumptions

Every scenario or action card should include:

- `assumption_source`: `peec_snapshot`, `public_evidence`, `model_analysis`, or `manual_seed`.
- `assumption_text`: short human-readable assumption.
- `confidence_tier`: `strong`, `moderate`, or `limited`.
- `evidence_refs`: refs into `EVIDENCE_LEDGER.json`.
- `unavailable_reason`: null when available; otherwise a stable code.

Recommended unavailable reason codes:

- `NO_PEEC_EVIDENCE`
- `SPARSE_CLUSTER`
- `TAXONOMY_FALLBACK`
- `METHOD_CONFLICT`
- `UNPUBLISHED_SNAPSHOT`
- `OVERCLAIM_RISK`

## Workflow Stages

The product should scaffold thinking before it generates the polished brief:

```text
define brand and competitors
  -> define prompt universe and campaign/action hypothesis
  -> collect Peec observations
  -> extract topics and campaign taxonomy
  -> compare methods
  -> review gates
  -> publish study/action brief
```

Useful stage fields:

- `stage_id`
- `stage_status`: `not_started`, `in_progress`, `ready`, `blocked`
- `done_definition`
- `blocking_reason`
- `artifact_refs`

The workflow does not need to be strictly linear. If a user revises the prompt universe, downstream artifacts should carry a new `artifact_version` and note what changed.

## Normalization Rule

Compare visibility relative to the brand's own prompt universe before making cross-competitor claims. A prompt cluster can be meaningfully weak for one brand even if the absolute mention count looks acceptable.

Suggested language:

- Use "below brand baseline" when comparing against the brand's own prompts.
- Use "competitor-owned in this cluster" only when Peec evidence shows the competitor is repeatedly present or higher ranked.
- Avoid "optimal", "will improve", or causal language.

## Sparse Data Behavior

Sparse data should degrade gracefully:

- Type-level campaign action unavailable -> roll up to campaign category.
- Parent topic unavailable -> use classified topic or identified topic with a fallback flag.
- Scenario recommendation unavailable -> show the missing evidence and the next prompt to monitor.
- Conflicting methods -> keep the observation in the study, but block the action.

## UX Priorities

If a dashboard is built, prioritize:

- evidence cards with quality tier and unavailable reasons
- prompt cluster table with competitor owner and campaign type
- scenario cards with visible assumptions
- blocked-claims panel
- artifact manifest with versions and snapshot ids

Avoid burying the guardrails in a footnote. The credibility of the demo comes from showing the checks.

