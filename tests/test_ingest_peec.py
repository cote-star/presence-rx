from datetime import UTC, datetime
from pathlib import Path

import pytest

from presence_rx.contracts import (
    HeroCards,
    Manifest,
    PipelineFunnel,
    PromptUniverse,
    SourceOfRecord,
    StudySsot,
)
from presence_rx.ingest_peec import (
    PROMPT_TEXT_UNAVAILABLE,
    SNAPSHOT_REF,
    build_artifacts,
    nothing_phone_seed,
    resolve_generated_at,
    write_artifacts,
)


def test_seed_ingestion_creates_five_topic_rows() -> None:
    artifacts = build_artifacts(nothing_phone_seed())

    assert len(artifacts.study_ssot.rows) == 5
    assert [row.cluster_label for row in artifacts.study_ssot.rows] == [
        "Smartphone Design",
        "Mobile Ecosystem",
        "Consumer Tech Innovation",
        "Minimalist Hardware",
        "Wireless Audio",
    ]


def test_locked_topic_metrics_match_ground_truth() -> None:
    rows = {row.cluster_label: row for row in build_artifacts(nothing_phone_seed()).study_ssot.rows}

    assert rows["Smartphone Design"].visibility_target_share == 0.72
    assert rows["Smartphone Design"].visibility_target_avg_position == 1.9
    assert rows["Mobile Ecosystem"].visibility_target_share == 0.12
    assert rows["Consumer Tech Innovation"].visibility_target_share == 0.10
    assert rows["Minimalist Hardware"].visibility_target_share == 0.06
    assert rows["Wireless Audio"].visibility_target_share == 0.01


def test_stronghold_has_no_competitor_owner() -> None:
    rows = {row.cluster_label: row for row in build_artifacts(nothing_phone_seed()).study_ssot.rows}

    assert rows["Smartphone Design"].visibility_competitor_owner is None


def test_every_study_row_has_peec_evidence_ref() -> None:
    artifacts = build_artifacts(nothing_phone_seed())

    for row in artifacts.study_ssot.rows:
        assert row.evidence_refs
        assert all(ref.startswith("peec:") for ref in row.evidence_refs)


def test_manifest_snapshot_id_is_deterministic() -> None:
    manifest = build_artifacts(nothing_phone_seed()).manifest

    assert manifest.peec_snapshot_id == SNAPSHOT_REF
    assert manifest.sources["peec_mcp"].snapshot_id == SNAPSHOT_REF
    assert manifest.generated_at.isoformat() == "2026-04-25T00:00:00+00:00"
    assert manifest.freshness.generated_at.isoformat() == "2026-04-25T00:00:00+00:00"


def test_generated_at_override_is_supported() -> None:
    seed = nothing_phone_seed()
    generated_at = resolve_generated_at(seed, "2026-04-25T12:34:56Z")

    manifest = build_artifacts(seed, generated_at=generated_at).manifest

    assert manifest.generated_at.isoformat() == "2026-04-25T12:34:56+00:00"


def test_source_date_epoch_override_is_supported(monkeypatch: pytest.MonkeyPatch) -> None:
    seed = nothing_phone_seed()
    monkeypatch.setenv("SOURCE_DATE_EPOCH", "1767225600")

    generated_at = resolve_generated_at(seed)

    assert generated_at.isoformat() == "2026-01-01T00:00:00+00:00"


def test_source_of_record_is_peec_or_derived_only() -> None:
    source_of_record = build_artifacts(nothing_phone_seed()).source_of_record

    assert {item.source for item in source_of_record.sources} <= {"peec_mcp", "derived"}


def test_provisional_gap_type_count_is_derived() -> None:
    funnel = build_artifacts(nothing_phone_seed()).pipeline_funnel
    stages = {stage.stage: stage.count for stage in funnel.stages}
    expected_gap_count = sum(1 for topic in nothing_phone_seed().topics if topic.gap_type)

    assert stages["provisional_gap_type_rows"] == expected_gap_count


def test_prompt_text_unavailability_is_explicit() -> None:
    prompt_universe = build_artifacts(nothing_phone_seed()).prompt_universe

    for cluster in prompt_universe.clusters:
        prompt = cluster.prompts[0]
        assert prompt.text is None
        assert prompt.unavailable_reason == PROMPT_TEXT_UNAVAILABLE


def test_no_prescription_plan_is_generated(tmp_path: Path) -> None:
    write_artifacts(build_artifacts(nothing_phone_seed()), tmp_path)

    assert not (tmp_path / "prescription_plan.json").exists()


def test_written_artifacts_match_contracts(tmp_path: Path) -> None:
    write_artifacts(build_artifacts(nothing_phone_seed()), tmp_path)

    PromptUniverse.model_validate_json((tmp_path / "prompt_universe.json").read_text())
    StudySsot.model_validate_json((tmp_path / "study_ssot.json").read_text())
    Manifest.model_validate_json((tmp_path / "manifest.json").read_text())
    SourceOfRecord.model_validate_json((tmp_path / "source_of_record.json").read_text())
    PipelineFunnel.model_validate_json((tmp_path / "pipeline_funnel.json").read_text())
    HeroCards.model_validate_json((tmp_path / "hero_cards.json").read_text())


def test_manifest_is_byte_identical_with_fixed_generated_at(tmp_path: Path) -> None:
    seed = nothing_phone_seed()
    fixed_time = datetime(2026, 4, 25, 12, 34, 56, tzinfo=UTC)
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    write_artifacts(build_artifacts(seed, generated_at=fixed_time), first_dir)
    write_artifacts(build_artifacts(seed, generated_at=fixed_time), second_dir)

    assert (first_dir / "manifest.json").read_bytes() == (second_dir / "manifest.json").read_bytes()
