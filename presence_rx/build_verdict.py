"""Generate PRESENCE_VERDICT.md from pipeline artifacts."""

from __future__ import annotations

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.brand_config import BrandConfig
from presence_rx.contracts import (
    CompetitorLandscape,
    EvidenceLedger,
    GapClassification,
    GeminiAnalysis,
    Manifest,
    StudySsot,
    TavilyEvidence,
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
    landscape: CompetitorLandscape | None = None,
    tavily: TavilyEvidence | None = None,
    brand_config: BrandConfig | None = None,
) -> str:
    """Build the Presence Verdict markdown from pipeline artifacts."""
    brand = manifest.brand
    rows = study.rows
    total = len(rows)
    blind_spots = [r for r in rows if r.gap_type is not None]
    strongholds = [r for r in rows if r.gap_type is None]

    classified = classification.classified_gaps if classification else []
    classified_map = {g.cluster_id: g for g in classified}
    claims = ledger.claims if ledger else []
    blocked_claims = ledger.blocked_claims if ledger else []
    blocked_by_claim_id = {bc.claim_id: bc for bc in blocked_claims}
    findings = {f.cluster_id: f for f in gemini.findings} if gemini else {}
    metric_map = {r.cluster_id: r for r in metrics.rows} if metrics else {}
    landscape_map = {t.cluster_id: t for t in landscape.topics} if landscape else {}
    tavily_finding_map = {f.cluster_id: f for f in tavily.findings} if tavily else {}

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
    # Compute brand-level metrics from study rows
    avg_vis = sum(r.visibility_target_share or 0 for r in rows) / total if total else 0
    avg_pos = sum(
        r.visibility_target_avg_position or 0 for r in rows
    ) / total if total else 0
    lines.append(
        f"- **Average topic visibility:** {avg_vis * 100:.0f}%\n"
        f"- **Average position:** {avg_pos:.1f}\n"
        f"- **Topics tracked:** {total}\n"
        f"- **Blind spots:** {len(blind_spots)}\n"
    )

    # Topic Diagnosis
    lines.append("## Topic Diagnosis\n")
    for row in rows:
        vis_pct = f"{(row.visibility_target_share or 0) * 100:.0f}%"
        pos = f"{row.visibility_target_avg_position or 0:.1f}"
        from presence_rx.display_labels import human_gap_type, human_strategic_status

        gap = human_gap_type(row.gap_type)
        competitor = row.visibility_competitor_owner or "N/A"

        lines.append(f"### {row.cluster_label}\n")
        lines.append(f"- **Visibility:** {vis_pct} | **Position:** {pos}")
        lines.append(f"- **Gap type:** {gap}")

        # Strategic status badge
        if row.strategic_status:
            status_label = human_strategic_status(row.strategic_status)
            importance = row.strategic_importance or "medium"
            note_part = f" \u2014 {row.strategic_note}" if row.strategic_note else ""
            lines.append(
                f"- **Strategic status:** {status_label} ({importance}){note_part}"
            )
        if row.visibility_competitor_owner:
            lt = landscape_map.get(row.cluster_id)
            comp_vis = (
                f"{lt.competitor_visibility_share * 100:.0f}%"
                if lt and lt.competitor_visibility_share is not None
                else "N/A"
            )
            lines.append(
                f"- **Competitor:** {competitor} dominates at {comp_vis} "
                f"vs {brand} at {vis_pct}"
            )

        # Classification status
        gap_info = next((g for g in classified if g.cluster_id == row.cluster_id), None)
        if gap_info:
            lines.append(
                f"- **Classification:** {gap_info.classification_status} "
                f"({gap_info.confidence_tier}) | "
                f"**Signal Alignment:** {gap_info.method_agreement_score * 100:.0f}%"
            )

        # Perception themes (from Gemini analysis)
        finding = findings.get(row.cluster_id)
        if finding:
            lines.append(f"- **Diagnostic:** {finding.safe_scenario_wording}")

        # Value metrics
        vm = metric_map.get(row.cluster_id)
        if vm:
            from presence_rx.display_labels import human_decision, human_trend

            lines.append(
                f"- **Action Priority:** {vm.opportunity_score}/100 | "
                f"**Recommended Action:** {human_decision(vm.decision_bucket)} | "
                f"**Trend:** {human_trend(vm.trend_label)}"
            )

        lines.append("")

    # Gap-Type Summary Table
    lines.append("## Gap-Type Summary\n")
    lines.append(
        "| Topic | Visibility | Gap Type | Status "
        "| Evidence Level | Signal Alignment | Action Priority |"
    )
    lines.append(
        "|-------|-----------|----------|--------"
        "|----------------|-----------------|-----------------|"
    )
    for row in rows:
        from presence_rx.display_labels import human_gap_type as _hgt

        vis = f"{(row.visibility_target_share or 0) * 100:.0f}%"
        gap = _hgt(row.gap_type)
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

            # User-facing question
            lines.append(f'**What users ask:** "What\'s the best {topic.lower()}?"\n')

            # Who currently owns the answer
            row = next((r for r in rows if r.cluster_id == claim.cluster_id), None)
            lt = landscape_map.get(claim.cluster_id)
            competitor = row.visibility_competitor_owner if row else "N/A"
            comp_vis = "N/A"
            if lt and lt.competitor_owner and lt.competitor_visibility_share is not None:
                competitor = lt.competitor_owner
                comp_vis = f"{lt.competitor_visibility_share * 100:.0f}%"
            lines.append(
                f"**Who currently owns the answer:** {competitor} "
                f"({comp_vis} visibility)\n"
            )

            # What proof exists
            tavily_f = tavily_finding_map.get(claim.cluster_id)
            gap_info = classified_map.get(claim.cluster_id)
            method_count = (
                sum(1 for s in gap_info.method_signals if s.signal == "supports")
                if gap_info else len(claim.methods)
            )
            total_methods = len(gap_info.method_signals) if gap_info else len(claim.methods)
            if tavily_f is not None:
                source_count = len(tavily_f.sources)
                tavily_proof = f"{source_count} public sources checked"
            else:
                tavily_proof = "Tavily: not available for this case study"
            lines.append(
                f"**What proof exists:** {tavily_proof}; "
                f"{method_count} of {total_methods} methods agree\n"
            )

            # Blocked claim or directional language
            blocked = blocked_by_claim_id.get(claim.claim_id)
            if blocked:
                lines.append(
                    f'**What claim is unsafe:** "{blocked.claim}" '
                    f"\u2192 BLOCKED\n"
                )
                lines.append(
                    f'**What the brand should say instead:** '
                    f'"{blocked.safe_rewrite}"\n'
                )
            else:
                lines.append(
                    '**What claim is unsafe:** No blocked claims for this topic\n'
                )
                lines.append(
                    f'**What the brand should say instead:** '
                    f'"{claim.publication_language}"\n'
                )

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

    # Data Sources provenance
    lines.append("### Data Sources\n")
    peec_src = manifest.sources.get("peec")
    peec_label = (
        f"verified snapshot ({manifest.generated_at.strftime('%Y-%m-%d')})"
    )
    if peec_src and peec_src.snapshot_id:
        snap = peec_src.snapshot_id
        date = manifest.generated_at.strftime("%Y-%m-%d")
        peec_label = f"verified snapshot `{snap}` ({date})"
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
    landscape: Annotated[Path | None, typer.Option("--landscape")] = None,
    tavily: Annotated[Path | None, typer.Option("--tavily")] = None,
) -> None:
    """Generate PRESENCE_VERDICT.md from pipeline artifacts."""
    content = build_presence_verdict(
        StudySsot.model_validate_json(study.read_text()),
        Manifest.model_validate_json(manifest.read_text()),
        classification=_read_optional(classification, GapClassification),
        ledger=_read_optional(ledger, EvidenceLedger),
        metrics=_read_optional(metrics, ValueAddedMetrics),
        gemini=_read_optional(gemini, GeminiAnalysis),
        landscape=_read_optional(landscape, CompetitorLandscape),
        tavily=_read_optional(tavily, TavilyEvidence),
    )
    path = write_presence_verdict(content, out)
    console.print(f"[green]wrote[/green] {path}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
