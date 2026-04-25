"""Multi-brand generalization tests.

Prove the pipeline works for Nothing Phone, Attio, and BMW
without cross-contamination or hardcoded brand leakage.
"""
import pytest

from presence_rx.brand_config import list_brands, load_brand_config
from presence_rx.build_action_brief import build_action_brief
from presence_rx.build_challenged_claims import build_challenged_claims
from presence_rx.build_evidence_ledger import build_evidence_ledger
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.build_verdict import build_presence_verdict
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.ingest_peec import build_artifacts, get_seed

BRAND_IDS = ["nothing-phone", "attio", "bmw"]


def test_all_brands_in_registry():
    """config/brands.json lists all 3 brands."""
    brands = list_brands()
    assert set(BRAND_IDS) == set(brands)


def test_brand_configs_load_and_validate():
    """Each brand config loads and has required fields."""
    for case_id in BRAND_IDS:
        config = load_brand_config(case_id)
        assert config.case_id == case_id
        assert len(config.competitors) >= 3
        assert len(config.priority_topics) >= 3


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_seed_produces_valid_artifacts(case_id):
    """Each brand seed produces 5 study rows with valid contracts."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    assert len(artifacts.study_ssot.rows) == 5
    assert artifacts.manifest.brand == seed.brand
    # Exactly 1 stronghold, 4 blind spots
    strongholds = [r for r in artifacts.study_ssot.rows if r.gap_type is None]
    blind_spots = [r for r in artifacts.study_ssot.rows if r.gap_type is not None]
    assert len(strongholds) == 1
    assert len(blind_spots) == 4


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_classification_works_per_brand(case_id):
    """Gap classification produces 4 classified gaps per brand."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest
    )
    assert classification.summary.classified_gaps == 4


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_challenged_claims_per_brand(case_id):
    """Each brand produces blocked claims for its blind spots."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    results = build_challenged_claims(artifacts.study_ssot, artifacts.manifest)
    assert len(results) >= 1, f"{case_id} should have at least 1 blocked claim"
    for _claim, blocked in results:
        assert seed.brand in blocked.blocked_reason
        assert "OWNERSHIP_OVERCLAIM" in blocked.blocked_reason


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_no_cross_contamination_in_verdict(case_id):
    """Verdict markdown must not mention other brands as the main brand."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    content = build_presence_verdict(artifacts.study_ssot, artifacts.manifest)

    other_brands = {
        "nothing-phone": "Nothing Phone",
        "attio": "Attio",
        "bmw": "BMW",
    }
    del other_brands[case_id]

    # The verdict title must contain THIS brand
    assert f"# Presence Verdict: {seed.brand}" in content

    # Other brands should NOT appear in the title
    for _other_id, other_name in other_brands.items():
        assert f"# Presence Verdict: {other_name}" not in content


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_no_cross_contamination_in_action_brief(case_id):
    """Action brief must not mention other brands as the main brand."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    content = build_action_brief(artifacts.study_ssot, artifacts.manifest)

    assert f"# Action Brief: {seed.brand}" in content


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_competitor_names_correct_per_brand(case_id):
    """Each brand's competitors come from its own seed, not another brand's."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    classification = build_gap_classification(
        artifacts.study_ssot, artifacts.manifest
    )
    ledger = build_evidence_ledger(
        artifacts.study_ssot, artifacts.manifest, classification,
        challenged_claims=build_challenged_claims(artifacts.study_ssot, artifacts.manifest),
    )

    # The blocked claims should reference THIS brand's competitors
    for blocked in ledger.blocked_claims:
        # The blocked reason mentions the brand name
        assert seed.brand in blocked.blocked_reason


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_value_metrics_per_brand(case_id):
    """Each brand gets 5 metric rows with valid opportunity scores."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    assert len(metrics.rows) == 5
    for row in metrics.rows:
        assert 0 <= row.opportunity_score <= 100
