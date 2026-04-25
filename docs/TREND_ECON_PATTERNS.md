# Trend Analytics Patterns For Peec

These patterns adapt prior trend analytics ideas into public-safe Peec product mechanics. Do not copy private data, internal paths, notebooks, client names, or proprietary code. Rebuild only the product ideas below for the hackathon.

## Best Ideas To Bring In

### 1. Prompt Clusters As Trend Objects

The trend repo turns noisy content streams into durable trend objects. Peec can do the same for LLM answer surfaces:

```text
Peec prompts / answers
  -> prompt clusters
  -> cluster diagnostics
  -> visibility surges and slow-burn background
  -> action brief
```

Peec mapping:

| Trend analytics concept | Peec concept |
| --- | --- |
| article/story | Peec prompt and answer observation |
| trend | prompt cluster |
| peak | visibility/perception surge |
| slow-burn | persistent baseline association |
| trust/intensity | evidence quality and answer strength |
| SSOT | study artifact table shared by CLI/UI/report |

### 1a. Micro Signals To Macro Narratives

Do not stop at a list of prompt observations. Convert micro signals into a higher-altitude narrative:

```text
individual Peec observations
  -> prompt cluster
  -> parent topic
  -> campaign type
  -> macro AI distribution narrative
  -> marketer "so what"
```

Useful macro narrative fields:

- `narrative_label`: short, board-readable theme.
- `supporting_clusters`: prompt clusters backing the narrative.
- `cultural_or_market_truth`: what the cluster suggests about buyer language or category expectations.
- `so_what`: why a marketer should care.
- `action_implication`: the next content, monitoring, or proof-building move.

Example:

```json
{
  "narrative_label": "Minimalist hardware is an identity gap, not a feature gap",
  "supporting_clusters": ["cluster:minimalist-hardware", "cluster:wireless-audio"],
  "cultural_or_market_truth": "AI answers anchor minimalist tech to Apple, regardless of the brand's design language.",
  "so_what": "The brand needs public minimalist-positioning content to claim category language it already lives.",
  "action_implication": "Publish minimalist-hardware content and monitor adjacent prompts after the next snapshot."
}
```

### 2. Three-Pass Clustering, Simplified

The full repo uses multi-stage clustering. For hackathon Peec, use the same shape but keep it deterministic and small:

1. Group prompts by intent: category, competitor, buying intent, problem-aware, analyst/review.
2. Sub-cluster by message theme: pricing, implementation, flexibility, trust, enterprise readiness.
3. Merge near-duplicates with guardrails so one marketing claim does not appear as three separate findings.

Useful output fields:

- `assignment_method`: `peec_cluster`, `rule_group`, `gemini_theme`, or `manual_seed`.
- `cluster_membership_score`: confidence that the prompt belongs in the cluster.
- `merge_reason`: why two prompt groups were merged.
- `merge_guardrail`: why a tempting merge was rejected.

### 3. Quality Flags Before Recommendations

Bring in the trend QA mindset. Each prompt cluster should be flagged before it can drive an action.

Peec flags:

- `flag_small`: too few Peec observations.
- `flag_low_membership`: weak prompt-cluster fit.
- `flag_incoherent`: prompts in the cluster do not share a clear theme.
- `flag_too_close`: overlaps with another cluster.
- `flag_over_split`: two clusters should probably be one finding.

Demo use:

- Show that a cluster is visible but flagged, so the action brief says "test this" rather than "claim this."

### 4. Surge Versus Slow-Burn

The trend repo separates spikes from slow-burn momentum. Peec can separate:

- `surge`: prompt clusters where the brand suddenly appears, disappears, or changes rank/perception.
- `slow_burn`: stable background association that should be reinforced or monitored.

Even without time-series access, this can be simulated from Peec snapshot slices:

- by model/provider
- by prompt type
- by funnel stage
- by competitor pair

Example fields:

