# Parent Topic And Unsupervised Patterns For Peec

These are public-safe patterns adapted for the Peec challenge. They should be rebuilt from Peec MCP, Tavily, Gemini, and public web evidence only.

## Why This Helps

Most AI-marketing demos will generate recommendations directly from visibility data. The stronger path is a two-stage topic system:

```text
Peec answer observations
  -> unsupervised candidate topics
  -> parent topic classification
  -> confidence-filtered labels
  -> action brief and evidence ledger
```

That gives the study a defensible hierarchy:

- raw answer/prompt observations
- emergent topics
- parent marketing themes
- action recommendations
- blocked or downgraded claims

## Pattern 0: Start With Explicit Definitions

Before tagging, define what the system is trying to find:

- target brand
- competitors
- campaign/action hypothesis
- prompt cluster definition
- parent-topic taxonomy version
- campaign-taxonomy version

Do not tag against a vague theme like "brand relevance" alone. The association should be tied to a defined campaign/action hypothesis or prompt cluster.

## Pattern 1: Identify Candidate Topics First

For each Peec observation, extract candidate topic objects before assigning final labels.

Suggested fields:

```json
{
  "topic": "minimalist hardware",
  "analysis": "The answer frames the competitor as easier to implement than the target brand.",
  "brand_relevance_score": 0.76,
  "is_relevant": true,
  "group_suggestions": {
    "buyer_friction": 0.82,
    "proof_gap": 0.71,
    "competitor_advantage": 0.68
  }
}
```

Peec use:

- Extract from Peec MCP answer text and competitor positioning.
- Use Gemini to propose candidate topics and group suggestions.
- Keep the topic even if it is later filtered out, but mark why it did not reach the action brief.

## Pattern 2: Filter Before Classification

Do not classify every candidate. Apply cheap filtering first:

- `brand_relevance_score >= 0.4`
- at least one group suggestion above `0.4`
- Peec evidence exists for the prompt cluster
- keyword or prompt-cluster match when available

Peec use:

- This prevents noisy Peec answers from becoming polished recommendations.
- It gives the demo a clear "why this finding was blocked" moment.
- It saves stronger model calls for the reduced set that might actually affect the action brief.

Avoid global thresholds as absolute truth. Thresholds should be visible and adjustable by prompt cluster or brand context.

## Pattern 3: Classify Into Parent Themes

Classify relevant candidate topics into stable parent marketing themes.

Recommended parent themes for Nothing Phone:

- `category_entry_points`
- `competitor_positioning`
- `design_distinctiveness`
- `minimalist_category_language`
- `transparent_hardware`
- `ecosystem_integration`
- `audio_credibility`
- `consumer_innovation`
- `mobile_design_authority`
- `monitoring_watchlist`

The themes should be configurable in a local JSON file so the demo can show the taxonomy.

Parent topics should also map upward into campaign taxonomy fields when possible:

- `visibility_topic`
- `campaign_type`
- `campaign_category`

See [CAMPAIGN_TAXONOMY_FOR_PEEC.md](CAMPAIGN_TAXONOMY_FOR_PEEC.md) for the campaign hierarchy and fallback rules.

## Pattern 4: Extract Valid Topic Names

Classification output should include per-theme confidence and reasoning. Only accepted labels should flow into final artifacts.

Suggested classification shape:

```json
{
  "topic": "minimalist hardware",
  "group": [
    {
      "name": "buyer_friction",
      "classification": [
        {
          "category_confidence_scores": {
            "minimalist_hardware": {
              "reasoning": "Prompt answers repeatedly mention transparent design and minimalist aesthetic alongside the brand.",
              "confidence_score": 0.74
            },
            "design_distinctiveness": {
              "reasoning": "Some answers reference distinctive design but do not name the brand directly.",
              "confidence_score": 0.31
            }
          }
        }
      ]
    }
  ]
}
```

Accepted labels:

- include labels at or above `0.4`
- dedupe labels per prompt observation
- flatten to one row per prompt observation and parent topic

If multiple tags are evaluated in one call, emit one decision per tag:

```json
{
  "tag_id": "tag:minimalist_hardware",
  "label": true,
  "rationale": "The answer frames the brand around transparent and minimalist hardware design.",
  "confidence_score": 0.74,
  "exclusivity_group": "buyer_friction"
}
```

The tag contract makes it possible to compare overlapping concepts without hiding uncertainty.

## Pattern 5: Use Fallback Topic Sources

When the strongest artifact layer is missing, fall back in a declared order:

1. `final_parent_topic` - confidence-filtered parent topic.
2. `classified_topic` - classified but not accepted into final parent labels.
3. `identified_topic` - unsupervised candidate topic.
4. `none` - no topic payload available.

Peec use:

- `ACTION_BRIEF.md` should prefer final parent topics.
- `PRESENCE_VERDICT.md` can include classified or identified fallback topics as directional signals.
- `EVIDENCE_LEDGER.json` should record which source tier backed each recommendation.

## Pattern 6: Topic Coverage Audit

Create a small coverage audit so missing topic evidence is visible.

Suggested metrics:

- prompt observations
- observations with identified topics
- observations with classified topics
- observations with final parent topics
- observations mapped to campaign type
- observations rolled up to campaign category fallback
- observations using fallback topics
- parent-topic conversion rate
- top missing parent themes

This is useful in the demo because it shows the system is honest about coverage gaps.

## Pattern 7: Taxonomy Versioning And Comparability

Store `topic_taxonomy_version` and `campaign_type_mapping_version` with every run. If a taxonomy changes between runs, mark the outputs as not directly comparable.

```json
{
  "topic_taxonomy_version": "2026-04-25-demo",
  "campaign_type_mapping_version": "2026-04-25-demo",
  "comparability": {
    "comparable_to_previous": false,
    "reason": "TOPIC_TAXONOMY_CHANGED"
  }
}
```

This prevents stale comparisons when parent themes are added, removed, or reorganized. In the demo, it shows the system is aware that its own definitions evolve.

If a parent-topic mapping changes, avoid comparing current cluster counts to older runs without noting the version change.

## Peec MVP Implementation

Minimal files:

- `parent_topics.json`
- `topic_coverage_audit.json`
- `study_ssot.json`

Minimal flow:

```text
Peec observations
  -> identify candidate topics
  -> filter by brand relevance and group confidence
  -> classify into parent themes
  -> flatten/dedupe final labels
  -> choose fallback topic source
  -> feed study and action brief
```

## Demo Moment

Show one recommendation that uses a final parent topic, then show a second tempting recommendation blocked because it only has an unsupervised candidate topic and no classified parent theme.
