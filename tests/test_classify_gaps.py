import hashlib
import json
from pathlib import Path

import pytest

from presence_rx.analyze_gemini import (
    GeminiClientResponse,
    build_gemini_analysis,
    write_gemini_analysis,
)
from presence_rx.classify_gaps import (
    OUTPUT_NAME,
    build_gap_classification,
    main,
    write_gap_classification,
)
from presence_rx.contracts import (
    GapClassification,
    GeminiAnalysis,
    GeminiSummary,
    TavilyEvidence,
    TavilySummary,
)
from presence_rx.enrich_tavily import (
    TavilyClientResponse,
    build_tavily_evidence,
    write_tavily_evidence,
)
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed, write_artifacts
from presence_rx.plan_prescriptions import build_prescription_plan, write_prescription_plan

POISON = "POISON_TOKEN_DO_NOT_LEAK"

EXPECTED_DECISIONS = {
    ("supports", "supports"): ("confirmed", "strong"),
    ("supports", "conflicts"): ("conflicted", "blocked"),
    ("supports", "insufficient"): ("confirmed", "moderate"),
    ("supports", "unavailable"): ("confirmed", "moderate"),
    ("conflicts", "supports"): ("conflicted", "blocked"),
    ("conflicts", "conflicts"): ("conflicted", "blocked"),
    ("conflicts", "insufficient"): ("conflicted", "blocked"),
    ("conflicts", "unavailable"): ("conflicted", "blocked"),
    ("insufficient", "supports"): ("confirmed", "moderate"),
    ("insufficient", "conflicts"): ("conflicted", "blocked"),
    ("insufficient", "insufficient"): ("provisional", "limited"),
    ("insufficient", "unavailable"): ("provisional", "limited"),
    ("unavailable", "supports"): ("confirmed", "moderate"),
    ("unavailable", "conflicts"): ("conflicted", "blocked"),
    ("unavailable", "insufficient"): ("provisional", "limited"),
    ("unavailable", "unavailable"): ("provisional", "limited"),
}


class FixedGeminiClient:
    def __init__(self, signal: str) -> None:
        self.signal = signal

    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
        return GeminiClientResponse(
            text=json.dumps(
                {
                    "perception_themes": ["theme text should not leak"],
                    "missing_associations": ["missing association should not leak"],
                    "competitor_association": "competitor wording should not leak",
                    "safe_scenario_wording": "scenario wording should not leak",
                    "gap_type_support": self.signal,
                    "rationale": "partner rationale should not leak",
                }
            ),
            response_model_version="gemini-test-version",
            input_tokens=1,
            output_tokens=1,
        )


class FixedTavilyClient:
    def __init__(self, signal: str) -> None:
        self.signal = signal

    def search(
        self,
        *,
        query: str,
        search_depth: str,
        max_results: int,
        timeout: int,
    ) -> TavilyClientResponse:
        is_target = "Nothing Phone" in query
        roles_with_results = {
            "supports": {"target", "competitor"},
            "conflicts": {"target"},
            "insufficient": set(),
        }[self.signal]
        role = "target" if is_target else "competitor"
        results = []
        if role in roles_with_results:
            results.append(
                {
                    "title": f"{POISON} title",
                    "url": f"https://example.com/{role}?utm=1#frag",
                    "content": f"{POISON} snippet",
                    "score": 0.9,
                }
            )
        return TavilyClientResponse(
            payload={
                "results": results,
                "response_time": 0.1,
                "usage": {"credits": 1},
            }
        )


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def _gemini(signal: str | None) -> GeminiAnalysis | None:
    if signal is None:
        return None
    artifacts = _artifacts()
    return build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FixedGeminiClient(signal),
    )


def _tavily(signal: str | None) -> TavilyEvidence | None:
    if signal is None:
        return None
    artifacts = _artifacts()
    return build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FixedTavilyClient(signal),
    )


def _classification(gemini_signal: str | None = None, tavily_signal: str | None = None):
    artifacts = _artifacts()
    return build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=_gemini(gemini_signal),
        tavily=_tavily(tavily_signal),
    )


def test_classifies_four_blind_spots_and_excludes_stronghold() -> None:
    classification = _classification()

    assert classification.summary.classified_gaps == 4
    assert len(classification.classified_gaps) == 4
    assert all(
        gap.cluster_id != "cluster:smartphone-design"
        for gap in classification.classified_gaps
    )


def test_absent_partner_paths_are_unavailable_not_cli_failures(tmp_path: Path) -> None:
    write_artifacts(_artifacts(), tmp_path)

    main(
        study=tmp_path / "study_ssot.json",
        manifest=tmp_path / "manifest.json",
        out=tmp_path,
        gemini=tmp_path / "missing_gemini.json",
        tavily=tmp_path / "missing_tavily.json",
    )

    path = tmp_path / OUTPUT_NAME
    classification = GapClassification.model_validate_json(path.read_text())
    assert classification.metadata.used_gemini is False
    assert classification.metadata.used_tavily is False
    for gap in classification.classified_gaps:
        assert [signal.signal for signal in gap.method_signals] == [
            "supports",
            "unavailable",
            "unavailable",
        ]
        assert gap.method_signals[1].unavailable_reason == "artifact_not_provided"
        assert gap.method_signals[2].unavailable_reason == "artifact_not_provided"


