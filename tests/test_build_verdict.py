from presence_rx.build_competitor_landscape import build_competitor_landscape
from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.build_verdict import build_presence_verdict
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed
from presence_rx.synthesize_gemini_analysis import build_synthetic_gemini_analysis

POISON = "POISON_TAVILY_SNIPPET_DO_NOT_EMBED"


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def test_verdict_contains_expected_sections() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)

    content = build_presence_verdict(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
    )
    assert "# Presence Verdict: Nothing Phone" in content
    assert "## Executive Summary" in content
    assert "## Topic Diagnosis" in content
    assert "## Gap-Type Summary" in content
    assert "## Methodology" in content


def test_verdict_contains_real_topic_data() -> None:
    artifacts = _artifacts()
    content = build_presence_verdict(artifacts.study_ssot, artifacts.manifest)
    assert "Smartphone Design" in content
    assert "Minimalist Hardware" in content
    assert "Wireless Audio" in content
    assert "72%" in content  # Smartphone Design visibility
    assert "6%" in content   # Minimalist Hardware visibility


def test_verdict_does_not_contain_raw_snippets() -> None:
    artifacts = _artifacts()
    content = build_presence_verdict(artifacts.study_ssot, artifacts.manifest)
    assert POISON not in content
    assert "raw" not in content.lower() or "raw_prompts" in content.lower()


def test_verdict_evidence_has_proof_blocks() -> None:
    artifacts = _artifacts()
    gemini = build_synthetic_gemini_analysis(artifacts.study_ssot, artifacts.manifest)
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest, gemini=gemini,
    )
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    landscape = build_competitor_landscape(
        artifacts.study_ssot, artifacts.manifest, classification=classification,
    )

    content = build_presence_verdict(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
        gemini=gemini,
        landscape=landscape,
    )
    assert "**What users ask:**" in content
    assert "**Who currently owns the answer:**" in content
    assert "**What proof exists:**" in content
    assert "**What claim is unsafe:**" in content
    assert "**What the brand should say instead:**" in content
    assert "Evidence refs:" not in content
