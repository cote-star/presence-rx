import hashlib
import json
from pathlib import Path

import pytest
from pydantic import ValidationError

from presence_rx.contracts import PlannedPrompt, PrescriptionPlan
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed, write_artifacts
from presence_rx.plan_prescriptions import (
    build_prescription_plan,
    write_prescription_plan,
)


def _step2_inputs(tmp_path: Path) -> tuple[Path, Path]:
    write_artifacts(build_artifacts(nothing_phone_seed()), tmp_path)
    return tmp_path / "study_ssot.json", tmp_path / "manifest.json"


def _build_plan() -> PrescriptionPlan:
    artifacts = build_artifacts(nothing_phone_seed())
    return build_prescription_plan(artifacts.study_ssot, artifacts.manifest)


def test_plan_generates_exactly_twelve_prompts() -> None:
    plan = _build_plan()

    assert plan.summary.planned_prompts == 12
    assert len(plan.planned_prompts) == 12


def test_stronghold_is_excluded_from_planned_operations() -> None:
    plan = _build_plan()
    payload = plan.model_dump_json()

    assert "smartphone-design" not in payload
    assert all(
        prompt.source_cluster_id != "cluster:smartphone-design"
        for prompt in plan.planned_prompts
    )


def test_operation_ids_are_slug_based_and_suffix_free() -> None:
    plan = _build_plan()
    operation_ids = [
        *[topic.operation_id for topic in plan.planned_topics],
        *[tag.operation_id for tag in plan.planned_tags],
        *[prompt.operation_id for prompt in plan.planned_prompts],
    ]

    assert "op:create_prompt:minimalist-hardware:de" in operation_ids
    assert "op:create_topic:minimalist-hardware" in operation_ids
    assert "op:create_tag:gap-perception" in operation_ids
    assert all(":001" not in operation_id for operation_id in operation_ids)
    assert all(" " not in operation_id for operation_id in operation_ids)


def test_invalid_execution_status_fails_model_validation() -> None:
    valid_prompt = _build_plan().planned_prompts[0].model_dump()
    valid_prompt["execution_status"] = "executed"

    with pytest.raises(ValidationError, match="planned"):
        PlannedPrompt.model_validate(valid_prompt)


def test_country_codes_are_limited_to_us_de_gb() -> None:
    country_codes = {prompt.country_code for prompt in _build_plan().planned_prompts}

    assert country_codes == {"US", "DE", "GB"}


def test_planned_prompt_text_language_and_source_are_explicit() -> None:
    for prompt in _build_plan().planned_prompts:
        assert prompt.text
        assert prompt.prompt_language == "en"
        assert prompt.prompt_text_source == "templated"


def test_prompts_trace_to_study_rows_and_peec_refs() -> None:
    for prompt in _build_plan().planned_prompts:
        row_ref = prompt.source_cluster_id.removeprefix("cluster:")
        assert f"study_ssot:row:{row_ref}" in prompt.evidence_refs
        assert "peec:snapshot:nothing-phone:2026-04-25" in prompt.evidence_refs
        assert any(ref.startswith("peec:topic:") for ref in prompt.evidence_refs)


def test_evidence_refs_have_no_double_cluster_prefix() -> None:
    plan = _build_plan()
    for topic in plan.planned_topics:
        for ref in topic.evidence_refs:
            assert ":cluster:" not in ref, (
                f"planned_topic evidence_ref {ref!r} contains ':cluster:' "
                "(double-prefix regression)"
            )
    for prompt in plan.planned_prompts:
        for ref in prompt.evidence_refs:
            assert ":cluster:" not in ref, (
                f"planned_prompt evidence_ref {ref!r} contains ':cluster:' "
                "(double-prefix regression)"
            )


def test_plan_output_is_byte_identical_across_runs(tmp_path: Path) -> None:
    artifacts = build_artifacts(nothing_phone_seed())
    plan = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = write_prescription_plan(plan, first_dir).read_bytes()
    second = write_prescription_plan(plan, second_dir).read_bytes()

    assert first == second


def test_step2_artifacts_are_not_modified_by_plan_write(tmp_path: Path) -> None:
    write_artifacts(build_artifacts(nothing_phone_seed()), tmp_path)
    before = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in ["manifest.json", "prompt_universe.json", "hero_cards.json"]
    }

    plan = _build_plan()
    write_prescription_plan(plan, tmp_path)

    after = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in ["manifest.json", "prompt_universe.json", "hero_cards.json"]
    }
    assert before == after


def test_prescription_plan_validates_from_written_json(tmp_path: Path) -> None:
    plan = _build_plan()
    path = write_prescription_plan(plan, tmp_path)

    PrescriptionPlan.model_validate_json(path.read_text())


def test_planner_reads_json_inputs_only(tmp_path: Path) -> None:
    study_path, manifest_path = _step2_inputs(tmp_path)
    study_payload = json.loads(study_path.read_text())
    manifest_payload = json.loads(manifest_path.read_text())

    plan = build_prescription_plan(
        study=type(build_artifacts(nothing_phone_seed()).study_ssot).model_validate(study_payload),
        manifest=type(build_artifacts(nothing_phone_seed()).manifest).model_validate(manifest_payload),
    )

    assert plan.summary.planned_prompts == 12
