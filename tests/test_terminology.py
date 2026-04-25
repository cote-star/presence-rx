"""Tests that public surfaces use industry-standard terminology.

These tests prevent internal/work-adjacent terms from leaking into
user-facing outputs (dashboard HTML, generated markdown).
JSON artifact keys are internal and NOT checked here.
"""

from presence_rx.build_action_brief import build_action_brief
from presence_rx.build_mvp_dashboard import build_dashboard
from presence_rx.build_verdict import build_presence_verdict
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed


def _artifacts():
    return build_artifacts(nothing_phone_seed())


# ---- Dashboard HTML terminology ----

def test_dashboard_uses_new_metric_labels():
    """Dashboard must use industry-standard metric labels."""
    artifacts = _artifacts()
    html = build_dashboard(artifacts.study_ssot)

    # New terms MUST be present (radar chart axis labels)
    assert "Intent Fit" in html
    assert "Citation Authority" in html
    assert "Evidence Coverage" in html
    assert "Signal Alignment" in html
    assert "Action Priority" in html
    # The dashboard uses "Claim review" as the nav/panel label
    assert "Claim review" in html


def test_dashboard_no_old_metric_labels():
    """Dashboard must NOT show old internal-sounding labels."""
    artifacts = _artifacts()
    html = build_dashboard(artifacts.study_ssot)

    # These exact display strings must NOT appear as visible labels.
    # (the underlying JS variable names like m.source_trust_score are fine)
    assert "Source Trust<" not in html  # as label text before a tag
    assert "Proof Strength<" not in html
    assert ">Source Trust</th>" not in html
    assert ">Proof Strength</th>" not in html


def test_dashboard_no_decision_bucket_in_copy():
    """Problem copy should say 'recommended action' not 'decision bucket'."""
    artifacts = _artifacts()
    html = build_dashboard(artifacts.study_ssot)

    assert "decision bucket" not in html


# ---- Markdown terminology ----

def test_verdict_uses_new_labels():
    """PRESENCE_VERDICT.md must use industry-standard column headers."""
    artifacts = _artifacts()
    content = build_presence_verdict(artifacts.study_ssot, artifacts.manifest)

    # The Gap-Type Summary table uses these headers
    assert "Action Priority" in content
    assert "Signal Alignment" in content
    assert "Evidence Level" in content


def test_action_brief_uses_new_labels():
    """ACTION_BRIEF.md must use industry-standard field labels."""
    from presence_rx.build_value_metrics import build_value_added_metrics
    from presence_rx.classify_gaps import build_gap_classification

    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    content = build_action_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        metrics=metrics,
    )

    # New labels must appear when classification + metrics are provided
    assert "Recommended Action" in content or "Action Priority" in content \
        or "Recommended next move" in content
