import hashlib
import json
from pathlib import Path

import pytest

from presence_rx.analyze_gemini import (
    GeminiClientResponse,
    build_gemini_analysis,
    write_gemini_analysis,
)
from presence_rx.build_evidence_ledger import (
    LEDGER_TEMPLATE_VERSION,
    OUTPUT_NAME,
    build_evidence_ledger,
    main,
    write_evidence_ledger,
)
from presence_rx.classify_gaps import build_gap_classification, write_gap_classification
from presence_rx.contracts import EvidenceLedger
from presence_rx.enrich_tavily import (
    TavilyClientResponse,
    build_tavily_evidence,
    write_tavily_evidence,
)
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed, write_artifacts
from presence_rx.plan_prescriptions import build_prescription_plan, write_prescription_plan

POISON = "POISON_TOKEN_DO_NOT_LEAK"


class FixedGeminiClient:
    def __init__(self, signal: str) -> None:
        self.signal = signal

    def analyze(self, *, model: str, prompt: str) -> GeminiClientResponse:
        return GeminiClientResponse(
            text=json.dumps(
                {
                    "perception_themes": [f"{POISON} theme"],
                    "missing_associations": [f"{POISON} missing"],
                    "competitor_association": f"{POISON} competitor",
                    "safe_scenario_wording": f"{POISON} scenario",
                    "gap_type_support": self.signal,
                    "rationale": f"{POISON} rationale",
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
        role = "target" if "Nothing Phone" in query else "competitor"
        roles_with_results = {
            "supports": {"target", "competitor"},
            "conflicts": {"target"},
            "insufficient": set(),
        }[self.signal]
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
            payload={"results": results, "response_time": 0.1, "usage": {"credits": 1}}
        )


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def _classification(gemini_signal: str | None = None, tavily_signal: str | None = None):
    artifacts = _artifacts()
    gemini = (
        build_gemini_analysis(
            artifacts.study_ssot,
            artifacts.manifest,
            model="gemini-test-model",
            client=FixedGeminiClient(gemini_signal),
        )
        if gemini_signal
        else None
    )
    tavily = (
        build_tavily_evidence(
            artifacts.study_ssot,
            artifacts.manifest,
            client=FixedTavilyClient(tavily_signal),
        )
        if tavily_signal
        else None
    )
    return build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=gemini,
        tavily=tavily,
    )


def _ledger(gemini_signal: str | None = None, tavily_signal: str | None = None):
    artifacts = _artifacts()
    return build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        _classification(gemini_signal, tavily_signal),
    )


def test_builds_one_claim_per_classified_gap() -> None:
    ledger = _ledger("supports", "supports")

    assert len(ledger.claims) == 4
    assert {claim.cluster_id for claim in ledger.claims} == {
        "cluster:mobile-ecosystem",
        "cluster:consumer-tech-innovation",
        "cluster:minimalist-hardware",
        "cluster:wireless-audio",
    }


def test_metadata_and_template_version_are_recorded() -> None:
    ledger = _ledger()

    assert ledger.metadata.source_manifest_ref == "peec:snapshot:nothing-phone:2026-04-25"
    assert ledger.metadata.peec_snapshot_id == "peec:snapshot:nothing-phone:2026-04-25"
    assert ledger.metadata.ledger_template_version == LEDGER_TEMPLATE_VERSION
    assert ledger.metadata.used_classification is True
    assert ledger.metadata.classifier_version == "gap_classifier:v1"
    assert ledger.brand == "Nothing Phone"


def test_confirmed_claims_are_directional_with_mechanical_language() -> None:
    ledger = _ledger("supports", "supports")

    for claim in ledger.claims:
        assert claim.status == "directional"
        assert claim.publication_status == "directional_with_caveat"
        assert claim.confidence_tier == "strong"
        assert claim.why_not_stronger is None
        assert claim.publication_language.startswith("Prioritize testing the Nothing Phone")
        assert "3 of 3 methods support." in claim.publication_language


def test_provisional_claims_are_diagnostics_only_and_not_blocked() -> None:
    ledger = _ledger()

    assert {claim.status for claim in ledger.claims} == {"insufficient_evidence"}
    assert {claim.publication_status for claim in ledger.claims} == {"diagnostics_only"}
    assert ledger.blocked_claims == []
    for claim in ledger.claims:
        assert claim.publication_language.startswith("Explore the Nothing Phone")
        assert claim.why_not_stronger == (
            "confidence_tier=limited; needs reviewed multi-method support with "
            "no conflicts to reach strong"
        )


