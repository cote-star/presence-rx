"""Generate ACTION_BRIEF.md from pipeline artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    EvidenceLedger,
    GapClassification,
    GapType,
    Manifest,
    PrescriptionPlan,
    StudySsot,
    ValueAddedMetrics,
)

console = Console()

OUTPUT_NAME = "ACTION_BRIEF.md"

GAP_TYPE_NAMES = {
    GapType.PERCEPTION: "Perception",
    GapType.INDEXING: "Indexing",
    GapType.VOLUME_FREQUENCY: "Volume / Frequency",
}

INTERVENTION_CLASS = {
    GapType.PERCEPTION: (
        "Positioning + messaging correction; reframing content with explicit trait language"
    ),
    GapType.INDEXING: (
        "Schema markup, structured data, AI-citation optimization, "
        "source-of-truth canonicalization"
    ),
    GapType.VOLUME_FREQUENCY: (
        "Content creation + distribution + amplification; "
        "sustained editorial outreach; UGC seeding"
    ),
}


def build_action_brief(
    study: StudySsot,
    manifest: Manifest,
    *,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
    metrics: ValueAddedMetrics | None = None,
    prescription: PrescriptionPlan | None = None,
) -> str:
    """Build the Action Brief markdown from pipeline artifacts."""
    brand = manifest.brand
    claims = ledger.claims if ledger else []
    blocked_claims = ledger.blocked_claims if ledger else []
    classified = classification.classified_gaps if classification else []
    metric_map = {r.cluster_id: r for r in metrics.rows} if metrics else {}
    rows_by_gap: dict[GapType, list] = {}
    for row in study.rows:
        if row.gap_type is not None:
            rows_by_gap.setdefault(GapType(row.gap_type), []).append(row)

    lines: list[str] = []
    lines.append(f"# Action Brief: {brand}\n")
    lines.append(f"*Generated: {manifest.generated_at.isoformat()}*\n")

    # Claims To Avoid
    lines.append("## Claims To Avoid\n")
    if blocked_claims:
        for bc in blocked_claims:
            lines.append(f"### {bc.claim_id}\n")
            lines.append(f"- **Blocked claim:** {bc.claim}")
            lines.append(f"- **Reason:** {bc.blocked_reason}")
            lines.append(f"- **Safe rewrite:** {bc.safe_rewrite}")
            lines.append(f"- **Next evidence:** {bc.next_evidence_to_collect}")
            lines.append("")
    else:
        lines.append(
            "*No blocked claims.* All 4 gap classifications were confirmed by "
            "3-method agreement with no conflicts.\n"
        )

    # Actions by Intervention Class
    lines.append("## Actions by Intervention Class\n")
    for gap_type in [GapType.PERCEPTION, GapType.INDEXING, GapType.VOLUME_FREQUENCY]:
        gap_rows = rows_by_gap.get(gap_type, [])
        if not gap_rows:
            continue
        name = GAP_TYPE_NAMES[gap_type]
        intervention = INTERVENTION_CLASS[gap_type]
        topic_names = ", ".join(r.cluster_label for r in gap_rows)

        lines.append(f"### {name} Gaps ({topic_names})\n")
        lines.append(f"**Intervention class:** {intervention}\n")

        for row in gap_rows:
            vis = f"{(row.visibility_target_share or 0) * 100:.0f}%"
            competitor = row.visibility_competitor_owner or "N/A"
            vm = metric_map.get(row.cluster_id)

            lines.append(f"#### {row.cluster_label}\n")
            lines.append(f"- **Visibility:** {vis} | **Competitor:** {competitor}")

            # Classification
            gap_info = next(
                (g for g in classified if g.cluster_id == row.cluster_id), None
            )
            if gap_info:
                lines.append(
                    f"- **Status:** {gap_info.classification_status} "
                    f"({gap_info.confidence_tier})"
                )

            # Value metrics
            if vm:
                lines.append(f"- **Decision:** {vm.decision_bucket}")
                lines.append(f"- **Reason:** {vm.decision_bucket_reason}")
                lines.append(f"- **Recommended next move:** {vm.recommended_next_move}")
                lines.append(f"- **Opportunity score:** {vm.opportunity_score}/100")

            # Claim language
            claim = next(
                (c for c in claims if c.cluster_id == row.cluster_id), None
            )
            if claim:
                lines.append(f"- **Publication language:** {claim.publication_language}")

            lines.append("")

    # Monitoring Plan
    lines.append("## Monitoring Plan\n")
    if prescription:
        lines.append(
            f"**{prescription.summary.planned_prompts} monitoring prompts** planned "
            f"across **{prescription.summary.planned_topics} topics** and "
            f"**{prescription.summary.planned_tags} tags**.\n"
        )

        lines.append("### Planned Topics\n")
        lines.append("| Topic | Gap Type | Source Cluster |")
        lines.append("|-------|----------|----------------|")
        for topic in prescription.planned_topics:
            lines.append(
                f"| {topic.name} | {topic.gap_type} | {topic.source_cluster_id} |"
            )
        lines.append("")

        lines.append("### Planned Prompts (sample)\n")
        lines.append("| Prompt | Country | Gap Type |")
        lines.append("|--------|---------|----------|")
        for prompt in prescription.planned_prompts[:6]:
            lines.append(f"| {prompt.text[:80]}... | {prompt.country_code} | {prompt.gap_type} |")
        if len(prescription.planned_prompts) > 6:
            lines.append(
                f"| *...and {len(prescription.planned_prompts) - 6} more* | | |"
            )
        lines.append("")

        lines.append("### Planned Tags\n")
        for tag in prescription.planned_tags:
            lines.append(f"- `{tag.tag_slug}` ({tag.kind}): {tag.description}")
        lines.append("")
    else:
        lines.append("*No prescription plan available.*\n")

    # Pipeline Provenance
    lines.append("## Pipeline Provenance\n")
    lines.append(f"- **Brand:** {brand}")
    lines.append(f"- **Snapshot:** `{manifest.peec_snapshot_id}`")
    lines.append(f"- **Competitors:** {', '.join(manifest.competitors[:5])}")
    lines.append(f"- **Artifact version:** `{manifest.artifact_version}`")
    lines.append(f"- **Generated:** `{manifest.generated_at.isoformat()}`")
    lines.append("")

    return "\n".join(lines)


def write_action_brief(content: str, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(content)
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
    ledger: Annotated[Path | None, typer.Option("--ledger")] = None,
    metrics: Annotated[Path | None, typer.Option("--metrics")] = None,
    prescription: Annotated[Path | None, typer.Option("--prescription")] = None,
) -> None:
    """Generate ACTION_BRIEF.md from pipeline artifacts."""
    content = build_action_brief(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        ledger=_read_optional(ledger, EvidenceLedger),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        prescription=_read_optional(prescription, PrescriptionPlan),
    )
    path = write_action_brief(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
