"""Behavioral validation tests for the Presence Rx pipeline.

These tests prove the pipeline produces correct results for the RIGHT reasons,
not just that outputs match a schema.  Each test encodes a domain invariant
(e.g., "blind spots always score higher opportunity than strongholds") and
explains WHY the assertion matters in its docstring.
"""

from __future__ import annotations

from pathlib import Path

from presence_rx.build_action_brief import build_action_brief
from presence_rx.build_challenged_claims import build_challenged_claims
from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.build_verdict import build_presence_verdict
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.contracts import (
    ClaimStatus,
    GeminiAnalysis,
    TavilyEvidence,
)
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed
from presence_rx.plan_prescriptions import build_prescription_plan

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "generated"


# ---------------------------------------------------------------------------
# Shared helpers
# ---------------------------------------------------------------------------

def _artifacts():
    return build_artifacts(nothing_phone_seed())


def _classification_with_real_data(
    gemini: GeminiAnalysis | None = None,
    tavily: TavilyEvidence | None = None,
):
    artifacts = _artifacts()
    return build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
        gemini=gemini,
        tavily=tavily,
    )


def _load_real_gemini() -> GeminiAnalysis | None:
    path = DATA_DIR / "gemini_analysis.json"
    if not path.exists():
        return None
    return GeminiAnalysis.model_validate_json(path.read_text())


def _load_real_tavily() -> TavilyEvidence | None:
    path = DATA_DIR / "tavily_evidence.json"
    if not path.exists():
        return None
    return TavilyEvidence.model_validate_json(path.read_text())


# ===========================================================================
# 1. Opportunity score ordering
# ===========================================================================


def test_blind_spot_opportunity_higher_than_stronghold():
    """Blind spots should always have higher opportunity than strongholds.

    WHY: The whole product thesis is that blind spots represent untapped
    opportunity.  If the stronghold (72% visibility) scores higher than a
    blind spot (6-12%), the opportunity model is broken.
    """
    artifacts = _artifacts()
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    rows = {r.cluster_id: r for r in metrics.rows}

    stronghold = rows["cluster:smartphone-design"]
    for cluster_id, row in rows.items():
        if row.gap_type is not None:
            assert row.opportunity_score > stronghold.opportunity_score, (
                f"{cluster_id} opportunity {row.opportunity_score} should be > "
                f"stronghold {stronghold.opportunity_score}"
            )


# ===========================================================================
# 2. Ironic gap ranks high opportunity
# ===========================================================================


def test_ironic_gap_ranks_high_opportunity():
    """Minimalist Hardware -- brand IS about minimalism but only 6% visible -- should rank high.

    WHY: This is the single most compelling blind spot in the dataset.
    The brand's core identity (minimalism) is invisible in AI answers.
    If opportunity scoring does not surface this ironic gap near the top,
    the model fails at its primary job.
    """
    artifacts = _artifacts()
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    rows = {r.cluster_id: r for r in metrics.rows}

    minimalist = rows["cluster:minimalist-hardware"]
    # Must be in the top 2 opportunity scores (among the 5 clusters)
    sorted_by_opp = sorted(metrics.rows, key=lambda r: r.opportunity_score, reverse=True)
    top_two_ids = {r.cluster_id for r in sorted_by_opp[:2]}
    assert minimalist.cluster_id in top_two_ids, (
        f"Minimalist Hardware opportunity {minimalist.opportunity_score} "
        f"should be in top 2; actual ranking: "
        + ", ".join(f"{r.cluster_id}={r.opportunity_score}" for r in sorted_by_opp)
    )


# ===========================================================================
# 3. All four blind spots confirmed strong with Tavily+Gemini
# ===========================================================================


