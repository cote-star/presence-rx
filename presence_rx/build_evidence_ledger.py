"""Build the guardrailed Evidence Ledger from local classification artifacts."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console

from presence_rx.contracts import (
    BlockedClaim,
    Claim,
    ClaimStatus,
    ClassifiedGap,
    EvidenceItem,
    EvidenceLedger,
    EvidenceLedgerMetadata,
    EvidenceTier,
    GapClassification,
    Manifest,
    MethodSignal,
    PublicationStatus,
    StudySsot,
)
from presence_rx.ingest_peec import parse_generated_at, slugify

console = Console()

OUTPUT_NAME = "EVIDENCE_LEDGER.json"
LEDGER_TEMPLATE_VERSION = "evidence_ledger:v1"


def _available_methods(signals: list[MethodSignal]) -> list[str]:
    return [signal.method for signal in signals if signal.signal != "unavailable"]


def _signal_counts(signals: list[MethodSignal]) -> tuple[int, int, int]:
    available = [signal for signal in signals if signal.signal != "unavailable"]
    supporting = sum(1 for signal in available if signal.signal == "supports")
    conflicts = sum(1 for signal in available if signal.signal == "conflicts")
    return supporting, len(available), conflicts


def _why_not_stronger(tier: EvidenceTier) -> str | None:
    if tier == EvidenceTier.STRONG:
        return None
    return (
        f"confidence_tier={tier.value}; needs reviewed multi-method support with "
        "no conflicts to reach strong"
    )


def _claim_status(gap: ClassifiedGap) -> tuple[ClaimStatus, PublicationStatus]:
    if gap.classification_status == "conflicted" or gap.confidence_tier == EvidenceTier.BLOCKED:
        return ClaimStatus.BLOCKED, PublicationStatus.BLOCKED
    if gap.classification_status in {"provisional", "insufficient"}:
        return ClaimStatus.INSUFFICIENT_EVIDENCE, PublicationStatus.DIAGNOSTICS_ONLY
    return ClaimStatus.DIRECTIONAL, PublicationStatus.DIRECTIONAL_WITH_CAVEAT


def _claim_text(brand: str, gap: ClassifiedGap, status: ClaimStatus) -> str:
    gap_type = gap.provisional_gap_type.value
    if status == ClaimStatus.BLOCKED:
        return (
            f"{gap.cluster_label} classification is contested; partner methods "
            "conflict and require review."
        )
    if status == ClaimStatus.INSUFFICIENT_EVIDENCE:
        return (
            f"{brand} has a provisional {gap_type} signal in {gap.cluster_label}; "
            "partner evidence is limited or unavailable."
        )
    return (
        f"{brand} has a {gap_type} blind spot in {gap.cluster_label}; "
        f"partner evidence is {gap.confidence_tier.value}."
    )


def _publication_language(brand: str, gap: ClassifiedGap, status: ClaimStatus) -> str:
    supporting, available, conflicts = _signal_counts(gap.method_signals)
    if status == ClaimStatus.BLOCKED:
        return (
            f"Do not claim {brand} ownership of the {gap.cluster_label} topic; "
            f"partner methods conflict ({conflicts} conflicts)."
        )
    if gap.confidence_tier == EvidenceTier.STRONG:
        return (
            f"Prioritize testing the {brand} association in the {gap.cluster_label} "
            f"topic; {supporting} of {available} methods support."
        )
    if gap.confidence_tier == EvidenceTier.MODERATE:
        return (
            f"Test the {brand} association in the {gap.cluster_label} topic; "
            f"{supporting} of {available} methods support."
        )
    return (
        f"Explore the {brand} association in the {gap.cluster_label} topic; "
        "partner evidence is limited."
    )


def _claim_id(brand: str, gap: ClassifiedGap) -> str:
    return f"claim:{slugify(brand)}:{slugify(gap.cluster_label)}:v1"


def _claim(brand: str, gap: ClassifiedGap) -> Claim:
    status, publication_status = _claim_status(gap)
    return Claim(
        claim_id=_claim_id(brand, gap),
        claim=_claim_text(brand, gap, status),
        status=status,
        cluster_id=gap.cluster_id,
        methods=_available_methods(gap.method_signals),
        evidence_refs=gap.evidence_refs,
        confidence_tier=gap.confidence_tier,
        publication_status=publication_status,
        publication_language=_publication_language(brand, gap, status),
        why_not_stronger=_why_not_stronger(gap.confidence_tier),
    )


def _blocked_claim(brand: str, gap: ClassifiedGap, claim: Claim) -> BlockedClaim:
    return BlockedClaim(
        claim_id=claim.claim_id,
        claim=claim.claim,
        blocked_reason="METHOD_CONFLICT",
        safe_rewrite=(
            f"Explore the {brand} association in the {gap.cluster_label} topic; "
            "partner evidence is limited."
        ),
        next_evidence_to_collect=(
            f"Review Gemini and Tavily evidence for {gap.cluster_label}, then "
            "rerun classification after conflicts are resolved."
        ),
    )


def _source_type(evidence_ref: str) -> str:
    if evidence_ref.startswith("peec:"):
        return "peec_mcp"
    if evidence_ref.startswith("gemini:"):
        return "gemini"
    if evidence_ref.startswith("tavily:"):
        return "tavily"
    return "derived"


def _evidence_summary(evidence_ref: str) -> str:
    source_type = _source_type(evidence_ref)
    if source_type == "peec_mcp":
        return f"Peec reference carried from Step 7 classification: {evidence_ref}."
    if source_type == "gemini":
        return f"Gemini finding reference carried from Step 7 classification: {evidence_ref}."
    if source_type == "tavily":
        return f"Tavily evidence reference carried from Step 7 classification: {evidence_ref}."
    return f"Derived study reference carried from Step 7 classification: {evidence_ref}."


def _evidence_items(claims: list[Claim]) -> list[EvidenceItem]:
    refs: list[str] = []
    for claim in claims:
        refs.extend(claim.evidence_refs)
    return [
        EvidenceItem(
            evidence_ref=evidence_ref,
            source_type=_source_type(evidence_ref),
            summary=_evidence_summary(evidence_ref),
            url=None,
            confidence=None,
        )
        for evidence_ref in dict.fromkeys(refs)
    ]


def build_evidence_ledger(
    study: StudySsot,
    manifest: Manifest,
    classification: GapClassification,
    *,
    challenged_claims: list[tuple[Claim, BlockedClaim]] | None = None,
    generated_at: datetime | None = None,
) -> EvidenceLedger:
    study_cluster_ids = {row.cluster_id for row in study.rows}
    unknown_clusters = sorted(
        gap.cluster_id
        for gap in classification.classified_gaps
        if gap.cluster_id not in study_cluster_ids
    )
    if unknown_clusters:
        raise ValueError(
            "classification contains clusters not present in study_ssot: "
            + ", ".join(unknown_clusters)
        )

    claims = [_claim(manifest.brand, gap) for gap in classification.classified_gaps]
    claims_by_id = {claim.claim_id: claim for claim in claims}
    blocked_claims = [
        _blocked_claim(manifest.brand, gap, claims_by_id[_claim_id(manifest.brand, gap)])
        for gap in classification.classified_gaps
        if _claim_status(gap)[0] == ClaimStatus.BLOCKED
    ]
    if challenged_claims:
        for claim, blocked in challenged_claims:
            claims.append(claim)
            blocked_claims.append(blocked)
    return EvidenceLedger(
        metadata=EvidenceLedgerMetadata(
            source_manifest_ref=manifest.peec_snapshot_id,
            peec_snapshot_id=manifest.peec_snapshot_id,
            ledger_template_version=LEDGER_TEMPLATE_VERSION,
            used_classification=True,
            classifier_version=classification.metadata.classifier_version,
        ),
        generated_at=generated_at or manifest.generated_at,
        brand=manifest.brand,
        claims=claims,
        evidence=_evidence_items(claims),
        blocked_claims=blocked_claims,
    )


def write_evidence_ledger(ledger: EvidenceLedger, out_dir: Path) -> Path:
    out_dir.mkdir(parents=True, exist_ok=True)
    path = out_dir / OUTPUT_NAME
    path.write_text(json.dumps(ledger.model_dump(mode="json"), indent=2) + "\n")
    return path


def _read_required_text(path: Path, label: str) -> str:
    try:
        return path.read_text()
    except FileNotFoundError:
        raise typer.BadParameter(f"missing {label}: {path}") from None


def main(
    study: Annotated[
        Path,
        typer.Option("--study", help="Path to Step 2 study_ssot.json."),
    ] = Path("data/generated/study_ssot.json"),
    manifest: Annotated[
        Path,
        typer.Option("--manifest", help="Path to Step 2 manifest.json."),
    ] = Path("data/generated/manifest.json"),
    classification: Annotated[
        Path,
        typer.Option("--classification", help="Path to Step 7 gap_classification.json."),
    ] = Path("data/generated/gap_classification.json"),
    out: Annotated[
        Path,
        typer.Option("--out", help="Directory for EVIDENCE_LEDGER.json."),
    ] = Path("data/generated"),
    generated_at: Annotated[
        str | None,
        typer.Option("--generated-at", help="Optional ISO timestamp override."),
    ] = None,
) -> None:
    """Build a local Evidence Ledger without API calls."""

    study_artifact = StudySsot.model_validate_json(_read_required_text(study, "study"))
    manifest_artifact = Manifest.model_validate_json(
        _read_required_text(manifest, "manifest")
    )
    classification_artifact = GapClassification.model_validate_json(
        _read_required_text(classification, "classification")
    )
    ledger = build_evidence_ledger(
        study_artifact,
        manifest_artifact,
        classification_artifact,
        generated_at=parse_generated_at(generated_at) if generated_at else None,
    )
    path = write_evidence_ledger(ledger, out)
    console.print(f"[green]wrote[/green] {path}")
    console.print(
        "[yellow]Review before tracking:[/yellow] this file is gitignored until "
        "a reviewed verdict-pack step promotes it."
    )


def run() -> None:
    typer.run(main)


if __name__ == "__main__":
    run()
