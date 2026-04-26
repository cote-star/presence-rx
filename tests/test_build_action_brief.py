from presence_rx.build_action_brief import build_action_brief
from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed
from presence_rx.plan_prescriptions import build_prescription_plan

POISON = "POISON_TAVILY_SNIPPET_DO_NOT_EMBED"


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def test_action_brief_contains_expected_sections() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    prescription = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)

    content = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
        prescription=prescription,
    )
    assert "# Action Brief: Nothing Phone" in content
    assert "## Claims To Avoid" in content
    assert "## Actions by Intervention Class" in content
    assert "## Monitoring Plan" in content
    assert "## Pipeline Provenance" in content


def test_action_brief_groups_by_gap_type() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)

    content = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
    )
    assert "### Perception Gaps" in content
    assert "### Discovery Gaps" in content
    assert "### Attention Gaps" in content


def test_action_brief_includes_prescription_data() -> None:
    artifacts = _artifacts()
    prescription = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)
    content = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        prescription=prescription,
    )
    assert "monitoring prompts" in content.lower()
    assert "Planned Topics" in content


def test_action_brief_does_not_contain_raw_snippets() -> None:
    artifacts = _artifacts()
    content = build_action_brief(artifacts.study_ssot, artifacts.manifest)
    assert POISON not in content


def test_action_brief_has_provenance_section() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(artifacts.study_ssot, artifacts.manifest, classification)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)

    content = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
    )
    assert "Data Sources" in content
