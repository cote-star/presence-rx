"""Build a deterministic Gemini-shaped substitute when live Gemini is unavailable."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.analyze_gemini import OUTPUT_NAME, PROMPT_TEMPLATE_VERSION
from presence_rx.contracts import (
    GeminiAnalysis,
    GeminiFinding,
    GeminiMetadata,
    GeminiSummary,
    Manifest,
    StudyRow,
    StudySsot,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

SYNTHETIC_MODEL = "local-substitute:gemini-quota-fallback"


def _blind_spot_rows(study: StudySsot) -> list[StudyRow]:
    return [row for row in study.rows if row.gap_type is not None]


def _study_row_ref(row: StudyRow) -> str:
    return f"study_ssot:row:{row.cluster_id.removeprefix('cluster:')}"


def _topic_ref(row: StudyRow) -> str:
    return f"peec:topic:{slugify(row.cluster_label)}"


def _finding_id(row: StudyRow) -> str:
    return f"gemini:analysis:{slugify(row.cluster_label)}:v1"


def _themes(row: StudyRow) -> list[str]:
    if row.gap_type == "indexing":
        return [f"{row.cluster_label.lower()} discoverability", "owned content surfacing"]
    if row.gap_type == "volume_frequency":
        return [f"{row.cluster_label.lower()} presence", "category coverage depth"]
    return [f"{row.cluster_label.lower()} association", "category positioning"]


def _missing(row: StudyRow) -> list[str]:
    if row.gap_type == "indexing":
        return [f"clear {row.cluster_label.lower()} proof surfaced in AI answers"]
    if row.gap_type == "volume_frequency":
        return [f"repeated {row.cluster_label.lower()} association"]
    return [f"{row.cluster_label.lower()} association"]


def build_synthetic_gemini_analysis(
    study: StudySsot,
    manifest: Manifest,
    *,
    generated_at: datetime | None = None,
) -> GeminiAnalysis:
    findings = [
        GeminiFinding(
            finding_id=_finding_id(row),
            cluster_id=row.cluster_id,
            cluster_label=row.cluster_label,
            gap_type=row.gap_type,
            source_of_record="gemini",
            perception_themes=_themes(row),
            missing_associations=_missing(row),
            competitor_association=(
                f"{row.visibility_competitor_owner} is the Peec-visible owner"
                if row.visibility_competitor_owner
                else None
            ),
            safe_scenario_wording=(
                f"Treat {row.cluster_label} as a provisional diagnostic gap until live "
                "Gemini analysis is available."
            ),
            gap_type_support="supports",
            rationale=(
                "Local deterministic substitute used because live Gemini quota was unavailable; "
                "replace with a live Gemini run before public claims."
            ),
            evidence_refs=list(
                dict.fromkeys(
                    [
                        manifest.peec_snapshot_id,
                        _topic_ref(row),
                        _study_row_ref(row),
                        _finding_id(row),
                    ]
                )
            ),
        )
        for row in _blind_spot_rows(study)
        if row.gap_type is not None
    ]
    return GeminiAnalysis(
        metadata=GeminiMetadata(
            generated_at=generated_at or manifest.generated_at,
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            run_mode="test",
            requested_model=SYNTHETIC_MODEL,
            response_model_version=SYNTHETIC_MODEL,
            prompt_template_version=PROMPT_TEMPLATE_VERSION,
            temperature=0,
            request_count=len(findings),
            input_tokens=0,
            output_tokens=0,
            sdk_package="none",
            sdk_version="0",
        ),
        summary=GeminiSummary(
            analyzed_rows=len(findings),
            supported_gap_types=len(findings),
            conflicted_gap_types=0,
            insufficient_gap_types=0,
        ),
        findings=findings,
    )


def write_synthetic_gemini_analysis(analysis: GeminiAnalysis, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(analysis.model_dump(mode="json"), indent=2) + "\n")
    return path


def main(
    study: Annotated[Path, typer.Option("--study")] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[Path, typer.Option("--manifest")] = Path("data/generated/manifest.json"),
    out: Annotated[Path, typer.Option("--out")] = Path("data/generated"),
    generated_at: Annotated[str | None, typer.Option("--generated-at")] = None,
) -> None:
    analysis = build_synthetic_gemini_analysis(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        generated_at=parse_generated_at(generated_at) if generated_at else None,
    )
    path = write_synthetic_gemini_analysis(analysis, out)
    console.print(f"[yellow]wrote substitute[/yellow] {path}")
    console.print("[yellow]Replace this with a live Gemini artifact before public claims.[/yellow]")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
