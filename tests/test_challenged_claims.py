"""Tests for the challenged claims guardrail system."""

from __future__ import annotations

from presence_rx.build_challenged_claims import build_challenged_claims
from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.contracts import ClaimStatus, EvidenceLedger
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def _classification():
    artifacts = _artifacts()
    return build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=None,
        tavily=None,
    )


def test_challenged_ownership_claim_blocked_when_visibility_low() -> None:
    """Minimalist Hardware (6%, Apple) should be BLOCKED."""
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    minimalist_results = [
        (claim, blocked)
        for claim, blocked in results
        if claim.cluster_id == "cluster:minimalist-hardware"
    ]
    assert len(minimalist_results) == 1
    claim, blocked = minimalist_results[0]

    assert claim.status == ClaimStatus.BLOCKED
    assert "minimalist" in blocked.blocked_reason.lower() or "Minimalist" in blocked.blocked_reason
    assert "Apple" in blocked.blocked_reason
    assert "6%" in blocked.blocked_reason
    assert "39%" in blocked.blocked_reason


def test_challenged_claim_not_generated_for_stronghold() -> None:
    """Smartphone Design (72%, no competitor) should not produce a blocked claim."""
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    # Smartphone Design is a stronghold (72% visibility, no competitor_owner),
    # and it is not in CHALLENGED_CLAIMS. Verify no blocked claim has that cluster.
    cluster_ids = {claim.cluster_id for claim, _ in results}
    assert "cluster:smartphone-design" not in cluster_ids


def test_blocked_claim_has_specific_safe_rewrite() -> None:
    """safe_rewrite should mention the topic and be cautious."""
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    for _claim, blocked in results:
        # safe_rewrite must be different from the tempting claim
        assert blocked.safe_rewrite != blocked.claim

        # Must mention the topic area (case-insensitive)
        assert "emerging" in blocked.safe_rewrite.lower()
        assert "behind" in blocked.safe_rewrite.lower()

        # Must not contain ownership superlatives
        assert "go-to" not in blocked.safe_rewrite
        assert "leading" not in blocked.safe_rewrite
        assert "leads" not in blocked.safe_rewrite


def test_blocked_claim_has_gap_type_specific_next_evidence() -> None:
    """perception gap -> positioning content; volume gap -> editorial coverage."""
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    by_cluster = {claim.cluster_id: blocked for claim, blocked in results}

    # Minimalist Hardware has gap_type=perception
    minimalist = by_cluster.get("cluster:minimalist-hardware")
    assert minimalist is not None
    assert "positioning content" in minimalist.next_evidence_to_collect.lower()

    # Wireless Audio has gap_type=volume_frequency
    audio = by_cluster.get("cluster:wireless-audio")
    assert audio is not None
    assert "editorial coverage" in audio.next_evidence_to_collect.lower()

    # Consumer Tech Innovation has gap_type=perception
    innovation = by_cluster.get("cluster:consumer-tech-innovation")
    assert innovation is not None
    assert "positioning content" in innovation.next_evidence_to_collect.lower()


def test_evidence_ledger_integrates_challenged_claims() -> None:
    """Build full ledger with challenged claims; verify blocked_claims
    populated and validator passes."""
    artifacts = _artifacts()
    classification = _classification()

    challenged = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)
    assert len(challenged) > 0, "test expects at least one challenged claim"

    ledger = build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        classification,
        challenged_claims=challenged,
    )

    # The challenged blocked claims should be in the ledger
    challenged_ids = {claim.claim_id for claim, _ in challenged}
    ledger_blocked_ids = {bc.claim_id for bc in ledger.blocked_claims}
    assert challenged_ids.issubset(ledger_blocked_ids)

    # The mirrored Claim entries should be in the ledger claims
    ledger_blocked_claim_ids = {
        c.claim_id for c in ledger.claims if c.status == ClaimStatus.BLOCKED
    }
    assert challenged_ids.issubset(ledger_blocked_claim_ids)

    # Pydantic validator should pass (it checks every BLOCKED claim has a mirror)
    EvidenceLedger.model_validate(ledger.model_dump(mode="json"))