def test_all_blind_spots_confirmed_strong_with_both_methods():
    """With both gemini and tavily data, all 4 blind spots should be confirmed/strong.

    WHY: The real data files have all 4 findings returning 'supports' with
    both target and competitor roles present.  If classification does not
    promote all 4 to confirmed+strong, the decision table is wrong.
    """
    gemini = _load_real_gemini()
    tavily = _load_real_tavily()
    if gemini is None or tavily is None:
        import pytest
        pytest.skip("real gemini_analysis.json or tavily_evidence.json not available")

    classification = _classification_with_real_data(gemini=gemini, tavily=tavily)

    assert len(classification.classified_gaps) == 4, (
        f"expected 4 classified gaps, got {len(classification.classified_gaps)}"
    )
    for gap in classification.classified_gaps:
        assert gap.classification_status == "confirmed", (
            f"{gap.cluster_id} status is {gap.classification_status}, expected confirmed"
        )
        assert gap.confidence_tier == "strong", (
            f"{gap.cluster_id} confidence is {gap.confidence_tier}, expected strong"
        )


# ===========================================================================
# 4. Stronghold excluded from blind-spot classification
# ===========================================================================


def test_stronghold_not_in_classified_gaps():
    """Smartphone Design (72% visibility) should not appear in classified gaps.

    WHY: Only rows with gap_type != None enter classification.  If the
    stronghold leaks in, downstream claims and prescriptions are polluted
    with a topic that needs no intervention.
    """
    artifacts = _artifacts()
    classification = build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
    )

    classified_ids = {gap.cluster_id for gap in classification.classified_gaps}
    assert "cluster:smartphone-design" not in classified_ids, (
        "Smartphone Design (stronghold) should never appear in classified gaps"
    )


# ===========================================================================
# 5. Every claim traces to Peec source
# ===========================================================================


def test_every_claim_has_peec_evidence_ref():
    """Every claim must have at least one peec: evidence ref.

    WHY: Peec MCP is the source of truth for this pipeline.  If any claim
    lacks a peec: reference, it means the evidence chain is broken and
    the claim cannot be traced back to the authoritative visibility data.
    """
    artifacts = _artifacts()
    classification = build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
    )
    ledger = build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        classification,
    )

    for claim in ledger.claims:
        peec_refs = [ref for ref in claim.evidence_refs if ref.startswith("peec:")]
        assert len(peec_refs) >= 1, (
            f"Claim {claim.claim_id} has no peec: evidence ref; "
            f"refs = {claim.evidence_refs}"
        )


# ===========================================================================
# 6. Every blind-spot claim has Tavily evidence
# ===========================================================================


def test_every_gap_claim_has_tavily_evidence_ref():
    """Every non-stronghold claim must reference tavily evidence when tavily is available.

    WHY: Tavily provides the public-web confirmation layer.  When tavily
    data is available and all findings support, every blind-spot claim
    should carry a tavily: evidence ref to prove the web evidence was
    actually wired through.
    """
    gemini = _load_real_gemini()
    tavily = _load_real_tavily()
    if gemini is None or tavily is None:
        import pytest
        pytest.skip("real gemini_analysis.json or tavily_evidence.json not available")

    artifacts = _artifacts()
    classification = _classification_with_real_data(gemini=gemini, tavily=tavily)
    ledger = build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        classification,
    )

    for claim in ledger.claims:
        tavily_refs = [ref for ref in claim.evidence_refs if ref.startswith("tavily:")]
        assert len(tavily_refs) >= 1, (
            f"Claim {claim.claim_id} has no tavily: evidence ref despite tavily "
            f"data being available; refs = {claim.evidence_refs}"
        )


# ===========================================================================
# 7. Blocked claims guardrail behavioral
# ===========================================================================


def test_ownership_overclaim_blocked_for_every_blind_spot():
    """Every blind spot with competitor owner should have its challenged claim blocked.

    WHY: The challenged-claims system exists to catch tempting marketing
    overclaims.  All 3 challenged claims target clusters where the brand
    has < 20% visibility and a competitor owner.  All 3 must be blocked.
    """
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    assert len(results) == 4, (
        f"expected 4 blocked challenged claims, got {len(results)}"
    )
    for claim, blocked in results:
        assert claim.status == ClaimStatus.BLOCKED, (
            f"challenged claim {claim.claim_id} should be BLOCKED, got {claim.status}"
        )
        assert "OWNERSHIP_OVERCLAIM" in blocked.blocked_reason, (
            f"blocked reason for {claim.claim_id} should mention OWNERSHIP_OVERCLAIM; "
            f"got: {blocked.blocked_reason}"
        )