```json
{
  "cluster_id": "cluster:minimalist-hardware",
  "zone": "slow_burn",
  "target_visibility": 0.06,
  "competitor_owner": "Apple",
  "dominant_association": "minimalist design (Apple-owned)",
  "recommended_move": "Publish minimalist hardware positioning content featuring transparent design"
}
```

### 5. SSOT For Dashboard And Reports

The trend repo's strongest operational pattern is a single source-of-truth table with prefixed derived fields. Peec should create one `study_ssot.json` that powers Markdown and any dashboard.

Recommended prefixes:

- `cluster_*` - prompt cluster identity and QA.
- `visibility_*` - mention/rank/share metrics from Peec.
- `perception_*` - Gemini-derived themes and missing associations.
- `evidence_*` - Tavily and Peec source coverage.
- `guardrail_*` - blocked/downgraded reasons.
- `action_*` - recommendation, owner, next prompt to monitor.

### 6. Strategic Quadrant

Bring in the trend strategic quadrant idea as a simple executive visual:

```text
                 high evidence
                      ^
                      |
    maintain          |       act now
                      |
low visibility -------+------- high visibility
                      |
    ignore            |       investigate
                      |
                 low evidence
```

Peec interpretation:

- `act now`: high evidence and meaningful visibility/perception gap.
- `maintain`: high evidence but no urgent gap.
- `investigate`: visible signal, weak evidence.
- `ignore`: weak signal and weak evidence.

### 7. Decision Bucket Routing

The strategic quadrant is a good chart, but a decision bucket is more directly actionable. Add a `decision_bucket` to every cluster and action.

Buckets:

- `act_now`: strong evidence and clear action. Lead with this.
- `test_next`: promising but needs one more evidence layer. Pilot this.
- `monitor`: signal exists but is noisy or incomplete. Watch this.
- `deprioritize`: low visibility and weak evidence. Skip for now.
- `block`: attractive claim that should not be used. Avoid this.

```json
{
  "cluster_id": "cluster:minimalist-hardware",
  "decision_bucket": "test_next",
  "why_this_bucket": "Visible identity gap, moderate evidence, missing public minimalist-positioning content.",
  "recommended_next_move": "Publish minimalist-hardware content and rerun the prompt cluster after the next snapshot.",
  "primary_gap": "MISSING_PROOF_ASSET"
}
```

Use the quadrant for the chart and the bucket for the action brief. The quadrant shows the landscape; the bucket tells the marketer what to do next.

### 8. Diagnostics In The Demo

The trend repo emphasizes diagnostics: dropped/merged peaks, thresholds used, dense ranks, coverage. Peec should expose similar diagnostics:

- prompt count per cluster
- evidence refs per claim
- method agreement count
- guardrail threshold used
- blocked claim count
- cluster rank within brand
- competitor owner per cluster

This gives the Peec project technical depth without building a heavy model.

## Suggested Hackathon Artifacts

Add these if implementation time allows:

- `study_ssot.json` - one row per prompt cluster/action finding.
- `cluster_diagnostics.json` - QA flags and merge decisions.
- `surge_slowburn.json` - zone labels for visibility/perception patterns.

Minimum implementation can still generate only:

- `prompt_universe.json`
- `EVIDENCE_LEDGER.json`
- `PRESENCE_VERDICT.md`
- `ACTION_BRIEF.md`
- `manifest.json`

But the language in the study should mention:

- prompt clusters
- quality flags
- slow-burn associations
- competitor-owned clusters
- guarded recommendations

## Pitch Upgrade

Use this framing:

> We adapted trend analytics to AI distribution. Instead of tracking article spikes, we track prompt clusters, competitor ownership, slow-burn associations, and evidence-backed actions across AI answer surfaces.

## Implementation Caution

Do not overbuild UMAP/HDBSCAN, stock enrichment, market returns, Spark, or peak-detection machinery for the hackathon. The Peec version should be lightweight and explainable:

- deterministic grouping first
- Gemini theme classification second
- simple confidence/guardrail thresholds
- visible evidence ledger
- Markdown artifacts before dashboard polish
