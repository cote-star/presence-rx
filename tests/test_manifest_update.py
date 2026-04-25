from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.ingest_peec import (
    build_artifacts,
    nothing_phone_seed,
    update_hero_cards_post_pipeline,
    update_manifest_post_pipeline,
    update_pipeline_funnel_post_pipeline,
)
from presence_rx.plan_prescriptions import build_prescription_plan


def _pipeline():
    seed = nothing_phone_seed()
    artifacts = build_artifacts(seed)
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    prescription = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)
    return artifacts, classification, ledger, prescription


def test_manifest_updates_confidence_counts() -> None:
    artifacts, classification, ledger, _ = _pipeline()
    updated = update_manifest_post_pipeline(
        artifacts.manifest, classification=classification, ledger=ledger,
    )
    # Without Gemini/Tavily the gaps are provisional/limited, not strong
    # But unclassified rows (stronghold) should be moderate
    assert updated.confidence_counts["moderate"] >= 1


def test_manifest_updates_pipeline_summary() -> None:
    artifacts, classification, ledger, _ = _pipeline()
    updated = update_manifest_post_pipeline(
        artifacts.manifest, classification=classification, ledger=ledger,
    )
    assert updated.pipeline_summary.evidence_gated == classification.summary.classified_gaps
    assert updated.pipeline_summary.actionable_recommendations == len(ledger.claims)


def test_manifest_adds_artifact_names() -> None:
    artifacts, classification, ledger, _ = _pipeline()
    updated = update_manifest_post_pipeline(artifacts.manifest, classification=classification)
    assert "gap_classification.json" in updated.artifacts
    assert "EVIDENCE_LEDGER.json" in updated.artifacts


def test_hero_cards_reflect_pipeline_results() -> None:
    artifacts, classification, ledger, _ = _pipeline()
    hero = update_hero_cards_post_pipeline(
        classification=classification, ledger=ledger,
    )
    assert hero.actionable_recommendations >= 0
    assert hero.blocked_claim_count == len(ledger.blocked_claims)
    assert hero.method_conflict_count == sum(
        1 for g in classification.classified_gaps
        if g.classification_status == "conflicted"
    )


def test_pipeline_funnel_extends_with_downstream_stages() -> None:
    artifacts, classification, ledger, prescription = _pipeline()
    updated = update_pipeline_funnel_post_pipeline(
        artifacts.pipeline_funnel,
        classification=classification,
        ledger=ledger,
        prescription=prescription,
    )
    stage_names = [s.stage for s in updated.stages]
    assert "evidence_gated" in stage_names
    assert "claims_generated" in stage_names
    assert "prescriptions_planned" in stage_names
    # Original stages preserved
    assert "raw_peec_topics" in stage_names
