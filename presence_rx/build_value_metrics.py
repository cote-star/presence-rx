"""Build MVP value-added metrics from local Presence Rx artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    GapClassification,
    GeminiAnalysis,
    Manifest,
    StudyRow,
    StudySsot,
    TavilyEvidence,
    ValueAddedMetrics,
    ValueMetricRow,
    ValueMetricsMetadata,
    ValueMetricsSummary,
)
from presence_rx.ingest_peec import parse_generated_at

console = Console()

OUTPUT_NAME = "value_added_metrics.json"
METRICS_VERSION = "value_added_metrics:v1"

# Nothing-Phone-specific trend context overrides (kept for backward compat).
# When the cluster_id matches, these take priority over _derive_trend_context().
TREND_CONTEXT: dict[str, dict[str, str]] = {
    "cluster:smartphone-design": {
        "parent_topic": "mobile_design_authority",
        "primary_gap": "NONE_STRONGHOLD",
        "recommended_next_move": (
            "Maintain monitoring and use this cluster as the comparison baseline."
        ),
    },
    "cluster:mobile-ecosystem": {
        "parent_topic": "ecosystem_integration",
        "primary_gap": "RETRIEVAL_NOT_CITATION",
        "recommended_next_move": (
            "Test schema, canonical source pages, and ecosystem prompts after the "
            "next Peec snapshot."
        ),
    },
    "cluster:consumer-tech-innovation": {
        "parent_topic": "consumer_innovation",
        "primary_gap": "MISSING_ASSOCIATION",
        "recommended_next_move": (
            "Publish explicit innovation proof and monitor whether AI answers adopt "
            "that association."
        ),
    },
    "cluster:minimalist-hardware": {
        "parent_topic": "minimalist_category_language",
        "primary_gap": "MISSING_ASSOCIATION",
        "recommended_next_move": (
            "Publish minimalist-hardware positioning content and rerun this prompt cluster."
        ),
    },
    "cluster:wireless-audio": {
        "parent_topic": "audio_credibility",
        "primary_gap": "MISSING_PUBLIC_VOLUME",
        "recommended_next_move": (
            "Seed sustained wireless-audio proof across editorial and owned surfaces."
        ),
    },
}


def _derive_trend_context(row: StudyRow) -> dict[str, str]:
    """Derive trend context from gap type -- works for any brand."""
    if row.gap_type is None:
        return {
            "parent_topic": "category_authority",
            "primary_gap": "NONE_STRONGHOLD",
            "recommended_next_move": (
                "Maintain monitoring and use this cluster as the comparison baseline."
            ),
        }
    if row.gap_type == "indexing":
        return {
            "parent_topic": "content_discoverability",
            "primary_gap": "RETRIEVAL_NOT_CITATION",
            "recommended_next_move": (
                f"Test schema, canonical source pages, and monitoring prompts "
                f"for {row.cluster_label}."
            ),
        }
    if row.gap_type == "perception":
        return {
            "parent_topic": "brand_association",
            "primary_gap": "MISSING_ASSOCIATION",
            "recommended_next_move": (
                f"Publish explicit {row.cluster_label.lower()} positioning content "
                f"and monitor AI adoption."
            ),
        }
    # volume_frequency
    return {
        "parent_topic": "category_presence",
        "primary_gap": "MISSING_PUBLIC_VOLUME",
        "recommended_next_move": (
            f"Seed sustained {row.cluster_label.lower()} proof across editorial "
            f"and owned surfaces."
        ),
    }


def _classification_map(
    classification: GapClassification | None,
) -> dict[str, object]:
    if classification is None:
        return {}
    return {gap.cluster_id: gap for gap in classification.classified_gaps}


def _tavily_map(tavily: TavilyEvidence | None) -> dict[str, object]:
    if tavily is None:
        return {}
    return {finding.cluster_id: finding for finding in tavily.findings}


def _parent_topic(row: StudyRow) -> str:
    if row.cluster_id in TREND_CONTEXT:
        return TREND_CONTEXT[row.cluster_id]["parent_topic"]
    return _derive_trend_context(row)["parent_topic"]


def _trend_label(
    row: StudyRow,
    classification_status: str,
    proof_strength_score: int,
) -> str:
    if row.gap_type is None:
        return "stronghold"
    if classification_status == "conflicted":
        return "contested"
    if proof_strength_score == 0:
        return "proof_gap"
    if (row.visibility_target_share or 0) < 0.15:
        return "blind_spot"
    return "watch"


def _trend_zone(
    row: StudyRow,
    trend_label: str,
) -> str:
    if trend_label in {"stronghold", "proof_gap", "contested"}:
        return trend_label
    if row.gap_type in {"perception", "indexing", "volume_frequency"}:
        return "slow_burn"
    return "snapshot_blind_spot"


def _zone_basis(trend_zone: str) -> str:
    if trend_zone == "contested":
        return "method_conflict"
    if trend_zone == "proof_gap":
        return "proof_coverage"
    return "single_snapshot_visibility"


def _decision_bucket(
    row: StudyRow,
    classification_status: str,
    proof_strength_score: int,
    method_agreement_score: int,
) -> tuple[str, str]:
    # Strategic intent overrides
    strategic_status = getattr(row, "strategic_status", None)
    if strategic_status == "non_priority":
        return "monitor", "Not a strategic priority for this brand"
    if strategic_status == "strategic_gap" and method_agreement_score >= 66:
        return "act_now", "Critical strategic gap with strong method agreement"
    if strategic_status == "owned_strength":
        return "monitor", "Defend this anchor position"

    if classification_status == "conflicted":
        return "block", "Partner methods conflict; keep the claim out of publication."
    if row.gap_type is None:
        return "monitor", "The target brand already owns this prompt cluster."
    if proof_strength_score == 0:
        return "test_next", "The signal is plausible but needs public proof before action."
    if method_agreement_score >= 100:
        return (
            "act_now",
            "Peec, Gemini, and Tavily agree on a clear prompt-cluster gap.",
        )
    return "test_next", "The gap is directionally useful but needs one more evidence layer."


def _primary_gap(row: StudyRow) -> str:
    context = TREND_CONTEXT.get(row.cluster_id)
    if context:
        return context["primary_gap"]
    return _derive_trend_context(row)["primary_gap"]


def _recommended_next_move(row: StudyRow) -> str:
    context = TREND_CONTEXT.get(row.cluster_id)
    if context:
        return context["recommended_next_move"]
    if row.action_recommendation:
        return row.action_recommendation
    return _derive_trend_context(row)["recommended_next_move"]


def _proof_strength_score(tavily_finding: object | None) -> int:
    if tavily_finding is None:
        return 0
    sources = getattr(tavily_finding, "sources", [])
    return min(100, len(sources) * 20)


def _source_trust_score(tavily_finding: object | None) -> int:
    if tavily_finding is None:
        return 0
    scores = [
        source.score
        for source in getattr(tavily_finding, "sources", [])
        if source.score is not None
    ]
    if not scores:
        return 0
    return round((sum(scores) / len(scores)) * 100)


def _method_agreement_score(classified_gap: object | None) -> int:
    if classified_gap is None:
        return 0
    return round(getattr(classified_gap, "method_agreement_score", 0) * 100)


def _relevance_score(row: StudyRow) -> int:
    if row.gap_type is None:
        return round((row.visibility_target_share or 0) * 100)
    visibility_gap = 1 - (row.visibility_target_share or 0)
    position_penalty = min(1, ((row.visibility_target_avg_position or 5) - 1) / 5)
    return round(visibility_gap * 70 + position_penalty * 30)


def _opportunity_score(
    relevance_score: int,
    source_trust_score: int,
    proof_strength_score: int,
    method_agreement_score: int,
) -> int:
    return round(
        relevance_score * 0.40
        + method_agreement_score * 0.30
        + proof_strength_score * 0.20
        + source_trust_score * 0.10
    )


def _row(
    study_row: StudyRow,
    classified_gap: object | None,
    tavily_finding: object | None,
) -> ValueMetricRow:
    relevance_score = _relevance_score(study_row)
    source_trust_score = _source_trust_score(tavily_finding)
    proof_strength_score = _proof_strength_score(tavily_finding)
    method_agreement_score = _method_agreement_score(classified_gap)
    opportunity_score = _opportunity_score(
        relevance_score,
        source_trust_score,
        proof_strength_score,
        method_agreement_score,
    )
    classification_status = getattr(classified_gap, "classification_status", "unclassified")
    trend_label = _trend_label(study_row, classification_status, proof_strength_score)
    trend_zone = _trend_zone(study_row, trend_label)
    decision_bucket, decision_bucket_reason = _decision_bucket(
        study_row,
        classification_status,
        proof_strength_score,
        method_agreement_score,
    )
    evidence_refs = (
        getattr(classified_gap, "evidence_refs", None)
        or study_row.evidence_refs
    )
    return ValueMetricRow(
        cluster_id=study_row.cluster_id,
        cluster_label=study_row.cluster_label,
        gap_type=study_row.gap_type,
        parent_topic=_parent_topic(study_row),
        trend_label=trend_label,
        trend_zone=trend_zone,
        zone_basis=_zone_basis(trend_zone),
        decision_bucket=decision_bucket,
        decision_bucket_reason=decision_bucket_reason,
        primary_gap=_primary_gap(study_row),
        recommended_next_move=_recommended_next_move(study_row),
        relevance_score=relevance_score,
        source_trust_score=source_trust_score,
        proof_strength_score=proof_strength_score,
        method_agreement_score=method_agreement_score,
        opportunity_score=opportunity_score,
        labeling_source="peec_mcp+gemini+tavily+derived",
        evidence_refs=list(dict.fromkeys(evidence_refs)),
        rationale=(
            "Mechanical MVP score from Peec visibility gap, method agreement, "
            "Tavily proof coverage, and source score."
        ),
    )


def build_value_added_metrics(
    study: StudySsot,
    manifest: Manifest,
    *,
    classification: GapClassification | None = None,
    gemini: GeminiAnalysis | None = None,
    tavily: TavilyEvidence | None = None,
    generated_at: datetime | None = None,
) -> ValueAddedMetrics:
    classifications = _classification_map(classification)
    tavily_findings = _tavily_map(tavily)
    rows = [
        _row(
            study_row,
            classifications.get(study_row.cluster_id),
            tavily_findings.get(study_row.cluster_id),
        )
        for study_row in study.rows
    ]
    average = (
        round(sum(row.opportunity_score for row in rows) / len(rows))
        if rows
        else 0
    )
    return ValueAddedMetrics(
        metadata=ValueMetricsMetadata(
            generated_at=generated_at or manifest.generated_at,
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            metrics_version=METRICS_VERSION,
            used_gemini=gemini is not None,
            used_tavily=tavily is not None,
            used_classification=classification is not None,
        ),
        summary=ValueMetricsSummary(
            rows=len(rows),
            average_opportunity_score=average,
            contested_rows=sum(1 for row in rows if row.trend_label == "contested"),
            proof_gap_rows=sum(1 for row in rows if row.trend_label == "proof_gap"),
        ),
        rows=rows,
    )


def write_value_added_metrics(metrics: ValueAddedMetrics, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(metrics.model_dump(mode="json"), indent=2) + "\n")
    return path


def _read_optional(path: Path | None, model):
    if path is None or not path.exists():
        return None
    return model.model_validate_json(path.read_text())


def main(
    study: Annotated[Path, typer.Option("--study")] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[Path, typer.Option("--manifest")] = Path("data/generated/manifest.json"),
    out: Annotated[Path, typer.Option("--out")] = Path("data/generated"),
    classification: Annotated[Path | None, typer.Option("--classification")] = None,
    gemini: Annotated[Path | None, typer.Option("--gemini")] = None,
    tavily: Annotated[Path | None, typer.Option("--tavily")] = None,
    generated_at: Annotated[str | None, typer.Option("--generated-at")] = None,
) -> None:
    metrics = build_value_added_metrics(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        gemini=_read_optional(gemini, GeminiAnalysis),
        tavily=_read_optional(tavily, TavilyEvidence),
        generated_at=parse_generated_at(generated_at) if generated_at else None,
    )
    path = write_value_added_metrics(metrics, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