@pytest.mark.parametrize(("gemini_signal", "tavily_signal"), sorted(EXPECTED_DECISIONS))
def test_all_decision_table_cells(gemini_signal: str, tavily_signal: str) -> None:
    classification = _classification(
        None if gemini_signal == "unavailable" else gemini_signal,
        None if tavily_signal == "unavailable" else tavily_signal,
    )
    expected_status, expected_tier = EXPECTED_DECISIONS[(gemini_signal, tavily_signal)]

    for gap in classification.classified_gaps:
        assert gap.classification_status == expected_status
        assert gap.confidence_tier == expected_tier
        assert gap.method_signals[1].signal == gemini_signal
        assert gap.method_signals[2].signal == tavily_signal


def test_strong_confidence_requires_tavily_target_and_competitor_sources() -> None:
    classification = _classification("supports", "supports")
    assert {gap.confidence_tier for gap in classification.classified_gaps} == {"strong"}

    target_only = _classification("supports", "conflicts")
    assert {gap.confidence_tier for gap in target_only.classified_gaps} == {"blocked"}


def test_partner_conflict_blocks_classification() -> None:
    classification = _classification("supports", "conflicts")

    assert {gap.classification_status for gap in classification.classified_gaps} == {"conflicted"}
    assert {gap.confidence_tier for gap in classification.classified_gaps} == {"blocked"}


def test_method_agreement_score_uses_supporting_over_available() -> None:
    classification = _classification("insufficient", "supports")

    for gap in classification.classified_gaps:
        assert gap.method_agreement_score == pytest.approx(2 / 3)


def test_classification_rationale_is_mechanical_template() -> None:
    classification = _classification("supports", "conflicts")

    for gap in classification.classified_gaps:
        assert gap.classification_rationale == (
            "Peec(supports) + Gemini(supports) + Tavily(conflicts) - "
            "2 of 3 available methods support; 1 conflicts."
        )


def test_partner_text_and_raw_snippets_do_not_leak() -> None:
    classification = _classification("supports", "supports")
    payload = classification.model_dump_json()

    assert POISON not in payload
    assert "theme text should not leak" not in payload
    assert "partner rationale should not leak" not in payload
    assert "example.com" not in payload


def test_evidence_refs_include_peec_and_available_partner_refs() -> None:
    classification = _classification("supports", "supports")

    for gap in classification.classified_gaps:
        row_slug = gap.cluster_id.removeprefix("cluster:")
        assert "peec:snapshot:nothing-phone:2026-04-25" in gap.evidence_refs
        assert f"peec:topic:{row_slug}" in gap.evidence_refs
        assert f"study_ssot:row:{row_slug}" in gap.evidence_refs
        assert f"gemini:analysis:{row_slug}:v1" in gap.evidence_refs
        assert f"tavily:evidence:{row_slug}:v1" in gap.evidence_refs


def test_gap_classification_output_is_byte_identical(tmp_path: Path) -> None:
    classification = _classification("supports", "supports")
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = write_gap_classification(classification, first_dir).read_bytes()
    second = write_gap_classification(classification, second_dir).read_bytes()

    assert first == second


def test_written_gap_classification_validates(tmp_path: Path) -> None:
    classification = _classification("supports", "supports")
    path = write_gap_classification(classification, tmp_path)

    GapClassification.model_validate_json(path.read_text())


def test_step2_step3_step5_and_step6_artifacts_are_not_modified(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)
    write_prescription_plan(
        build_prescription_plan(artifacts.study_ssot, artifacts.manifest),
        tmp_path,
    )
    write_gemini_analysis(_gemini("supports"), tmp_path)
    write_tavily_evidence(_tavily("supports"), tmp_path)
    protected = [
        "manifest.json",
        "study_ssot.json",
        "prompt_universe.json",
        "hero_cards.json",
        "prescription_plan.json",
        "gemini_analysis.json",
        "tavily_evidence.json",
    ]
    before = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }

    write_gap_classification(_classification("supports", "supports"), tmp_path)

    after = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }
    assert before == after


def test_method_returned_no_finding_reason_when_artifact_has_empty_findings() -> None:
    artifacts = _artifacts()
    gemini = _gemini("supports")
    assert gemini is not None
    empty_gemini = gemini.model_copy(
        update={
            "summary": GeminiSummary(
                analyzed_rows=0,
                supported_gap_types=0,
                conflicted_gap_types=0,
                insufficient_gap_types=0,
            ),
            "findings": [],
        }
    )
    tavily = _tavily("supports")
    assert tavily is not None
    empty_tavily = tavily.model_copy(
        update={
            "summary": TavilySummary(
                analyzed_rows=0,
                planned_queries=tavily.metadata.request_count,
                sources=0,
                supported_findings=0,
                conflicted_findings=0,
                insufficient_findings=0,
            ),
            "findings": [],
        }
    )

    classification = build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=empty_gemini,
        tavily=empty_tavily,
    )

    for gap in classification.classified_gaps:
        assert gap.method_signals[1].signal == "unavailable"
        assert gap.method_signals[1].unavailable_reason == "row_not_in_artifact"
        assert gap.method_signals[2].signal == "unavailable"
        assert gap.method_signals[2].unavailable_reason == "row_not_in_artifact"
