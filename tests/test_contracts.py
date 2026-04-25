from datetime import UTC, datetime

import pytest
from pydantic import ValidationError

from presence_rx.contracts import (
    EvidenceLedger,
    PromptUniverse,
    StudySsot,
    validate_payload,
)


def test_valid_prompt_universe_passes() -> None:
    payload = {
        "brand": "Nothing Phone",
        "competitors": ["Apple"],
        "clusters": [
            {
                "cluster_id": "cluster:minimalist-hardware",
                "label": "Minimalist Hardware",
                "stage": "consideration",
                "prompt_type": "category",
                "prompts": [
                    {
                        "prompt_id": "prompt:001",
                        "text": "best minimalist phone",
                        "source": "peec_mcp",
                    }
                ],
            }
        ],
    }

    artifact = PromptUniverse.model_validate(payload)

    assert artifact.brand == "Nothing Phone"


def test_missing_required_id_fails() -> None:
    payload = {
        "brand": "Nothing Phone",
        "competitors": [],
        "clusters": [
            {
                "cluster_id": "",
                "label": "Minimalist Hardware",
                "stage": "consideration",
                "prompt_type": "category",
                "prompts": [
                    {
                        "prompt_id": "prompt:001",
                        "text": "best minimalist phone",
                        "source": "peec_mcp",
                    }
                ],
            }
        ],
    }

    with pytest.raises(ValidationError, match="cluster_id"):
        PromptUniverse.model_validate(payload)


def test_missing_metric_requires_unavailable_reason() -> None:
    payload = {
        "rows": [
            {
                "cluster_id": "cluster:minimalist-hardware",
                "cluster_label": "Minimalist Hardware",
                "cluster_stage": "consideration",
                "cluster_prompt_type": "category",
                "cluster_prompt_count": None,
                "visibility_target_share": 0.06,
                "visibility_target_avg_position": 4.1,
                "visibility_competitor_owner": "Apple",
                "gap_type": "perception",
                "confidence_tier": "moderate",
                "evidence_refs": ["peec:topic:minimalist-hardware"],
                "input_gate_status": "passed",
                "evidence_tier": "moderate",
                "publication_status": "directional_with_caveat",
                "recommendation_available": False,
                "unavailable_reason": None,
            }
        ]
    }

    with pytest.raises(ValidationError, match="missing metrics require unavailable_reason"):
        StudySsot.model_validate(payload)


def test_available_recommendation_requires_evidence_and_publication_fields() -> None:
    payload = {
        "rows": [
            {
                "cluster_id": "cluster:wireless-audio",
                "cluster_label": "Wireless Audio",
                "cluster_stage": "consideration",
                "cluster_prompt_type": "category",
                "cluster_prompt_count": 5,
                "visibility_target_share": 0.01,
                "visibility_target_avg_position": 2.0,
                "visibility_competitor_owner": "Apple",
                "gap_type": "volume_frequency",
                "confidence_tier": "strong",
                "evidence_refs": [],
                "input_gate_status": "passed",
                "evidence_tier": "strong",
                "publication_status": "publishable",
                "recommendation_available": True,
                "action_recommendation": "Publish Nothing Ear comparison content.",
                "action_monitor_prompt": "best wireless earbuds for Android",
            }
        ]
    }

    with pytest.raises(ValidationError, match="evidence ref"):
        StudySsot.model_validate(payload)


def test_blocked_claim_must_be_in_register() -> None:
    payload = {
        "metadata": {
            "source_manifest_ref": "peec:snapshot:nothing-phone:2026-04-25",
            "peec_snapshot_id": "peec:snapshot:nothing-phone:2026-04-25",
            "ledger_template_version": "evidence_ledger:v1",
            "used_classification": True,
            "classifier_version": "gap_classifier:v1",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "brand": "Nothing Phone",
        "claims": [
            {
                "claim_id": "claim:nothing:minimalist:blocked",
                "claim": "Nothing Phone is the go-to minimalist tech brand.",
                "status": "blocked",
                "cluster_id": "cluster:minimalist-hardware",
                "methods": ["peec_visibility"],
                "evidence_refs": ["peec:topic:minimalist-hardware"],
                "confidence_tier": "blocked",
                "publication_status": "blocked",
                "publication_language": (
                    "Do not claim Nothing Phone ownership of the Minimalist Hardware topic; "
                    "partner methods conflict (1 conflicts)."
                ),
            }
        ],
        "evidence": [
            {
                "evidence_ref": "peec:topic:minimalist-hardware",
                "source_type": "peec_mcp",
                "summary": "Nothing Phone has 6% visibility; Apple has 39%.",
                "url": None,
                "confidence": 0.9,
            }
        ],
        "blocked_claims": [],
    }

    with pytest.raises(ValidationError, match="blocked_claims register"):
        EvidenceLedger.model_validate(payload)


def test_blocked_claim_passes_when_registered() -> None:
    payload = {
        "metadata": {
            "source_manifest_ref": "peec:snapshot:nothing-phone:2026-04-25",
            "peec_snapshot_id": "peec:snapshot:nothing-phone:2026-04-25",
            "ledger_template_version": "evidence_ledger:v1",
            "used_classification": True,
            "classifier_version": "gap_classifier:v1",
        },
        "generated_at": datetime.now(UTC).isoformat(),
        "brand": "Nothing Phone",
        "claims": [
            {
                "claim_id": "claim:nothing:minimalist:blocked",
                "claim": "Nothing Phone is the go-to minimalist tech brand.",
                "status": "blocked",
                "cluster_id": "cluster:minimalist-hardware",
                "methods": ["peec_visibility"],
                "evidence_refs": ["peec:topic:minimalist-hardware"],
                "confidence_tier": "blocked",
                "publication_status": "blocked",
                "publication_language": (
                    "Do not claim Nothing Phone ownership of the Minimalist Hardware topic; "
                    "partner methods conflict (1 conflicts)."
                ),
            }
        ],
        "evidence": [
            {
                "evidence_ref": "peec:topic:minimalist-hardware",
                "source_type": "peec_mcp",
                "summary": "Nothing Phone has 6% visibility; Apple has 39%.",
                "url": None,
                "confidence": 0.9,
            }
        ],
        "blocked_claims": [
            {
                "claim_id": "claim:nothing:minimalist:blocked",
                "claim": "Nothing Phone is the go-to minimalist tech brand.",
                "blocked_reason": "OVERCLAIM_RISK",
                "safe_rewrite": (
                    "Nothing Phone dominates Smartphone Design but not Minimalist Hardware."
                ),
                "next_evidence_to_collect": "Publish minimalist hardware proof and rerun prompts.",
            }
        ],
    }

    artifact = EvidenceLedger.model_validate(payload)

    assert artifact.blocked_claims[0].blocked_reason == "OVERCLAIM_RISK"


def test_validate_payload_infers_known_contract() -> None:
    artifact = validate_payload(
        {
            "guardrail_pass_rate_pct": 67,
            "cluster_pass_rate_pct": 50,
            "actionable_recommendations": 3,
            "method_conflict_count": 1,
            "blocked_claim_count": 1,
        },
        "hero_cards",
    )

    assert artifact.model_dump()["blocked_claim_count"] == 1
