import hashlib
import json
from pathlib import Path
from typing import Any

import pytest
import typer
from pydantic import ValidationError

from presence_rx.analyze_gemini import (
    GeminiClientResponse,
    build_gemini_analysis,
    write_gemini_analysis,
)
from presence_rx.contracts import TavilyEvidence, TavilyMetadata
from presence_rx.enrich_tavily import (
    OUTPUT_NAME,
    TavilyClientResponse,
    TavilyEnrichmentError,
    build_queries,
    build_tavily_evidence,
    canonicalize_url,
    main,
    write_tavily_evidence,
)
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed, write_artifacts
from presence_rx.plan_prescriptions import build_prescription_plan, write_prescription_plan


class FakeTavilyClient:
    def __init__(self, *, fail_after: int | None = None, malformed: bool = False) -> None:
        self.calls: list[dict[str, Any]] = []
        self.fail_after = fail_after
        self.malformed = malformed

    def search(
        self,
        *,
        query: str,
        search_depth: str,
        max_results: int,
        timeout: int,
    ) -> TavilyClientResponse:
        if self.fail_after is not None and len(self.calls) >= self.fail_after:
            raise RuntimeError("simulated Tavily failure")
        self.calls.append(
            {
                "query": query,
                "search_depth": search_depth,
                "max_results": max_results,
                "timeout": timeout,
            }
        )
        if self.malformed:
            return TavilyClientResponse(payload={"results": [{"url": ""}]})
        slug = query.lower().replace('"', "").replace(" ", "-")
        return TavilyClientResponse(
            payload={
                "results": [
                    {
                        "title": f"Public result for {query}",
                        "url": f"https://example.com/{slug}?utm_source=test#section",
                        "content": (
                            "A concise public-web snippet that is useful only after "
                            "human review."
                        ),
                        "score": 0.72,
                    }
                ],
                "response_time": 0.25,
                "usage": {"credits": 1},
            }
        )


class RoleSelectiveTavilyClient:
    def __init__(self, roles_with_results: set[str]) -> None:
        self.roles_with_results = roles_with_results

    def search(
        self,
        *,
        query: str,
        search_depth: str,
        max_results: int,
        timeout: int,
    ) -> TavilyClientResponse:
        role = "target" if "Nothing Phone" in query else "competitor"
        results = []
        if role in self.roles_with_results:
            results.append(
                {
                    "title": f"{role.title()} public result",
                    "url": f"https://example.com/{role}",
                    "content": f"{role.title()} public snippet awaiting human review.",
                    "score": 0.61,
                }
            )
        return TavilyClientResponse(
            payload={
                "results": results,
                "response_time": 0.1,
                "usage": {"credits": 1},
            }
        )


class FakeGeminiClient:
    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
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
            input_tokens=1,
            output_tokens=1,
        )


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def test_build_queries_creates_eight_searches_and_excludes_stronghold() -> None:
    artifacts = _artifacts()

    queries = build_queries(artifacts.study_ssot, artifacts.manifest)

    assert len(queries) == 8
    assert all(query.row.cluster_id != "cluster:smartphone-design" for query in queries)
    assert [query.source_role for query in queries[:2]] == ["target", "competitor"]


def test_wireless_audio_queries_are_exact() -> None:
    artifacts = _artifacts()
    queries = build_queries(artifacts.study_ssot, artifacts.manifest)
    wireless = [query for query in queries if query.row.cluster_id == "cluster:wireless-audio"]

    assert [query.query for query in wireless] == [
        '"Nothing Phone" "Wireless Audio" reviews proof',
        '"Apple" "Wireless Audio" reviews proof',
    ]
    assert [query.query_ref for query in wireless] == [
        "row:wireless-audio:target_query",
        "row:wireless-audio:competitor_query",
    ]


def test_builds_four_findings_from_fake_tavily() -> None:
    artifacts = _artifacts()
    client = FakeTavilyClient()

    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=client,
    )

    assert evidence.summary.analyzed_rows == 4
    assert evidence.summary.planned_queries == 8
    assert evidence.summary.sources == 8
    assert len(client.calls) == 8
    assert evidence.metadata.successful_query_count == 8
    assert evidence.metadata.failed_query_count == 0
    assert evidence.metadata.search_depth == "basic"
    assert evidence.metadata.max_results == 5
    assert evidence.metadata.query_timeout_seconds == 30
    assert evidence.metadata.include_raw_content is False
    assert evidence.metadata.include_answer is False
    assert evidence.metadata.include_images is False
    assert evidence.metadata.include_usage is True
    assert evidence.metadata.response_time_seconds == 2.0
    assert evidence.metadata.api_credits_used == 8.0


def test_sources_are_canonicalized_query_derived_and_raw() -> None:
    artifacts = _artifacts()
    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FakeTavilyClient(),
    )

    for finding in evidence.findings:
        assert {source.source_role for source in finding.sources} == {"target", "competitor"}
        for source in finding.sources:
            assert "?" not in str(source.url)
            assert "#" not in str(source.url)
            assert source.snippet_review_status == "raw"
            assert source.query_ref.endswith(("target_query", "competitor_query"))


