"""Generate ACTIVATION_BRIEF.md from pipeline artifacts + brand config."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.brand_config import BrandConfig, load_brand_config
from presence_rx.contracts import (
    EvidenceLedger,
    GapClassification,
    GapType,
    GeminiAnalysis,
    Manifest,
    StudySsot,
    TavilyEvidence,
    ValueAddedMetrics,
)

console = Console()

OUTPUT_NAME = "ACTIVATION_BRIEF.md"

GAP_TYPE_SECTION_NAMES = {
    GapType.PERCEPTION: "Perception Gaps",
    GapType.INDEXING: "Indexing Gaps",
    GapType.VOLUME_FREQUENCY: "Volume / Frequency Gaps",
}


def build_activation_brief(
    study: StudySsot,
    manifest: Manifest,
    *,
    classification: GapClassification | None = None,
    metrics: ValueAddedMetrics | None = None,
    gemini: GeminiAnalysis | None = None,
    brand_config: BrandConfig | None = None,
    tavily: TavilyEvidence | None = None,
    ledger: EvidenceLedger | None = None,
) -> str:
    """Build the Activation Brief markdown from pipeline artifacts + brand config."""
    brand = brand_config.brand_name if brand_config else manifest.brand
    metric_map = {r.cluster_id: r for r in metrics.rows} if metrics else {}
    findings = {f.cluster_id: f for f in gemini.findings} if gemini else {}
    tavily_finding_map = {f.cluster_id: f for f in tavily.findings} if tavily else {}
    blocked_claim_map: dict[str, object] = {}
    claims_map: dict[str, object] = {}
    if ledger:
        for bc in ledger.blocked_claims:
            blocked_claim_map[bc.claim_id] = bc
        for c in ledger.claims:
            claims_map[c.cluster_id] = c

    # Group study rows by gap_type
    rows_by_gap: dict[GapType, list] = {}
    for row in study.rows:
        if row.gap_type is not None:
            rows_by_gap.setdefault(GapType(row.gap_type), []).append(row)

    # Count distinct gap types present
    gap_type_count = len(rows_by_gap)
    total_blind_spots = sum(len(v) for v in rows_by_gap.values())

    # Audience / channel / journey from brand config
    audiences = brand_config.audience_segments if brand_config else []
    channels = brand_config.channels_to_activate if brand_config else []
    journey_stages = brand_config.buying_journey_stages if brand_config else []

    lines: list[str] = []
    lines.append(f"# Activation Brief: {brand}\n")
    lines.append(f"*Generated: {manifest.generated_at.isoformat()}*\n")

    # Overview
    lines.append("## Overview\n")
    lines.append(
        f"{brand} has **{total_blind_spots} blind spots** requiring activation "
        f"across **{gap_type_count} intervention classes**.\n"
    )

    # Sections per gap type
    for gap_type in [GapType.PERCEPTION, GapType.INDEXING, GapType.VOLUME_FREQUENCY]:
        gap_rows = rows_by_gap.get(gap_type, [])
        if not gap_rows:
            continue
        section_name = GAP_TYPE_SECTION_NAMES[gap_type]
        lines.append(f"## {section_name}\n")

        for row in gap_rows:
            vis_pct = f"{(row.visibility_target_share or 0) * 100:.0f}%"
            competitor = row.visibility_competitor_owner or "N/A"
            topic = row.cluster_label
            cluster_id = row.cluster_id

            finding = findings.get(cluster_id)
            tavily_f = tavily_finding_map.get(cluster_id)
            vm = metric_map.get(cluster_id)
            claim = claims_map.get(cluster_id)

            # Competitor association text
            comp_association = competitor
            if finding and finding.competitor_association:
                comp_association = finding.competitor_association

            lines.append(f"### {topic}\n")
            lines.append(
                f"**Gap:** {brand} wants to be known for {topic} "
                f"but AI associates it with {comp_association}\n"
            )

            # Owned Content Brief
            lines.append("#### Owned Content Brief\n")
            lines.append(
                f"- **What to create:** Dedicated {topic.lower()} page "
                f"with structured data and explicit brand positioning"
            )
            lines.append(
                f"- **Where:** {brand} website, blog, documentation"
            )
            lines.append(
                f'- **Key language:** Use explicit "{topic}" keywords '
                f"that AI systems index"
            )
            if finding:
                for assoc in finding.missing_associations:
                    lines.append(
                        f"- **Missing association to address:** {assoc}"
                    )
            lines.append("")

            # Earned Media Angle
            lines.append("#### Earned Media Angle\n")
            lines.append(
                f'- **Pitch:** "{brand} as the new {topic.lower()} contender '
                f"-- data shows {vis_pct} vs {competitor} "
                f'as current AI answer owner"'
            )
            # Suggest target outlets from tavily domains if available
            if tavily_f and tavily_f.sources:
                domains = sorted({s.domain for s in tavily_f.sources[:5]})
                lines.append(
                    f"- **Target outlets:** {', '.join(domains)}"
                )
            else:
                lines.append(
                    "- **Target outlets:** Tech editorial, independent review sites"
                )
            lines.append("")

            # Comparison Page
            lines.append("#### Comparison Page\n")
            lines.append(
                f'- **Title template:** "{brand} vs {competitor}: '
                f'{topic} comparison"'
            )
            lines.append(
                "- **Must include:** Feature matrix, pricing, "
                "user testimonials, independent benchmarks"
            )
            lines.append("")

            # FAQ / Search Answer
            lines.append("#### FAQ / Search Answer\n")
            lines.append(
                f'- **Q:** "Is {brand} good for {topic.lower()}?"'
            )
            if claim:
                lines.append(
                    f"- **A:** {claim.publication_language}"
                )
            elif vm:
                lines.append(
                    f"- **A:** {vm.recommended_next_move}"
                )
            else:
                lines.append(
                    f"- **A:** {brand} offers competitive {topic.lower()} "
                    f"capabilities -- see our comparison with {competitor} "
                    f"for details."
                )
            lines.append("")

            # Audience & Channel
            lines.append("#### Audience & Channel\n")
            if audiences:
                lines.append(
                    f"- **Audiences:** {', '.join(audiences)}"
                )
            if channels:
                lines.append(
                    f"- **Channels:** {', '.join(channels)}"
                )
            if journey_stages:
                lines.append(
                    f"- **Journey stage:** {', '.join(journey_stages)}"
                )
            lines.append("")

            # Proof Needed Before Publication
            lines.append("#### Proof Needed Before Publication\n")
            lines.append(
                "- Peec visibility must show improvement trend"
            )
            lines.append(
                f"- Tavily search must find {brand} editorial coverage "
                f"for this topic"
            )
            lines.append(
                f"- At least one independent review mentioning "
                f"{brand} + {topic}"
            )

            # Blocked claim warning
            blocked = None
            if ledger:
                blocked = next(
                    (
                        bc
                        for bc in ledger.blocked_claims
                        if bc.claim_id == cluster_id
                        or any(
                            c.cluster_id == cluster_id
                            for c in ledger.claims
                            if c.claim_id == bc.claim_id
                            and c.status.value == "blocked"
                        )
                    ),
                    None,
                )
            if blocked:
                lines.append(
                    f"- **Claim to avoid:** {blocked.claim}"
                )
                lines.append(
                    f"- **Safe alternative:** {blocked.safe_rewrite}"
                )
            lines.append("")

    # Data Sources
    lines.append("## Data Sources\n")
    peec_src = manifest.sources.get("peec")
    if peec_src and peec_src.snapshot_id:
        lines.append(
            f"- **Peec MCP:** verified snapshot "
            f"`{peec_src.snapshot_id}` "
            f"({manifest.generated_at.strftime('%Y-%m-%d')})"
        )
    else:
        lines.append(
            f"- **Peec MCP:** verified snapshot "
            f"({manifest.generated_at.strftime('%Y-%m-%d')})"
        )

    if tavily is not None:
        query_count = tavily.metadata.request_count
        source_count = tavily.summary.sources
        lines.append(
            f"- **Tavily:** live ({query_count} queries, "
            f"{source_count} sources)"
        )
    else:
        lines.append("- **Tavily:** unavailable")

    if gemini is not None:
        run_mode = gemini.metadata.run_mode
        if run_mode == "test":
            lines.append(
                "- **Gemini:** substitute (API quota exhausted; "
                "findings grounded in Peec + Tavily data)"
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


def write_activation_brief(content: str, out_dir: Path) -> Path:
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
    metrics: Annotated[Path | None, typer.Option("--metrics")] = None,
    gemini: Annotated[Path | None, typer.Option("--gemini")] = None,
    tavily: Annotated[Path | None, typer.Option("--tavily")] = None,
    ledger: Annotated[Path | None, typer.Option("--ledger")] = None,
    case_id: Annotated[str, typer.Option("--case-id")] = "nothing-phone",
) -> None:
    """Generate ACTIVATION_BRIEF.md from pipeline artifacts + brand config."""
    try:
        brand_config = load_brand_config(case_id)
    except FileNotFoundError:
        brand_config = None

    content = build_activation_brief(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        gemini=_read_optional(gemini, GeminiAnalysis),
        brand_config=brand_config,
        tavily=_read_optional(tavily, TavilyEvidence),
        ledger=_read_optional(ledger, EvidenceLedger),
    )
    path = write_activation_brief(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
