# Artifact Contracts

Initial contracts for the Presence Verdict Pack. Keep these stable enough for the generator, CLI, and optional dashboard to share. Examples use the locked Nothing Phone project; cluster IDs and topic names match the real Peec topics in `PEEC_MCP_EXPLORATION.md`.

## `prompt_universe.json`

```json
{
  "brand": "Nothing Phone",
  "competitors": ["Apple", "Samsung"],
  "clusters": [
    {
      "cluster_id": "cluster:smartphone-design",
      "label": "Smartphone Design",
      "stage": "consideration",
      "prompt_type": "category",
      "prompts": [
        {
          "prompt_id": "prompt:001",
          "text": "best minimalist phone with transparent design",
          "source": "peec_mcp"
        }
      ]
    }
  ]
}
```

## `EVIDENCE_LEDGER.json`

```json
{
  "generated_at": "2026-04-25T12:00:00+02:00",
  "brand": "Nothing Phone",
  "claims": [
    {
      "claim_id": "claim:nothing-phone:startup-crm:001",
      "claim": "Nothing Phone is absent from Minimalist Hardware prompts despite being a minimalist brand. Apple owns the cluster.",
      "status": "directional",
      "cluster_id": "cluster:smartphone-design",
      "methods": ["peec_visibility", "gemini_perception", "tavily_public_evidence"],
      "evidence_refs": ["peec:prompt:001", "tavily:source:001"],
      "why_not_stronger": "Cluster has fewer than five Peec observations."
    }
  ],
  "evidence": [
    {
      "evidence_ref": "peec:prompt:001",
      "source_type": "peec_mcp",
      "summary": "Target brand mentioned after two competitors.",
      "url": null,
      "confidence": 0.74
    },
    {
      "evidence_ref": "tavily:source:001",
      "source_type": "tavily",
      "summary": "Public source used to validate competitor messaging language.",
      "url": "https://example.com",
      "confidence": 0.68
    }
  ]
}
```

## `manifest.json`

```json
{
  "brand": "Nothing Phone",
  "competitors": ["Apple", "Samsung"],
  "generated_at": "2026-04-25T12:00:00+02:00",
  "artifact_version": "0.1.0",
  "taxonomy_version": "2026-04-25-demo",
  "peec_snapshot_id": "demo-snapshot",
  "published": true,
  "sources": {
    "peec_mcp": {
      "snapshot_id": "demo-snapshot",
      "prompt_count": 0
    },
    "tavily": {
      "query_count": 0,
      "source_count": 0
    },
    "gemini": {
      "analysis_runs": 0
    },
    "lovable": {
      "dashboard_url": null
    }
  },
  "confidence_counts": {
    "actionable": 0,
    "directional": 0,
    "insufficient_evidence": 0,
    "blocked": 0
  },
  "quality_counts": {
    "strong": 0,
    "moderate": 0,
    "limited": 0,
    "blocked": 0
  },
  "unavailable_reason_counts": {
    "NO_PEEC_EVIDENCE": 0,
    "SPARSE_CLUSTER": 0,
    "TAXONOMY_FALLBACK": 0,
    "METHOD_CONFLICT": 0,
    "OVERCLAIM_RISK": 0
  },
  "freshness": {
    "status": "current",
    "generated_at": "2026-04-25T12:00:00+02:00",
    "newer_snapshot_available": false
  },
  "comparability": {
    "comparable_to_previous": true,
    "reason": null
  },
  "pipeline_summary": {
    "raw_prompts": 42,
    "clusters": 9,
    "evidence_gated": 5,
    "actionable_recommendations": 3
  },
  "artifacts": [
    "prompt_universe.json",
    "EVIDENCE_LEDGER.json",
    "PRESENCE_VERDICT.md",
    "ACTION_BRIEF.md",
    "pipeline_funnel.json",
    "source_of_record.json"
  ]
}
```

## `study_ssot.json`

Optional but recommended. One row per prompt cluster/finding, built for reuse by Markdown artifacts and the dashboard.