def test_canonicalize_url_strips_query_and_fragment() -> None:
    assert canonicalize_url("https://Example.com/path/?utm=1#section") == "https://example.com/path"


def test_every_finding_has_peec_study_and_tavily_refs() -> None:
    artifacts = _artifacts()
    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FakeTavilyClient(),
    )

    for finding in evidence.findings:
        row_slug = finding.cluster_id.removeprefix("cluster:")
        assert "peec:snapshot:nothing-phone:2026-04-25" in finding.evidence_refs
        assert f"peec:topic:{row_slug}" in finding.evidence_refs
        assert f"study_ssot:row:{row_slug}" in finding.evidence_refs
        assert f"tavily:evidence:{row_slug}:v1" in finding.evidence_refs
        assert finding.source_of_record == "tavily"
        assert finding.public_proof_support in {"supports", "conflicts", "insufficient"}


def test_target_only_sources_conflict_with_blind_spot_label() -> None:
    artifacts = _artifacts()
    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=RoleSelectiveTavilyClient({"target"}),
    )

    assert {finding.public_proof_support for finding in evidence.findings} == {"conflicts"}
    assert evidence.summary.conflicted_findings == 4


def test_no_sources_are_insufficient() -> None:
    artifacts = _artifacts()
    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=RoleSelectiveTavilyClient(set()),
    )

    assert {finding.public_proof_support for finding in evidence.findings} == {"insufficient"}
    assert evidence.summary.insufficient_findings == 4


def test_invalid_run_mode_fails_model_validation() -> None:
    metadata = build_tavily_evidence(
        _artifacts().study_ssot,
        _artifacts().manifest,
        client=FakeTavilyClient(),
    ).metadata.model_dump()
    metadata["run_mode"] = "fixture"

    with pytest.raises(ValidationError, match="live|test"):
        TavilyMetadata.model_validate(metadata)


def test_malformed_tavily_output_fails_validation() -> None:
    artifacts = _artifacts()

    with pytest.raises(TavilyEnrichmentError, match="failed after 0 of 8 queries"):
        build_tavily_evidence(
            artifacts.study_ssot,
            artifacts.manifest,
            client=FakeTavilyClient(malformed=True),
        )


def test_partial_failure_writes_no_artifact(tmp_path: Path) -> None:
    artifacts = _artifacts()

    with pytest.raises(
        TavilyEnrichmentError,
        match=(
            "failed after 3 of 8 queries; "
            "failed_query_ref=row:consumer-tech-innovation:competitor_query"
        ),
    ):
        evidence = build_tavily_evidence(
            artifacts.study_ssot,
            artifacts.manifest,
            client=FakeTavilyClient(fail_after=3),
        )
        write_tavily_evidence(evidence, tmp_path)

    assert not (tmp_path / OUTPUT_NAME).exists()


def test_written_tavily_evidence_validates(tmp_path: Path) -> None:
    artifacts = _artifacts()
    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FakeTavilyClient(),
    )
    path = write_tavily_evidence(evidence, tmp_path)

    TavilyEvidence.model_validate_json(path.read_text())


def test_preview_path_prints_plan_and_writes_nothing(
    tmp_path: Path,
    capsys: pytest.CaptureFixture[str],
) -> None:
    write_artifacts(_artifacts(), tmp_path)

    main(
        study=tmp_path / "study_ssot.json",
        manifest=tmp_path / "manifest.json",
        out=tmp_path,
        live=True,
        yes_confirm_billing=False,
    )

    captured = capsys.readouterr()
    assert "estimated_request_count: 8" in captured.out
    assert "Nothing Phone" in captured.out
    assert "Wireless Audio" in captured.out
    assert "No Tavily request sent" in captured.out
    assert not (tmp_path / OUTPUT_NAME).exists()


def test_live_confirmed_requires_api_key(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> None:
    write_artifacts(_artifacts(), tmp_path)
    monkeypatch.setenv("TAVILY_API_KEY", "")

    with pytest.raises(typer.Exit) as exc:
        main(
            study=tmp_path / "study_ssot.json",
            manifest=tmp_path / "manifest.json",
            out=tmp_path,
            live=True,
            yes_confirm_billing=True,
        )

    assert exc.value.exit_code == 1
    assert not (tmp_path / OUTPUT_NAME).exists()


def test_step2_step3_and_step5_artifacts_are_not_modified(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)
    write_prescription_plan(
        build_prescription_plan(artifacts.study_ssot, artifacts.manifest),
        tmp_path,
    )
    write_gemini_analysis(
        build_gemini_analysis(
            artifacts.study_ssot,
            artifacts.manifest,
            model="gemini-test-model",
            client=FakeGeminiClient(),
        ),
        tmp_path,
    )
    protected = [
        "manifest.json",
        "study_ssot.json",
        "prompt_universe.json",
        "hero_cards.json",
        "prescription_plan.json",
        "gemini_analysis.json",
    ]
    before = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }

    evidence = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FakeTavilyClient(),
    )
    write_tavily_evidence(evidence, tmp_path)

    after = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }
    assert before == after
