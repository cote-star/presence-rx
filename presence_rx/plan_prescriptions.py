"""Build non-mutating Peec prescription plans from Step 2 artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    GapType,
    Manifest,
    PlannedPrompt,
    PlannedTag,
    PlannedTopic,
    PrescriptionMetadata,
    PrescriptionPlan,
    PrescriptionSummary,
    StudyRow,
    StudySsot,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

COUNTRY_CODES = ("US", "DE", "GB")
GAP_TAGS: dict[GapType, tuple[str, str]] = {
    GapType.PERCEPTION: (
        "gap-perception",
        "Blind spots where the brand association is missing or weaker than competitors.",
    ),
    GapType.INDEXING: (
        "gap-indexing",
        "Blind spots where owned or credible sources need better AI-answer surfacing.",
    ),
    GapType.VOLUME_FREQUENCY: (
        "gap-volume-frequency",
        "Blind spots where public proof and repeated category presence are too sparse.",
    ),
}
GEO_TAGS = {
    "US": "Marks planned operations targeting the United States market.",
    "DE": "Marks planned operations targeting the Germany market.",
    "GB": "Marks planned operations targeting the Great Britain market.",
}
PROMPT_TEMPLATES: dict[GapType, str] = {
    GapType.PERCEPTION: (
        "Which {topic} options should buyers consider when they want "
        "distinctive alternatives to {competitor_owner}?"
    ),
    GapType.INDEXING: (
        "Which {topic} options should buyers consider when they want "
        "credible alternatives in the category?"
    ),
    GapType.VOLUME_FREQUENCY: (
        "Which {topic} options should buyers consider when they want "
        "proven alternatives to the market leader?"
    ),
}


def _study_row_ref(row: StudyRow) -> str:
    return f"study_ssot:row:{row.cluster_id.removeprefix('cluster:')}"


def _topic_ref(row: StudyRow) -> str:
    return f"peec:topic:{slugify(row.cluster_label)}"


def _evidence_refs(row: StudyRow, manifest: Manifest) -> list[str]:
    refs = [manifest.peec_snapshot_id, _topic_ref(row), _study_row_ref(row)]
    return list(dict.fromkeys(refs))


def _blind_spot_rows(study: StudySsot) -> list[StudyRow]:
    return [row for row in study.rows if row.gap_type is not None]


def _planned_topic_name(row: StudyRow) -> str:
    return f"bbh-2026-{slugify(row.cluster_label)}"


def _planned_prompt_text(row: StudyRow) -> str:
    if row.gap_type is None:
        raise ValueError("cannot create planned prompt for row without gap_type")
    return PROMPT_TEMPLATES[row.gap_type].format(
        topic=row.cluster_label.lower(),
        competitor_owner=row.visibility_competitor_owner or "leading competitors",
    )


def build_prescription_plan(
    study: StudySsot,
    manifest: Manifest,
    generated_at: datetime | None = None,
) -> PrescriptionPlan:
    resolved_generated_at = generated_at or manifest.generated_at
    blind_spots = _blind_spot_rows(study)
    gap_types = sorted({row.gap_type for row in blind_spots if row.gap_type}, key=str)

    planned_topics = [
        PlannedTopic(
            operation_id=f"op:create_topic:{slugify(row.cluster_label)}",
            execution_status="planned",
            topic_slug=slugify(row.cluster_label),
            name=_planned_topic_name(row),
            source_cluster_id=row.cluster_id,
            gap_type=row.gap_type,
            evidence_refs=_evidence_refs(row, manifest),
        )
        for row in blind_spots
        if row.gap_type is not None
    ]

    planned_tags = [
        PlannedTag(
            operation_id=f"op:create_tag:{GAP_TAGS[gap_type][0]}",
            execution_status="planned",
            tag_slug=GAP_TAGS[gap_type][0],
            name=f"bbh-2026-{GAP_TAGS[gap_type][0]}",
            kind="gap",
            description=GAP_TAGS[gap_type][1],
        )
        for gap_type in gap_types
    ] + [
        PlannedTag(
            operation_id=f"op:create_tag:geo-{country_code.lower()}",
            execution_status="planned",
            tag_slug=f"geo-{country_code.lower()}",
            name=f"bbh-2026-geo-{country_code.lower()}",
            kind="geo",
            description=description,
        )
        for country_code, description in GEO_TAGS.items()
    ]

    planned_prompts: list[PlannedPrompt] = []
    for row in blind_spots:
        if row.gap_type is None:
            continue
        topic_slug = slugify(row.cluster_label)
        gap_tag_slug = GAP_TAGS[row.gap_type][0]
        for country_code in COUNTRY_CODES:
            country_slug = country_code.lower()
            planned_prompts.append(
                PlannedPrompt(
                    operation_id=f"op:create_prompt:{topic_slug}:{country_slug}",
                    execution_status="planned",
                    prompt_slug=f"{topic_slug}:{country_slug}",
                    text=_planned_prompt_text(row),
                    prompt_language="en",
                    prompt_text_source="templated",
                    country_code=country_code,
                    topic_slug=topic_slug,
                    gap_type=row.gap_type,
                    tag_refs=[gap_tag_slug, f"geo-{country_slug}"],
                    source_cluster_id=row.cluster_id,
                    evidence_refs=_evidence_refs(row, manifest),
                )
            )

    return PrescriptionPlan(
        metadata=PrescriptionMetadata(
            generated_at=resolved_generated_at,
            source_manifest_ref=str(manifest.peec_snapshot_id),
            peec_snapshot_id=manifest.peec_snapshot_id,
        ),
        summary=PrescriptionSummary(
            planned_prompts=len(planned_prompts),
            planned_topics=len(planned_topics),
            planned_tags=len(planned_tags),
        ),
        planned_topics=planned_topics,
        planned_tags=planned_tags,
        planned_prompts=planned_prompts,
    )


def write_prescription_plan(plan: PrescriptionPlan, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / "prescription_plan.json"
    path.write_text(json.dumps(plan.model_dump(mode="json"), indent=2) + "\n")
    return path


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
        typer.Option("--out", help="Directory for prescription_plan.json."),
    ] = Path("data/generated"),
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Generate a non-mutating Peec prescription plan."""

    study_artifact = StudySsot.model_validate_json(study.read_text())
    manifest_artifact = Manifest.model_validate_json(manifest.read_text())
    resolved_generated_at = parse_generated_at(generated_at) if generated_at else None
    plan = build_prescription_plan(
        study_artifact,
        manifest_artifact,
        generated_at=resolved_generated_at,
    )
    path = write_prescription_plan(plan, out)
    console.print(f"[green]wrote[/green] {path}")


if __name__ == "__main__":
    typer.run(main)
