"""Generate challenged marketing claims and test them against Peec data."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    BlockedClaim,
    Claim,
    ClaimStatus,
    EvidenceTier,
    GapType,
    Manifest,
    PublicationStatus,
    StudyRow,
    StudySsot,
)
from presence_rx.ingest_peec import slugify

console = Console()

def _generate_challenged_claims(study: StudySsot, manifest: Manifest) -> list[dict]:
    """Generate tempting ownership claims from ANY brand's blind spots."""
    claims = []
    for row in study.rows:
        if row.gap_type and row.visibility_competitor_owner and row.desired_association:
            claims.append({
                "cluster_id": row.cluster_id,
                "tempting_claim": (
                    f"{manifest.brand} is the leading "
                    f"{row.cluster_label.lower()} brand"
                ),
                "claim_type": "ownership_superlative",
            })
    return claims


_NEXT_EVIDENCE_BY_GAP_TYPE: dict[GapType, str] = {
    GapType.PERCEPTION: "Publish explicit positioning content for this topic",
    GapType.INDEXING: "Improve schema markup and structured data for this topic",
    GapType.VOLUME_FREQUENCY: "Increase editorial and public coverage for this topic",
}

_DEFAULT_NEXT_EVIDENCE = "Collect additional Peec snapshots to establish trend"


def _find_study_row(study: StudySsot, cluster_id: str) -> StudyRow | None:
    for row in study.rows:
        if row.cluster_id == cluster_id:
            return row
    return None


def _safe_rewrite(brand: str, cluster_label: str, competitor: str) -> str:
    return (
        f"{brand} is emerging in the {cluster_label.lower()} category, "
        f"currently behind {competitor} in AI visibility."
    )


def _next_evidence(gap_type: GapType | None) -> str:
    if gap_type is None:
        return _DEFAULT_NEXT_EVIDENCE
    return _NEXT_EVIDENCE_BY_GAP_TYPE.get(gap_type, _DEFAULT_NEXT_EVIDENCE)


def _blocked_reason(
    brand: str, visibility: float, cluster_label: str, competitor: str,
    comp_vis: float | None,
) -> str:
    vis_pct = round(visibility * 100)
    if comp_vis is not None:
        comp_vis_pct = round(comp_vis * 100)
        return (
            f"OWNERSHIP_OVERCLAIM: {brand} has {vis_pct}% visibility in {cluster_label} "
            f"while {competitor} holds {comp_vis_pct}%. "
            "Claiming ownership is not supported by Peec data."
        )
    return (
        f"OWNERSHIP_OVERCLAIM: {brand} has {vis_pct}% visibility in {cluster_label} "
        f"while {competitor} owns the topic. "
        "Claiming ownership is not supported by Peec data."
    )


def build_challenged_claims(
    study: StudySsot,
    manifest: Manifest,
) -> list[tuple[Claim, BlockedClaim]]:
    """Evaluate tempting marketing claims against Peec study data.

    Returns a list of (Claim, BlockedClaim) pairs for each claim that fails
    the guardrail check (visibility < 20% AND a competitor owner exists).
    """
    brand = manifest.brand
    results: list[tuple[Claim, BlockedClaim]] = []
    challenged_claims = _generate_challenged_claims(study, manifest)

    for entry in challenged_claims:
        cluster_id = entry["cluster_id"]
        tempting_claim = entry["tempting_claim"]

        row = _find_study_row(study, cluster_id)
        if row is None:
            continue

        # Guardrail: block if visibility < 20% AND competitor owner exists
        if (
            row.visibility_target_share is not None
            and row.visibility_target_share < 0.20
            and row.visibility_competitor_owner
        ):
            claim_id = f"challenged:{slugify(row.cluster_label)}:v1"
            competitor = row.visibility_competitor_owner
            competitor_visibility = _estimate_competitor_visibility(study, row)

            reason = _blocked_reason(
                brand,
                row.visibility_target_share,
                row.cluster_label,
                competitor,
                competitor_visibility,
            )

            claim = Claim(
                claim_id=claim_id,
                claim=tempting_claim,
                status=ClaimStatus.BLOCKED,
                cluster_id=cluster_id,
                methods=["peec"],
                evidence_refs=row.evidence_refs,
                confidence_tier=EvidenceTier.BLOCKED,
                publication_status=PublicationStatus.BLOCKED,
                publication_language=(
                    f"Do not claim {brand} ownership of the {row.cluster_label} topic; "
                    f"{competitor} holds dominant visibility."
                ),
                why_not_stronger=(
                    f"confidence_tier=blocked; {brand} visibility "
                    f"({round(row.visibility_target_share * 100)}%) is below the 20% "
                    f"ownership threshold while {competitor} dominates"
                ),
            )

            blocked = BlockedClaim(
                claim_id=claim_id,
                claim=tempting_claim,
                blocked_reason=reason,
                safe_rewrite=_safe_rewrite(brand, row.cluster_label, competitor),
                next_evidence_to_collect=_next_evidence(row.gap_type),
            )

            results.append((claim, blocked))

    return results


def _estimate_competitor_visibility(study: StudySsot, row: StudyRow) -> float | None:
    """Estimate competitor visibility from study data.

    Uses the shared COMPETITOR_VISIBILITY_BY_CLUSTER when available.
    Returns None when no competitor visibility data is known for the cluster.
    """
    from presence_rx.build_competitor_landscape import COMPETITOR_VISIBILITY_BY_CLUSTER

    return COMPETITOR_VISIBILITY_BY_CLUSTER.get(row.cluster_id)


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
        typer.Option("--out", help="Directory for challenged_claims.json."),
    ] = Path("data/generated"),
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Evaluate tempting marketing claims against Peec study data."""

    study_artifact = StudySsot.model_validate_json(study.read_text())
    manifest_artifact = Manifest.model_validate_json(manifest.read_text())

    results = build_challenged_claims(study_artifact, manifest_artifact)

    out.mkdir(parents=True, exist_ok=True)
    output_path = out / "challenged_claims.json"
    payload = [
        {
            "claim": claim.model_dump(mode="json"),
            "blocked_claim": blocked.model_dump(mode="json"),
        }
        for claim, blocked in results
    ]
    output_path.write_text(json.dumps(payload, indent=2) + "\n")
    console.print(f"[green]wrote[/green] {output_path}")
    evaluated = len(_generate_challenged_claims(study_artifact, manifest_artifact))
    console.print(f"  challenged claims evaluated: {evaluated}")
    console.print(f"  blocked: {len(results)}")


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