# ===========================================================================
# 8. Stronghold claim NOT blocked
# ===========================================================================


def test_no_blocked_claim_for_stronghold():
    """Smartphone Design (72% visibility) should never produce a blocked claim.

    WHY: The stronghold has high visibility and no competitor owner.
    Blocking a claim for a topic the brand actually owns would be a
    false positive in the guardrail system.
    """
    artifacts = _artifacts()
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    blocked_cluster_ids = {claim.cluster_id for claim, _ in results}
    assert "cluster:smartphone-design" not in blocked_cluster_ids, (
        "Smartphone Design stronghold should never produce a blocked claim"
    )


# ===========================================================================
# 9. Full pipeline integration
# ===========================================================================


def test_full_pipeline_produces_expected_artifact_counts():
    """End-to-end pipeline integration test.

    WHY: This is the integration smoke test.  It proves every pipeline
    step chains correctly and produces the exact expected counts:
    5 study rows, 4 classified gaps, 7 claims (4 directional + 3 blocked
    via challenged claims), 3 blocked claims from challenged system,
    5 metric rows, 4 planned topics.
    """
    artifacts = _artifacts()

    # Step 5: prescription plan
    prescription = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)

    # Step 7: classification (no enrichment -- provisional)
    classification = build_gap_classification(
        artifacts.study_ssot,
        artifacts.manifest,
    )

    # Step 9: challenged claims
    challenged = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)

    # Step 8: evidence ledger with challenged claims
    ledger = build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        classification,
        challenged_claims=challenged,
    )

    # Step 10: value metrics
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)

    # Step 11: verdict markdown
    verdict_md = build_presence_verdict(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
    )

    # Step 12: action brief markdown
    action_md = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
        prescription=prescription,
    )

    # Verify expected counts
    assert len(artifacts.study_ssot.rows) == 5, "expected 5 study rows"
    assert len(classification.classified_gaps) == 4, "expected 4 classified gaps"
    assert len(ledger.claims) == 8, (
        f"expected 8 claims (4 directional + 4 challenged), got {len(ledger.claims)}"
    )
    assert len(challenged) == 4, f"expected 4 challenged claims, got {len(challenged)}"
    assert len(ledger.blocked_claims) == 4, (
        f"expected 4 blocked claims from challenged system, got {len(ledger.blocked_claims)}"
    )
    assert len(metrics.rows) == 5, f"expected 5 metric rows, got {len(metrics.rows)}"
    assert len(prescription.planned_topics) == 4, (
        f"expected 4 planned topics, got {len(prescription.planned_topics)}"
    )

    # Markdown outputs are non-empty
    assert len(verdict_md) > 100, "verdict markdown should be substantial"
    assert len(action_md) > 100, "action brief markdown should be substantial"


# ===========================================================================
# 10. Markdown behavioral -- topics appear in correct sections
# ===========================================================================


def test_action_brief_groups_topics_by_gap_type():
    """Perception section has Minimalist+Innovation, Discovery has Mobile, Attention has Wireless.

    WHY: The action brief groups blind spots by intervention class
    (perception, discovery, attention).  If topics land in the
    wrong section, the recommended actions will be wrong.
    """
    artifacts = _artifacts()
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest,
    )
    ledger = build_evidence_ledger(
        artifacts.study_ssot, artifacts.manifest, classification,
    )
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    prescription = build_prescription_plan(artifacts.study_ssot, artifacts.manifest)

    md = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
        prescription=prescription,
    )

    # Find the Perception section and verify it contains the right topics
    perception_header = "### Perception Gaps"
    indexing_header = "### Discovery Gaps"
    volume_header = "### Attention Gaps"

    assert perception_header in md, f"Missing section: {perception_header}"
    assert indexing_header in md, f"Missing section: {indexing_header}"
    assert volume_header in md, f"Missing section: {volume_header}"

    # Perception section should list Minimalist Hardware and Consumer Tech Innovation
    perception_start = md.index(perception_header)
    indexing_start = md.index(indexing_header)
    perception_section = md[perception_start:indexing_start]
    assert "Minimalist Hardware" in perception_section, (
        "Minimalist Hardware should be in the Perception section"
    )
    assert "Consumer Tech Innovation" in perception_section, (
        "Consumer Tech Innovation should be in the Perception section"
    )

    # Discovery section should list Mobile Ecosystem
    volume_start = md.index(volume_header)
    discovery_section = md[indexing_start:volume_start]
    assert "Mobile Ecosystem" in discovery_section, (
        "Mobile Ecosystem should be in the Discovery section"
    )

    # Volume section should list Wireless Audio
    volume_section = md[volume_start:]
    assert "Wireless Audio" in volume_section, (
        "Wireless Audio should be in the Attention section"
    )