```json
{
  "rows": [
    {
      "cluster_id": "cluster:smartphone-design",
      "cluster_label": "Smartphone Design",
      "cluster_stage": "consideration",
      "cluster_prompt_type": "category",
      "cluster_prompt_count": 6,
      "cluster_membership_score": 0.82,
      "cluster_quality_flags": [],
      "visibility_target_share": 0.33,
      "visibility_target_avg_position": 4.2,
      "visibility_competitor_owner": "Apple",
      "perception_dominant_theme": "transparent design",
      "perception_missing_association": "minimalist hardware",
      "campaign_category": "Stakeholder & Culture",
      "campaign_type": "customer_experience",
      "visibility_topic": "Customer Service and Experience",
      "campaign_granularity": "type",
      "campaign_granularity_reason": "Enough observations exist for type-level recommendation.",
      "evidence_ref_count": 4,
      "guardrail_status": "directional",
      "guardrail_reason": "Peec and Tavily agree, but sample size is below actionable threshold.",
      "confidence_tier": "moderate",
      "recommendation_available": true,
      "unavailable_reason": null,
      "decision_bucket": "test_next",
      "decision_bucket_reason": "Visible prompt cluster, moderate evidence, missing product proof source.",
      "decision_bucket_primary_gap": "MISSING_PROOF_ASSET",
      "action_priority": 2,
      "action_recommendation": "Publish minimalist hardware positioning content featuring Nothing Phone's transparent design.",
      "action_next_move": "Create public proof for the missing association and rerun this prompt cluster.",
      "action_monitor_prompt": "best minimalist tech for a clean desk setup"
    }
  ]
}
```

## `cluster_diagnostics.json`

Optional diagnostic output adapted from trend QA.

```json
{
  "clusters": [
    {
      "cluster_id": "cluster:smartphone-design",
      "assignment_method": "rule_group+gemini_theme",
      "prompt_count": 6,
      "flag_small": false,
      "flag_low_membership": false,
      "flag_incoherent": false,
      "flag_too_close": false,
      "flag_over_split": false,
      "merge_decisions": [
        {
          "candidate_cluster_id": "cluster:mobile-ecosystem",
          "decision": "reject",
          "reason": "Different funnel stage and competitor owner."
        }
      ]
    }
  ]
}
```

## `parent_topics.json`

Optional but high leverage. Stores the parent-topic flow from candidate topics to accepted parent labels.

```json
{
  "observations": [
    {
      "observation_id": "peec:prompt:001",
      "cluster_id": "cluster:minimalist-hardware",
      "identified_topics": [
        {
          "topic": "minimalist hardware",
          "analysis": "Competitor is framed as easier to implement.",
          "brand_relevance_score": 0.76,
          "group_suggestions": {
            "buyer_friction": 0.82,
            "proof_gap": 0.71
          }
        }
      ],
      "classified_topics": [
        {
          "topic": "minimalist hardware",
          "parent_topic": "minimalist_hardware",
          "confidence_score": 0.74,
          "reasoning": "Prompt answers repeatedly mention transparent design and minimalist aesthetic alongside the brand."
        }
      ],
      "accepted_parent_topics": ["minimalist_hardware"],
      "fallback_topic_source": "final_parent_topic",
      "campaign_category": "Stakeholder & Culture",
      "campaign_type": "customer_experience",
      "visibility_topic": "Customer Service and Experience",
      "campaign_type_mapping_version": "2026-04-25-demo"
    }
  ]
}
```

## `topic_coverage_audit.json`

Optional coverage audit for the parent-topic pipeline.

```json
{
  "prompt_observations": 24,
  "with_identified_topics": 21,
  "with_classified_topics": 16,
  "with_final_parent_topics": 13,
  "using_fallback_topics": 8,
  "parent_topic_conversion_rate": 0.62,
  "top_missing_parent_themes": ["enterprise_trust", "pricing_and_packaging"]
}
```

## `method_comparison.json`

Optional method-agreement view.

