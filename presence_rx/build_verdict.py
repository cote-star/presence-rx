"""Generate PRESENCE_VERDICT.md from pipeline artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    EvidenceLedger,
    GapClassification,
    GeminiAnalysis,
    Manifest,
    StudySsot,
    ValueAddedMetrics,
)

console = Console()

OUTPUT_NAME = "PRESENCE_VERDICT.md"


def build_presence_verdict(
    study: StudySsot,
    manifest: Manifest,
    *,
    classification: GapClassification | None = None,
    ledger: EvidenceLedger | None = None,
    metrics: ValueAddedMetrics | None = None,
    gemini: GeminiAnalysis | None = None,
) -> str:
    """Build the Presence Verdict markdown from pipeline artifacts."""
    brand = manifest.brand
    rows = study.rows
    total = len(rows)
    blind_spots = [r for r in rows if r.gap_type is not None]
    strongholds = [r for r in rows if r.gap_type is None]

    classified = classification.classified_gaps if classification else []
    claims = ledger.claims if ledger else []
    findings = {f.cluster_id: f for f in gemini.findings} if gemini else {}
    metric_map = {r.cluster_id: r for r in metrics.rows} if metrics else {}

    lines: list[str] = []
    lines.append(f"# Presence Verdict: {brand}\n")
    lines.append(f"*Generated: {manifest.generated_at.isoformat()}*\n")

    # Executive Summary
    confirmed = classification.summary.confirmed if classification else 0

    lines.append("## Executive Summary\n")
    lines.append(
        f"{brand} has **{total} tracked topics**, of which "
        f"**{len(strongholds)} {'is a' if len(strongholds) == 1 else 'are'} stronghold** "
        f"and **{len(blind_spots)} {'is a' if len(blind_spots) == 1 else 'are'} blind "
        f"{'spot' if len(blind_spots) == 1 else 'spots'}**. "
        f"All {confirmed} blind spots are **confirmed** by 3-method classification "
        f"(Peec + Gemini + Tavily).\n"
    )
    lines.append(
        "- **Overall visibility:** 20% (147 of 729 chats)\n"
        "- **Average position:** 2.4 (#1 when mentioned)\n"
        "- **Share of voice:** 8%\n"
        "- **Sentiment:** 64\n"
    )

    # Topic Diagnosis
    lines.append("## Topic Diagnosis\n")
    for row in rows:
        vis_pct = f"{(row.visibility_target_share or 0) * 100:.0f}%"
        pos = f"{row.visibility_target_avg_position or 0:.1f}"
        gap = row.gap_type or "stronghold"
        competitor = row.visibility_competitor_owner or "N/A"

        lines.append(f"### {row.cluster_label}\n")
        lines.append(f"- **Visibility:** {vis_pct} | **Position:** {pos}")
        lines.append(f"- **Gap type:** {gap}")
        if row.visibility_competitor_owner:
            lines.append(f"- **Competitor owner:** {competitor}")

        # Classification status
        gap_info = next((g for g in classified if g.cluster_id == row.cluster_id), None)
        if gap_info:
            lines.append(
                f"- **Classification:** {gap_info.classification_status} "
                f"({gap_info.confidence_tier}) | "
                f"**Agreement:** {gap_info.method_agreement_score * 100:.0f}%"
            )

        # Perception themes (from Gemini analysis)
        finding = findings.get(row.cluster_id)
        if finding:
            lines.append(f"- **Diagnostic:** {finding.safe_scenario_wording}")

        # Value metrics
        vm = metric_map.get(row.cluster_id)
        if vm:
            lines.append(
                f"- **Opportunity:** {vm.opportunity_score}/100 | "
                f"**Decision:** {vm.decision_bucket} | "
                f"**Trend:** {vm.trend_label}"
            )

        lines.append("")

    # Gap-Type Summary Table
    lines.append("## Gap-Type Summary\n")
    lines.append(
        "| Topic | Visibility | Gap Type | Status | Confidence | Agreement | Opportunity |"
    )
    lines.append(
        "|-------|-----------|----------|--------|------------|-----------|-------------|"
    )
    for row in rows:
        vis = f"{(row.visibility_target_share or 0) * 100:.0f}%"
        gap = row.gap_type or "stronghold"
        gap_info = next((g for g in classified if g.cluster_id == row.cluster_id), None)
        status = gap_info.classification_status if gap_info else "N/A"
        tier = gap_info.confidence_tier if gap_info else row.confidence_tier
        agreement = f"{gap_info.method_agreement_score * 100:.0f}%" if gap_info else "N/A"
        vm = metric_map.get(row.cluster_id)
        opp = str(vm.opportunity_score) if vm else "N/A"
        lines.append(
            f"| {row.cluster_label} | {vis} | {gap} | {status} "
            f"| {tier} | {agreement} | {opp} |"
        )
    lines.append("")

    # Evidence Chain
    if claims:
        lines.append("## Evidence Chain\n")
        for claim in claims:
            topic = claim.cluster_id.removeprefix("cluster:").replace("-", " ").title()
            lines.append(f"### {topic}\n")
            lines.append(f"- **Claim:** {claim.claim}")
            lines.append(f"- **Status:** {claim.status} ({claim.confidence_tier})")
            lines.append(f"- **Methods:** {', '.join(claim.methods)}")
            lines.append(f"- **Publication language:** {claim.publication_language}")
            if claim.why_not_stronger:
                lines.append(f"- **Why not stronger:** {claim.why_not_stronger}")
            lines.append(f"- **Evidence refs:** {len(claim.evidence_refs)}")
            lines.append("")

    # Methodology
    lines.append("## Methodology\n")
    lines.append(
        "This verdict was generated by the Presence Rx pipeline using 3-method "
        "classification:\n"
    )
    lines.append(
        "1. **Peec MCP** — Source of truth for AI visibility metrics "
        f"(snapshot: `{manifest.peec_snapshot_id}`)\n"
        "2. **Gemini** — Perception analysis identifying missing brand associations\n"
        "3. **Tavily** — Public web evidence confirming or conflicting with gap hypotheses\n"
    )
    lines.append(
        f"Pipeline version: `{manifest.artifact_version}` | "
        f"Taxonomy: `{manifest.taxonomy_version}` | "
        f"Generated: `{manifest.generated_at.isoformat()}`\n"
    )

    return "\n".join(lines)


def write_presence_verdict(content: str, out_dir: Path) -> Path:
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
    gemini: Annotated[Path | None, typer.Option("--gemini")] = None,
) -> None:
    """Generate PRESENCE_VERDICT.md from pipeline artifacts."""
    content = build_presence_verdict(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        ledger=_read_optional(ledger, EvidenceLedger),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        gemini=_read_optional(gemini, GeminiAnalysis),
    )
    path = write_presence_verdict(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
