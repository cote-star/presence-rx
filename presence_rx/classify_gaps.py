"""Classify Peec blind spots from local Peec, Gemini, and Tavily artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated, Literal

import typer
from rich.console import Console

from presence_rx.contracts import (
    ClassifiedGap,
    EvidenceTier,
    GapClassification,
    GapClassificationMetadata,
    GapClassificationSummary,
    GeminiAnalysis,
    GeminiFinding,
    Manifest,
    MethodSignal,
    StudyRow,
    StudySsot,
    TavilyEvidence,
    TavilyFinding,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

OUTPUT_NAME = "gap_classification.json"
CLASSIFIER_VERSION = "gap_classifier:v1"
Signal = Literal["supports", "conflicts", "insufficient", "unavailable"]
Status = Literal["confirmed", "provisional", "conflicted", "insufficient"]

RATIO = {
    "supports": "supports",
    "conflicts": "conflicts",
    "insufficient": "insufficient",
    "unavailable": "unavailable",
}

DECISION_TABLE: dict[tuple[Signal, Signal], tuple[Status, EvidenceTier]] = {
    ("supports", "supports"): ("confirmed", EvidenceTier.STRONG),
    ("supports", "conflicts"): ("conflicted", EvidenceTier.BLOCKED),
    ("supports", "insufficient"): ("confirmed", EvidenceTier.MODERATE),
    ("supports", "unavailable"): ("confirmed", EvidenceTier.MODERATE),
    ("conflicts", "supports"): ("conflicted", EvidenceTier.BLOCKED),
    ("conflicts", "conflicts"): ("conflicted", EvidenceTier.BLOCKED),
    ("conflicts", "insufficient"): ("conflicted", EvidenceTier.BLOCKED),
    ("conflicts", "unavailable"): ("conflicted", EvidenceTier.BLOCKED),
    ("insufficient", "supports"): ("confirmed", EvidenceTier.MODERATE),
    ("insufficient", "conflicts"): ("conflicted", EvidenceTier.BLOCKED),
    ("insufficient", "insufficient"): ("provisional", EvidenceTier.LIMITED),
    ("insufficient", "unavailable"): ("provisional", EvidenceTier.LIMITED),
    ("unavailable", "supports"): ("confirmed", EvidenceTier.MODERATE),
    ("unavailable", "conflicts"): ("conflicted", EvidenceTier.BLOCKED),
    ("unavailable", "insufficient"): ("provisional", EvidenceTier.LIMITED),
    ("unavailable", "unavailable"): ("provisional", EvidenceTier.LIMITED),
}


def _blind_spot_rows(study: StudySsot) -> list[StudyRow]:
    return [row for row in study.rows if row.gap_type is not None]


def _study_row_ref(row: StudyRow) -> str:
    return f"study_ssot:row:{row.cluster_id.removeprefix('cluster:')}"


def _topic_ref(row: StudyRow) -> str:
    return f"peec:topic:{slugify(row.cluster_label)}"


def _peec_signal(row: StudyRow, manifest: Manifest) -> MethodSignal:
    refs = [manifest.peec_snapshot_id, _topic_ref(row), _study_row_ref(row), *row.evidence_refs]
    return MethodSignal(
        method="peec",
        signal="supports",
        evidence_refs=list(dict.fromkeys(refs)),
    )


def _finding_map(analysis: GeminiAnalysis | None) -> dict[str, GeminiFinding]:
    return {finding.cluster_id: finding for finding in analysis.findings} if analysis else {}


def _tavily_map(evidence: TavilyEvidence | None) -> dict[str, TavilyFinding]:
    return {finding.cluster_id: finding for finding in evidence.findings} if evidence else {}


def _gemini_signal(row: StudyRow, analysis: GeminiAnalysis | None) -> MethodSignal:
    if analysis is None:
        return MethodSignal(
            method="gemini",
            signal="unavailable",
            unavailable_reason="artifact_not_provided",
        )
    finding = _finding_map(analysis).get(row.cluster_id)
    if finding is None:
        return MethodSignal(
            method="gemini",
            signal="unavailable",
            unavailable_reason="row_not_in_artifact",
        )
    if finding.gap_type_support not in RATIO:
        return MethodSignal(
            method="gemini",
            signal="unavailable",
            unavailable_reason="method_returned_no_finding",
        )
    return MethodSignal(
        method="gemini",
        signal=RATIO[finding.gap_type_support],
        evidence_refs=finding.evidence_refs,
    )


def _tavily_signal(row: StudyRow, evidence: TavilyEvidence | None) -> MethodSignal:
    if evidence is None:
        return MethodSignal(
            method="tavily",
            signal="unavailable",
            unavailable_reason="artifact_not_provided",
        )
    finding = _tavily_map(evidence).get(row.cluster_id)
    if finding is None:
        return MethodSignal(
            method="tavily",
            signal="unavailable",
            unavailable_reason="row_not_in_artifact",
        )
    if finding.public_proof_support not in RATIO:
        return MethodSignal(
            method="tavily",
            signal="unavailable",
            unavailable_reason="method_returned_no_finding",
        )
    return MethodSignal(
        method="tavily",
        signal=RATIO[finding.public_proof_support],
        evidence_refs=finding.evidence_refs,
    )


def _tavily_has_target_and_competitor(row: StudyRow, evidence: TavilyEvidence | None) -> bool:
    if evidence is None:
        return False
    finding = _tavily_map(evidence).get(row.cluster_id)
    if finding is None:
        return False
    roles = {source.source_role for source in finding.sources}
    return {"target", "competitor"} <= roles


def _decision(
    gemini_signal: Signal,
    tavily_signal: Signal,
    *,
    tavily_has_target_and_competitor: bool,
) -> tuple[Status, EvidenceTier]:
    status, tier = DECISION_TABLE[(gemini_signal, tavily_signal)]
    if (gemini_signal, tavily_signal) == ("supports", "supports"):
        tier = EvidenceTier.STRONG if tavily_has_target_and_competitor else EvidenceTier.MODERATE
    return status, tier


def _method_agreement_score(signals: list[MethodSignal]) -> float:
    available = [signal for signal in signals if signal.signal != "unavailable"]
    if not available:
        return 0.0
    supporting = sum(1 for signal in available if signal.signal == "supports")
    return supporting / len(available)


def _mechanical_rationale(signals: list[MethodSignal]) -> str:
    by_method = {signal.method: signal.signal for signal in signals}
    available = [signal for signal in signals if signal.signal != "unavailable"]
    supporting = sum(1 for signal in available if signal.signal == "supports")
    conflicts = sum(1 for signal in available if signal.signal == "conflicts")
    return (
        f"Peec(supports) + Gemini({by_method['gemini']}) + Tavily({by_method['tavily']}) "
        f"- {supporting} of {len(available)} available methods support; {conflicts} conflicts."
    )


def _combined_evidence_refs(signals: list[MethodSignal]) -> list[str]:
    refs: list[str] = []
    for signal in signals:
        refs.extend(signal.evidence_refs)
    return list(dict.fromkeys(refs))


def _classified_gap(
    row: StudyRow,
    manifest: Manifest,
    gemini: GeminiAnalysis | None,
    tavily: TavilyEvidence | None,
) -> ClassifiedGap:
    if row.gap_type is None:
        raise ValueError(f"cannot classify row without gap_type: {row.cluster_id}")
    signals = [
        _peec_signal(row, manifest),
        _gemini_signal(row, gemini),
        _tavily_signal(row, tavily),
    ]
    gemini_signal = signals[1].signal
    tavily_signal = signals[2].signal
    status, confidence_tier = _decision(
        gemini_signal,
        tavily_signal,
        tavily_has_target_and_competitor=_tavily_has_target_and_competitor(row, tavily),
    )
    return ClassifiedGap(
        cluster_id=row.cluster_id,
        cluster_label=row.cluster_label,
        provisional_gap_type=row.gap_type,
        classification_status=status,
        confidence_tier=confidence_tier,
        method_signals=signals,
        method_agreement_score=_method_agreement_score(signals),
        classification_rationale=_mechanical_rationale(signals),
        evidence_refs=_combined_evidence_refs(signals),
    )


def build_gap_classification(
    study: StudySsot,
    manifest: Manifest,
    *,
    gemini: GeminiAnalysis | None = None,
    tavily: TavilyEvidence | None = None,
    generated_at: datetime | None = None,
) -> GapClassification:
    classified = [
        _classified_gap(row, manifest, gemini, tavily) for row in _blind_spot_rows(study)
    ]
    return GapClassification(
        metadata=GapClassificationMetadata(
            generated_at=generated_at or manifest.generated_at,
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            classifier_version=CLASSIFIER_VERSION,
            used_gemini=gemini is not None,
            used_tavily=tavily is not None,
        ),
        summary=GapClassificationSummary(
            classified_gaps=len(classified),
            confirmed=sum(1 for gap in classified if gap.classification_status == "confirmed"),
            provisional=sum(1 for gap in classified if gap.classification_status == "provisional"),
            conflicted=sum(1 for gap in classified if gap.classification_status == "conflicted"),
            insufficient=sum(
                1 for gap in classified if gap.classification_status == "insufficient"
            ),
        ),
        classified_gaps=classified,
    )


def write_gap_classification(classification: GapClassification, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(classification.model_dump(mode="json"), indent=2) + "\n")
    return path


def _read_optional_gemini(path: Path | None) -> GeminiAnalysis | None:
    if path is None or not path.exists():
        return None
    return GeminiAnalysis.model_validate_json(path.read_text())


def _read_optional_tavily(path: Path | None) -> TavilyEvidence | None:
    if path is None or not path.exists():
        return None
    return TavilyEvidence.model_validate_json(path.read_text())


def main(
    study: Annotated[
        Path,
        typer.Option("--study", help="Path to Step 2 study_ssot.json."),
    ] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[
        Path,
        typer.Option("--manifest", help="Path to Step 2 manifest.json."),
    ] = Path("data/generated/manifest.json"),
    out: Annotated[
        Path,
        typer.Option("--out", help="Directory for gap_classification.json."),
    ] = Path("data/generated"),
    gemini: Annotated[
        Path | None,
        typer.Option("--gemini", help="Optional gemini_analysis.json path."),
    ] = None,
    tavily: Annotated[
        Path | None,
        typer.Option("--tavily", help="Optional tavily_evidence.json path."),
    ] = None,
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Classify gap types from local artifacts without network calls."""

    study_artifact = StudySsot.model_validate_json(study.read_text())
    manifest_artifact = Manifest.model_validate_json(manifest.read_text())
    classification = build_gap_classification(
        study_artifact,
        manifest_artifact,
        gemini=_read_optional_gemini(gemini),
        tavily=_read_optional_tavily(tavily),
        generated_at=parse_generated_at(generated_at) if generated_at else None,
    )
    path = write_gap_classification(classification, out)
    console.print(f"[green]wrote[/green] {path}")
    console.print(
        "[yellow]Review before tracking:[/yellow] this file is gitignored until "
        "a reviewed SSOT refresh step promotes it."
    )


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