```json
{
  "claims": [
    {
      "claim_id": "claim:nothing-phone:implementation:001",
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

## `surge_slowburn.json`

Optional view for the demo narrative. If Peec provides time slices, use them directly. If not, derive zones from model/provider, prompt type, or funnel-stage slices and label that clearly.

```json
{
  "zones": [
    {
      "cluster_id": "cluster:wireless-audio",
      "zone": "slow_burn",
      "basis": "cross_prompt_snapshot",
      "target_visibility": 0.42,
      "competitor_owner": "Apple",
      "dominant_association": "transparent design",
      "recommended_move": "Reinforce minimalist positioning with transparent-hardware proof."
    }
  ]
}
```

## `scenario_assumptions.json`

Optional contract for a scenario planner or dashboard card. Use this when the demo compares actions or prompt-cluster scenarios.

```json
{
  "scenarios": [
    {
      "scenario_id": "scenario:implementation-support:001",
      "cluster_id": "cluster:minimalist-hardware",
      "campaign_type": "customer_experience",
      "assumptions": [
        {
          "assumption_source": "peec_snapshot",
          "assumption_text": "Nothing Phone trails Apple on minimalist-hardware prompts in the current Peec snapshot.",
          "confidence_tier": "moderate",
          "evidence_refs": ["peec:prompt:001"],
          "unavailable_reason": null
        }
      ],
      "recommendation_available": true,
      "allowed_language": "Test this action."
    }
  ]
}
```

## `stage_readiness.json`

Optional workflow artifact that shows whether the study is ready to publish.

```json
{
  "stages": [
    {
      "stage_id": "prompt_universe",
      "stage_status": "ready",
      "done_definition": "Brand, competitors, prompt clusters, and prompt sources are declared.",
      "blocking_reason": null,
      "artifact_refs": ["prompt_universe.json"]
    },
    {
      "stage_id": "action_brief",
      "stage_status": "blocked",
      "done_definition": "Every action has Peec evidence, campaign taxonomy, confidence tier, and monitor prompt.",
      "blocking_reason": "One recommendation has no Peec evidence ref.",
      "artifact_refs": ["ACTION_BRIEF.md", "EVIDENCE_LEDGER.json"]
    }
  ]
}
```

## `pipeline_funnel.json`

Shows record counts at each pipeline stage with expected vs unexpected drops. Gives the demo a strong "why only three recommendations?" answer.

```json
{
  "stages": [
    {
      "stage": "raw_prompts",
      "input_count": 42,
      "output_count": 42,
      "expected_drop_count": 0,
      "unexpected_drop_count": 0,
      "drop_reason": null
    },
    {
      "stage": "clustered_prompts",
      "input_count": 42,
      "output_count": 9,
      "expected_drop_count": 33,
      "unexpected_drop_count": 0,
      "drop_reason": "PROMPTS_GROUPED_INTO_CLUSTERS"
    },
    {
      "stage": "topic_classified",
      "input_count": 9,
      "output_count": 7,
      "expected_drop_count": 2,
      "unexpected_drop_count": 0,
      "drop_reason": "NO_PARENT_TOPIC_ACCEPTED"
    },
    {
      "stage": "evidence_gated",
      "input_count": 7,
      "output_count": 5,
      "expected_drop_count": 2,
      "unexpected_drop_count": 0,
      "drop_reason": "INSUFFICIENT_EVIDENCE"
    },
    {
      "stage": "actionable_recommendations",
      "input_count": 5,
      "output_count": 3,
      "expected_drop_count": 1,
      "unexpected_drop_count": 1,
      "drop_reason": "QUALITY_GATES"
    }
  ]
}
```

## `source_of_record.json`

Defines which source owns each metric. Prevents a Gemini narrative from being mistaken for Peec evidence.

```json
{
  "field_ownership": {
    "visibility_rank": "peec",
    "visibility_share": "peec",
    "competitor_owner": "peec_derived",
    "perception_theme": "gemini_analysis",
    "missing_association": "gemini_analysis",
    "public_proof": "tavily",
    "campaign_type": "taxonomy_mapping",
    "parent_topic": "gemini_classification",
    "guardrail_status": "derived_rules",
    "decision_bucket": "derived_rules"
  }
}
```

## `hero_cards.json`

Top-level evidence health cards for the dashboard. Show these before the findings table.

```json
{
  "guardrail_pass_rate_pct": 67,
  "cluster_pass_rate_pct": 50,
  "actionable_recommendations": 3,
  "blocked_claims": 2,
  "method_conflict_count": 1,
  "pipeline_input_prompts": 42,
  "pipeline_output_actions": 3
}
```

## Shared Field Extensions

These fields can be added to claims, clusters, or SSOT rows as needed.

### Publication Gate

Clusters and claims must pass a publication gate before they can appear in executive-facing outputs.

```json
{
  "publication_status": "directional_with_caveat",
  "publish_gate": {
    "decision": "allow_with_caveat",
    "passed_checks": ["has_peec_ref", "has_public_source", "has_parent_topic"],
    "failed_checks": ["low_prompt_count"],
    "blocked_reason": null
  }
}
```

Statuses: `publishable`, `directional_with_caveat`, `diagnostics_only`, `blocked`.

### Assumption Bundle

Attach to every recommendation and scenario so the output is never free-floating.

```json
{
  "assumption_bundle": {
    "peec_snapshot_id": "snapshot:demo",
    "artifact_version": "0.1.0",
    "topic_taxonomy_version": "2026-04-25-demo",
    "prompt_universe_version": "demo-v1",
    "excluded_slices": [
      { "slice": "enterprise-buying-prompts", "reason": "SPARSE_CLUSTER" }
    ],
    "display_caveat": "Based on AI answer visibility and public evidence, not causal proof."
  }
}
```

### Freshness And Comparability

Track whether the study is current and whether it can be compared to prior runs.

```json
{
  "freshness": {
    "status": "current",
    "generated_at": "2026-04-25T12:00:00+02:00",
    "newer_snapshot_available": false
  },
  "comparability": {
    "comparable_to_previous": false,
    "reason": "TOPIC_TAXONOMY_CHANGED"
  }
}
```

### Decision Bucket

Route findings into operational buckets. More actionable than a quadrant alone.

```json
{
  "decision_bucket": "test_next",
  "why_this_bucket": "Visible prompt cluster, moderate evidence, missing product proof source.",
  "recommended_next_move": "Create public proof for the missing association and rerun.",
  "primary_gap": "MISSING_PROOF_ASSET"
}
```

Buckets: `act_now`, `test_next`, `monitor`, `deprioritize`, `block`.

### Explicit Nulls

Missing data uses `null` with a sibling reason, never silent blanks or zeros.

```json
{
  "competitor_owner": null,
  "competitor_owner_unavailable_reason": "NO_CLEAR_OWNER",
  "public_proof_url": null,
  "public_proof_url_unavailable_reason": "NO_PUBLIC_SOURCE_FOUND"
}
```

### Evidence Power

Honest statement of what the available data can and cannot detect.

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

### Review Override

When a hackathon shortcut is used, make it visible and bounded.

```json
{
  "override": {
    "used": true,
    "override_type": "demo_directional_allowance",
    "rationale": "Public evidence and two methods agree, but Peec count is below threshold.",
    "expires_after": "hackathon_demo"
  }
}
```

### Narrative Fallback Cards

If the LLM fails to generate clean actions, produce labeled fallback cards.

```json
{
  "narrative_cards": [
    {
      "action_type": "Monitor",
      "body": "Cluster is visible but underpowered.",
      "generation_mode": "fallback_template"
    }
  ],
  "narrative_generation_status": "fallback_used"
}
```

### Blocked Claims Register

Attractive findings explicitly blocked before reaching executive copy.

```json
{
  "blocked_claims": [
    {
      "claim": "Nothing Phone is the go-to minimalist tech brand.",
      "blocked_reason": "METHOD_CONFLICT",
      "safe_rewrite": "Nothing Phone dominates Smartphone Design but is invisible in adjacent topics like Minimalist Hardware.",
      "next_evidence_to_collect": "Publish minimalist hardware content and rerun the prompt cluster after the next snapshot."
    }
  ]
}
```

## Guardrail Function Contract

Inputs:

- Peec observation count for the cluster.
- Method agreement count across Peec, Gemini, Tavily.
- Conflict flag.

Output status:

- `actionable`: at least 5 Peec observations, at least 2 methods agree, no conflict.
- `directional`: 2-4 Peec observations, or 1 strong method, no hard conflict.
- `insufficient_evidence`: fewer than 2 Peec observations or missing Peec support.
- `blocked`: contradictory evidence, unsupported high-stakes claim, or claim would overstate the data.

The demo must include at least one `directional`, `insufficient_evidence`, or `blocked` claim.
