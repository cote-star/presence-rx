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
    GeminiAnalysis,
    Manifest,
    PrescriptionPlan,
    StudySsot,
    TavilyEvidence,
    ValueAddedMetrics,
)
from presence_rx.display_labels import human_decision
from presence_rx.display_labels import human_gap_type as human_gap

console = Console()

OUTPUT_NAME = "ACTION_BRIEF.md"

GAP_TYPE_NAMES = {
    GapType.PERCEPTION: "Perception",
    GapType.INDEXING: "Discovery",
    GapType.VOLUME_FREQUENCY: "Attention",
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
    gemini: GeminiAnalysis | None = None,
    tavily: TavilyEvidence | None = None,
) -> str:
    """Build the Action Brief markdown from pipeline artifacts."""
    brand = manifest.brand
    claims = ledger.claims if ledger else []
    blocked_claims = ledger.blocked_claims if ledger else []
    classified = classification.classified_gaps if classification else []
    metric_map = {r.cluster_id: r for r in metrics.rows} if metrics else {}
    findings = {f.cluster_id: f for f in gemini.findings} if gemini else {}
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
                    f"- **Evidence Level:** {gap_info.classification_status} "
                    f"({gap_info.confidence_tier})"
                )

            # Value metrics
            if vm:
                lines.append(
                    f"- **Recommended Action:** {human_decision(vm.decision_bucket)}"
                )
                lines.append(f"- **Reason:** {vm.decision_bucket_reason}")
                lines.append(f"- **Recommended next move:** {vm.recommended_next_move}")
                lines.append(f"- **Action Priority:** {vm.opportunity_score}/100")

            # Claim language
            claim = next(
                (c for c in claims if c.cluster_id == row.cluster_id), None
            )
            if claim:
                lines.append(f"- **Publication language:** {claim.publication_language}")

            # Gemini perception themes
            finding = findings.get(row.cluster_id)
            if finding:
                for theme in finding.perception_themes:
                    lines.append(f"- **AI perception:** {theme}")
                for assoc in finding.missing_associations:
                    lines.append(f"- **Missing association:** {assoc}")

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
                f"| {topic.name} | {human_gap(topic.gap_type)} | {topic.source_cluster_id} |"
            )
        lines.append("")

        lines.append("### Planned Prompts (sample)\n")
        lines.append("| Prompt | Country | Gap Type |")
        lines.append("|--------|---------|----------|")
        for prompt in prescription.planned_prompts[:6]:
            gt = human_gap(prompt.gap_type)
            lines.append(
                f"| {prompt.text[:80]}... | {prompt.country_code} | {gt} |"
            )
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

    # Data Sources provenance
    lines.append("### Data Sources\n")
    peec_src = manifest.sources.get("peec")
    peec_label = (
        f"verified snapshot ({manifest.generated_at.strftime('%Y-%m-%d')})"
    )
    if peec_src and peec_src.snapshot_id:
        peec_label = (
            f"verified snapshot `{peec_src.snapshot_id}` "
            f"({manifest.generated_at.strftime('%Y-%m-%d')})"
        )
    lines.append(f"- **Peec MCP:** {peec_label}")

    tavily_available = tavily is not None and tavily.summary.sources > 0
    if tavily_available:
        query_count = tavily.metadata.request_count
        source_count = tavily.summary.sources
        resp_time = tavily.metadata.response_time_seconds
        tavily_label = f"live ({query_count} queries, {source_count} sources"
        if resp_time is not None:
            tavily_label += f", {resp_time:.2f}s response time"
        tavily_label += ")"
        lines.append(f"- **Tavily:** {tavily_label}")
    else:
        tavily_src = manifest.sources.get("tavily")
        if tavily_src and (tavily_src.query_count or 0) > 0 and (tavily_src.source_count or 0) > 0:
            q = tavily_src.query_count or 0
            s = tavily_src.source_count or 0
            lines.append(f"- **Tavily:** manifest ({q} queries, {s} sources)")
        else:
            lines.append("- **Tavily:** not available")

    if gemini is not None:
        run_mode = gemini.metadata.run_mode
        if run_mode == "test":
            if tavily_available:
                gemini_grounding = "findings grounded in Peec + Tavily data"
            else:
                gemini_grounding = "findings grounded in Peec data only"
            lines.append(
                f"- **Gemini:** substitute (API quota exhausted; "
                f"{gemini_grounding})"
            )
        else:
            lines.append(
                f"- **Gemini:** live ({gemini.metadata.request_count} requests, "
                f"model {gemini.metadata.requested_model})"
            )
    else:
        lines.append("- **Gemini:** unavailable")
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
    gemini: Annotated[Path | None, typer.Option("--gemini")] = None,
    tavily: Annotated[Path | None, typer.Option("--tavily")] = None,
) -> None:
    """Generate ACTION_BRIEF.md from pipeline artifacts."""
    content = build_action_brief(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        ledger=_read_optional(ledger, EvidenceLedger),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        prescription=_read_optional(prescription, PrescriptionPlan),
        gemini=_read_optional(gemini, GeminiAnalysis),
        tavily=_read_optional(tavily, TavilyEvidence),
    )
    path = write_action_brief(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