def test_conflicted_claims_are_blocked_and_registered() -> None:
    ledger = _ledger("supports", "conflicts")

    assert {claim.status for claim in ledger.claims} == {"blocked"}
    assert {claim.publication_status for claim in ledger.claims} == {"blocked"}
    assert len(ledger.blocked_claims) == len(ledger.claims)
    assert {claim.claim_id for claim in ledger.claims} == {
        blocked.claim_id for blocked in ledger.blocked_claims
    }
    for blocked in ledger.blocked_claims:
        assert blocked.blocked_reason == "METHOD_CONFLICT"
        assert blocked.safe_rewrite.startswith("Explore the Nothing Phone association")
        assert "rerun classification after conflicts are resolved" in (
            blocked.next_evidence_to_collect
        )


def test_zero_conflicts_emits_zero_block_register_entries() -> None:
    ledger = _ledger("supports", "supports")

    assert all(claim.status != "blocked" for claim in ledger.claims)
    assert ledger.blocked_claims == []
    EvidenceLedger.model_validate(ledger.model_dump(mode="json"))


def test_methods_filter_unavailable_signals() -> None:
    ledger = _ledger()

    assert {tuple(claim.methods) for claim in ledger.claims} == {("peec",)}


def test_evidence_items_are_created_for_every_claim_ref_with_null_urls() -> None:
    ledger = _ledger("supports", "supports")

    claim_refs = {ref for claim in ledger.claims for ref in claim.evidence_refs}
    evidence_refs = {item.evidence_ref for item in ledger.evidence}

    assert evidence_refs == claim_refs
    assert all(item.url is None for item in ledger.evidence)
    assert {item.source_type for item in ledger.evidence} == {
        "peec_mcp",
        "derived",
        "gemini",
        "tavily",
    }


def test_partner_text_and_urls_do_not_leak() -> None:
    ledger = _ledger("supports", "supports")
    payload = ledger.model_dump_json()

    assert POISON not in payload
    assert "example.com" not in payload


def test_written_evidence_ledger_is_byte_identical(tmp_path: Path) -> None:
    ledger = _ledger("supports", "supports")
    first_dir = tmp_path / "first"
    second_dir = tmp_path / "second"

    first = write_evidence_ledger(ledger, first_dir).read_bytes()
    second = write_evidence_ledger(ledger, second_dir).read_bytes()

    assert first == second


def test_written_evidence_ledger_validates(tmp_path: Path) -> None:
    path = write_evidence_ledger(_ledger("supports", "supports"), tmp_path)

    EvidenceLedger.model_validate_json(path.read_text())


def test_main_requires_classification_path(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)

    with pytest.raises(Exception, match="missing classification"):
        main(
            study=tmp_path / "study_ssot.json",
            manifest=tmp_path / "manifest.json",
            classification=tmp_path / "missing_gap_classification.json",
            out=tmp_path,
        )


def test_main_writes_only_evidence_ledger(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)
    classification = _classification("supports", "supports")
    write_gap_classification(classification, tmp_path)

    main(
        study=tmp_path / "study_ssot.json",
        manifest=tmp_path / "manifest.json",
        classification=tmp_path / "gap_classification.json",
        out=tmp_path,
    )

    assert (tmp_path / OUTPUT_NAME).exists()


def test_step2_step3_step5_step6_and_step7_artifacts_are_not_modified(tmp_path: Path) -> None:
    artifacts = _artifacts()
    write_artifacts(artifacts, tmp_path)
    write_prescription_plan(
        build_prescription_plan(artifacts.study_ssot, artifacts.manifest),
        tmp_path,
    )
    gemini = build_gemini_analysis(
        artifacts.study_ssot,
        artifacts.manifest,
        model="gemini-test-model",
        client=FixedGeminiClient("supports"),
    )
    tavily = build_tavily_evidence(
        artifacts.study_ssot,
        artifacts.manifest,
        client=FixedTavilyClient("supports"),
    )
    write_gemini_analysis(gemini, tmp_path)
    write_tavily_evidence(tavily, tmp_path)
    classification = build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=gemini,
        tavily=tavily,
    )
    write_gap_classification(classification, tmp_path)
    protected = [
        "manifest.json",
        "study_ssot.json",
        "prompt_universe.json",
        "hero_cards.json",
        "prescription_plan.json",
        "gemini_analysis.json",
        "tavily_evidence.json",
        "gap_classification.json",
    ]
    before = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }

    write_evidence_ledger(
        build_evidence_ledger(
            artifacts.study_ssot,
            artifacts.manifest,
            classification,
        ),
        tmp_path,
    )

    after = {
        name: hashlib.sha256((tmp_path / name).read_bytes()).hexdigest()
        for name in protected
    }
    assert before == after
