import hashlib
import json
from pathlib import Path

import pytest
import typer
from pydantic import ValidationError

from presence_rx.analyze_gemini import (
    OUTPUT_NAME,
    GeminiAnalysisError,
    GeminiClientResponse,
    build_gemini_analysis,
    build_requests,
    main,
    write_gemini_analysis,
)
from presence_rx.contracts import GeminiAnalysis, GeminiMetadata
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed, write_artifacts
from presence_rx.plan_prescriptions import build_prescription_plan, write_prescription_plan


class FakeGeminiClient:
    def __init__(self, *, fail_after: int | None = None, malformed: bool = False) -> None:
        self.calls: list[tuple[str, str]] = []
        self.fail_after = fail_after
        self.malformed = malformed

    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise RuntimeError("simulated Gemini failure")
        self.calls.append((model, prompt))
        if self.malformed:
            return GeminiClientResponse(text='{"perception_themes": []}')
        return GeminiClientResponse(
            text=json.dumps(
                {
                    "perception_themes": ["design-led Android alternative"],
                    "missing_associations": ["category ownership language"],
                    "competitor_association": "A competitor is the Peec-listed owner.",
                    "safe_scenario_wording": (
                        "Treat this as a diagnostic signal to test clearer association wording."
                    ),
                    "gap_type_support": "supports",
                    "rationale": "The Peec row and cautious theme analysis point the same way.",
                }
            ),
            response_model_version="gemini-test-version",
            input_tokens=101,
            output_tokens=37,
        )


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def test_builds_four_blind_spot_findings() -> None:
    artifacts = _artifacts()
    client = FakeGeminiClient()

    analysis = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=client,
    )

    assert analysis.summary.analyzed_rows == 4
    assert len(analysis.findings) == 4
    assert len(client.calls) == 4
    assert all("smartphone-design" not in finding.finding_id for finding in analysis.findings)


def test_every_finding_has_peec_study_and_gemini_refs() -> None:
    artifacts = _artifacts()
    analysis = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FakeGeminiClient(),
    )

    for finding in analysis.findings:
        row_slug = finding.cluster_id.removeprefix("cluster:")
        assert "peec:snapshot:nothing-phone:2026-04-25" in finding.evidence_refs
        assert f"peec:topic:{row_slug}" in finding.evidence_refs
        assert f"study_ssot:row:{row_slug}" in finding.evidence_refs
        assert f"gemini:analysis:{row_slug}:v1" in finding.evidence_refs
        assert finding.source_of_record == "gemini"


def test_metadata_tracks_model_prompt_usage_and_sdk() -> None:
    artifacts = _artifacts()
    analysis = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FakeGeminiClient(),
        run_mode="test",
    )

    assert analysis.metadata.run_mode == "test"
    assert analysis.metadata.requested_model == "gemini-test-model"
    assert analysis.metadata.response_model_version == "gemini-test-version"
    assert analysis.metadata.prompt_template_version == "gemini_blind_spot_analysis:v1"
    assert analysis.metadata.temperature == 0
    assert analysis.metadata.request_count == 4
    assert analysis.metadata.input_tokens == 404
    assert analysis.metadata.output_tokens == 148
    assert analysis.metadata.sdk_package == "google-genai"
    assert analysis.metadata.sdk_version


def test_invalid_run_mode_fails_model_validation() -> None:
    metadata = build_gemini_analysis(
        _artifacts().study_ssot,
        _artifacts().manifest,
        model="gemini-test-model",
        client=FakeGeminiClient(),
    ).metadata.model_dump()
    metadata["run_mode"] = "fixture"

    with pytest.raises(ValidationError, match="live|test"):
        GeminiMetadata.model_validate(metadata)


def test_malformed_gemini_output_fails_validation() -> None:
    artifacts = _artifacts()

    with pytest.raises(GeminiAnalysisError, match="failed after 0 of 4 rows"):
        build_gemini_analysis(
            artifacts.study_ssot,
            artifacts.manifest,
            model="gemini-test-model",
            client=FakeGeminiClient(malformed=True),
        )


def test_partial_failure_writes_no_artifact(tmp_path: Path) -> None:
    artifacts = _artifacts()

    with pytest.raises(GeminiAnalysisError, match="failed after 2 of 4 rows"):
        analysis = build_gemini_analysis(
            artifacts.study_ssot,
            artifacts.manifest,
            model="gemini-test-model",
            client=FakeGeminiClient(fail_after=2),
        )
        write_gemini_analysis(analysis, tmp_path)

    assert not (tmp_path / OUTPUT_NAME).exists()


def test_partial_failure_reports_progress() -> None:
    artifacts = _artifacts()

    with pytest.raises(GeminiAnalysisError, match="failed after 2 of 4 rows") as exc:
        build_gemini_analysis(
            artifacts.study_ssot,
            artifacts.manifest,
            model="gemini-test-model",
            client=FakeGeminiClient(fail_after=2),
        )

    assert "failed_row=cluster:minimalist-hardware" in str(exc.value)
    assert "output not written" in str(exc.value)


def test_written_gemini_analysis_validates(tmp_path: Path) -> None:
    artifacts = _artifacts()
    analysis = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FakeGeminiClient(),
    )
    path = write_gemini_analysis(analysis, tmp_path)

    GeminiAnalysis.model_validate_json(path.read_text())


def test_preview_path_prints_plan_and_writes_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write_artifacts(_artifacts(), tmp_path)

    main(
        study=tmp_path / "study_ssot.json",
        manifest=tmp_path / "manifest.json",
        out=tmp_path,
        model="gemini-test-model",
        live=True,
        yes_confirm_billing=False,
    )

    captured = capsys.readouterr()
    assert "estimated_request_count: 4" in captured.out
    assert "No Gemini request sent" in captured.out
    assert not (tmp_path / OUTPUT_NAME).exists()


def test_live_confirmed_requires_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_artifacts(_artifacts(), tmp_path)
    monkeypatch.setenv("GEMINI_API_KEY", "")

    with pytest.raises(typer.Exit) as exc:
        main(
            study=tmp_path / "study_ssot.json",
            manifest=tmp_path / "manifest.json",
            out=tmp_path,
            model="gemini-test-model",
            live=True,
            yes_confirm_billing=True,
        )

    assert exc.value.exit_code == 1
    assert not (tmp_path / OUTPUT_NAME).exists()


def test_model_is_required_for_preview(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_artifacts(_artifacts(), tmp_path)
    monkeypatch.setenv("GEMINI_MODEL", "")

    with pytest.raises(typer.Exit) as exc:
        main(
            study=tmp_path / "study_ssot.json",
            manifest=tmp_path / "manifest.json",
            out=tmp_path,
            model=None,
            live=False,
            yes_confirm_billing=False,
        )

    assert exc.value.exit_code == 1
    assert not (tmp_path / OUTPUT_NAME).exists()


def test_step2_and_step3_artifacts_are_not_modified(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)
    write_prescription_plan(
        build_prescription_plan(artifacts.study_ssot, artifacts.manifest),
        tmp_path,
    )
    protected = [
        "manifest.json",
        "study_ssot.json",
        "prompt_universe.json",
        "hero_cards.json",
        "prescription_plan.json",
    ]
    before = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }

    analysis = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FakeGeminiClient(),
    )
    write_gemini_analysis(analysis, tmp_path)

    after = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }
    assert before == after


def test_build_requests_excludes_stronghold() -> None:
    requests = build_requests(_artifacts().study_ssot, _artifacts().manifest)

    assert len(requests) == 4
    assert all(request.row.cluster_id != "cluster:smartphone-design" for request in requests)