# ===========================================================================
# 11. Markdown behavioral -- blocked claims in action brief
# ===========================================================================


def test_action_brief_claims_to_avoid_populated():
    """After challenged claims, Claims To Avoid must have real blocked content.

    WHY: The 'Claims To Avoid' section is a critical guardrail deliverable.
    If it says 'No blocked claims' when there ARE challenged claims, the
    action brief is hiding risk from the user.
    """
    artifacts = _artifacts()
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest,
    )
    challenged = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)
    ledger = build_evidence_ledger(
        artifacts.study_ssot,
        artifacts.manifest,
        classification,
        challenged_claims=challenged,
    )

    md = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
    )

    assert "## Claims To Avoid" in md, "Missing Claims To Avoid section"
    assert "No blocked claims" not in md, (
        "Claims To Avoid says 'No blocked claims' but there are 3 challenged claims"
    )
    # Each challenged claim should appear
    for claim, blocked in challenged:
        assert blocked.claim in md, (
            f"Blocked claim text '{blocked.claim}' should appear in Claims To Avoid"
        )
        assert blocked.safe_rewrite in md, (
            f"Safe rewrite for {claim.claim_id} should appear in the action brief"
        )


# ===========================================================================
# 12. Verdict mentions all five topics
# ===========================================================================


def test_verdict_covers_all_topics():
    """All 5 cluster labels must appear in PRESENCE_VERDICT.md.

    WHY: The verdict is the executive deliverable.  If any topic is missing,
    the user gets an incomplete picture of their brand's AI presence.
    """
    artifacts = _artifacts()
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest,
    )
    ledger = build_evidence_ledger(
        artifacts.study_ssot, artifacts.manifest, classification,
    )
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)

    md = build_presence_verdict(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        ledger=ledger,
        metrics=metrics,
    )

    expected_labels = [
        "Smartphone Design",
        "Mobile Ecosystem",
        "Consumer Tech Innovation",
        "Minimalist Hardware",
        "Wireless Audio",
    ]
    for label in expected_labels:
        assert label in md, (
            f"Verdict should mention '{label}' but it is missing"
        )


# ===========================================================================
# 13. Tavily real-data behavioral (WI-1)
# ===========================================================================


def test_real_tavily_data_all_findings_support():
    """With actual tavily_evidence.json (both roles present), all findings should be 'supports'.

    WHY: The real Tavily data was collected with live queries.  All 4
    findings have both target and competitor source roles present and
    returned 'supports'.  This test pins that real-world observation
    so regressions in data parsing or schema changes are caught.
    """
    tavily = _load_real_tavily()
    if tavily is None:
        import pytest
        pytest.skip("real tavily_evidence.json not available")

    assert len(tavily.findings) == 4, (
        f"expected 4 tavily findings, got {len(tavily.findings)}"
    )
    for finding in tavily.findings:
        assert finding.public_proof_support == "supports", (
            f"Finding {finding.finding_id} has public_proof_support="
            f"{finding.public_proof_support}, expected 'supports'"
        )
        # Verify both source roles are present
        roles = {source.source_role for source in finding.sources}
        assert "target" in roles, (
            f"Finding {finding.finding_id} is missing target role sources"
        )
        assert "competitor" in roles, (
            f"Finding {finding.finding_id} is missing competitor role sources"
        )
