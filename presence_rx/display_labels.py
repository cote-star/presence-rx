"""Human-friendly display labels for internal field values.

Translates raw enum/field values to public-facing terminology.
JSON artifact keys stay unchanged — this is rendering-layer only.
"""

from __future__ import annotations

GAP_TYPE_LABELS: dict[str | None, str] = {
    "perception": "perception",
    "indexing": "discovery",
    "volume_frequency": "attention",
    None: "stronghold",
}

GAP_TYPE_ARTICLE: dict[str | None, str] = {
    "perception": "a perception",
    "indexing": "a discovery",
    "volume_frequency": "an attention",
    None: "",
}

DECISION_LABELS: dict[str, str] = {
    "act_now": "Act now",
    "test_next": "Test next",
    "monitor": "Monitor",
    "block": "Block",
}

TREND_LABELS: dict[str, str] = {
    "blind_spot": "blind spot",
    "proof_gap": "evidence gap",
    "stronghold": "stronghold",
    "watch": "watch",
    "contested": "contested",
    "slow_burn": "emerging",
    "snapshot_blind_spot": "blind spot",
}


def human_gap_type(gap_type: str | None) -> str:
    """Return human-friendly gap type label."""
    return GAP_TYPE_LABELS.get(gap_type, gap_type or "unknown")


def human_gap_article(gap_type: str | None) -> str:
    """Return gap type with correct article ('an indexing', 'a perception')."""
    return GAP_TYPE_ARTICLE.get(gap_type, f"a {gap_type}" if gap_type else "")


def human_decision(bucket: str) -> str:
    """Return human-friendly decision bucket label."""
    return DECISION_LABELS.get(bucket, bucket.replace("_", " ").title())


def human_trend(label: str) -> str:
    """Return human-friendly trend label."""
    return TREND_LABELS.get(label, label.replace("_", " "))
