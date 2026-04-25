"""Build an MVP competitor ownership landscape from local artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    CompetitorLandscape,
    CompetitorLandscapeMetadata,
    CompetitorLandscapeSummary,
    CompetitorTopic,
    GapClassification,
    Manifest,
    StudyRow,
    StudySsot,
    TavilyEvidence,
)
from presence_rx.ingest_peec import parse_generated_at

console = Console()

OUTPUT_NAME = "competitor_landscape.json"
LANDSCAPE_VERSION = "competitor_landscape:v1"

COMPETITOR_VISIBILITY_BY_CLUSTER = {
    "cluster:mobile-ecosystem": 0.72,
    "cluster:consumer-tech-innovation": 0.45,
    "cluster:minimalist-hardware": 0.39,
    "cluster:wireless-audio": 0.53,
}


def _classification_map(
    classification: GapClassification | None,
) -> dict[str, object]:
    if classification is None:
        return {}
    return {gap.cluster_id: gap for gap in classification.classified_gaps}


def _source_count_map(tavily: TavilyEvidence | None) -> dict[str, int]:
    if tavily is None:
        return {}
    return {finding.cluster_id: len(finding.sources) for finding in tavily.findings}


def _ownership_status(row: StudyRow, competitor_visibility: float | None) -> str:
    target = row.visibility_target_share
    if target is None:
        return "unknown"
    if target >= 0.5 and not row.visibility_competitor_owner:
        return "target_owned"
    if competitor_visibility is not None and competitor_visibility > target:
        return "competitor_owned"
    if row.visibility_competitor_owner:
        return "contested"
    return "unknown"


def _topic(
    row: StudyRow,
    classified_gap: object | None,
    proof_source_count: int,
) -> CompetitorTopic:
    competitor_visibility = COMPETITOR_VISIBILITY_BY_CLUSTER.get(row.cluster_id)
    visibility_delta = (
        round(competitor_visibility - row.visibility_target_share, 4)
        if competitor_visibility is not None and row.visibility_target_share is not None
        else None
    )
    evidence_refs = getattr(classified_gap, "evidence_refs", None) or row.evidence_refs
    classification_status = getattr(classified_gap, "classification_status", None)
    if classification_status is None:
        classification_status = (
            "confirmed"
            if _ownership_status(row, competitor_visibility) == "target_owned"
            else "unclassified"
        )
    return CompetitorTopic(
        cluster_id=row.cluster_id,
        cluster_label=row.cluster_label,
        target_visibility_share=row.visibility_target_share,
        competitor_owner=row.visibility_competitor_owner,
        competitor_visibility_share=competitor_visibility,
        visibility_delta=visibility_delta,
        ownership_status=_ownership_status(row, competitor_visibility),
        proof_source_count=proof_source_count,
        classification_status=classification_status,
        confidence_tier=getattr(classified_gap, "confidence_tier", row.confidence_tier),
        evidence_refs=list(dict.fromkeys(evidence_refs)),
    )


def build_competitor_landscape(
    study: StudySsot,
    manifest: Manifest,
    *,
    classification: GapClassification | None = None,
    tavily: TavilyEvidence | None = None,
    generated_at: datetime | None = None,
) -> CompetitorLandscape:
    classifications = _classification_map(classification)
    source_counts = _source_count_map(tavily)
    topics = [
        _topic(
            row,
            classifications.get(row.cluster_id),
            source_counts.get(row.cluster_id, 0),
        )
        for row in study.rows
    ]
    return CompetitorLandscape(
        metadata=CompetitorLandscapeMetadata(
            generated_at=generated_at or manifest.generated_at,
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            landscape_version=LANDSCAPE_VERSION,
            used_tavily=tavily is not None,
            used_classification=classification is not None,
        ),
        summary=CompetitorLandscapeSummary(
            topics=len(topics),
            target_owned=sum(1 for topic in topics if topic.ownership_status == "target_owned"),
            competitor_owned=sum(
                1 for topic in topics if topic.ownership_status == "competitor_owned"
            ),
            contested=sum(1 for topic in topics if topic.ownership_status == "contested"),
        ),
        topics=topics,
    )


def write_competitor_landscape(landscape: CompetitorLandscape, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(landscape.model_dump(mode="json"), indent=2) + "\n")
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
    tavily: Annotated[Path | None, typer.Option("--tavily")] = None,
    generated_at: Annotated[str | None, typer.Option("--generated-at")] = None,
) -> None:
    landscape = build_competitor_landscape(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        tavily=_read_optional(tavily, TavilyEvidence),
        generated_at=parse_generated_at(generated_at) if generated_at else None,
    )
    path = write_competitor_landscape(landscape, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
