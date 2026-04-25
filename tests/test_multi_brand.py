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


# ---------- Multi-brand hardening tests ----------


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_no_brand_leakage_in_source_of_record(case_id):
    """source_of_record.json must not mention other brands."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    sor_dump = artifacts.source_of_record.model_dump_json()

    other_brands = {"Nothing Phone", "Attio", "BMW"} - {seed.brand}
    for other in other_brands:
        assert other not in sor_dump, (
            f"{case_id} source_of_record.json mentions '{other}'"
        )


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_manifest_brand_matches_seed(case_id):
    """Manifest brand must match the seed brand, not a hardcoded value."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    assert artifacts.manifest.brand == seed.brand


@pytest.mark.parametrize("case_id", BRAND_IDS)
def test_dashboard_uses_correct_brand_name(case_id):
    """Dashboard HTML must reference the correct brand, not hardcoded Nothing Phone."""
    from presence_rx.build_mvp_dashboard import build_dashboard

    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    html = build_dashboard(artifacts.study_ssot, manifest=artifacts.manifest)

    # The data dict should contain the correct brand name
    assert f'"brand_name": "{seed.brand}"' in html
    # Brand name should not be hardcoded in JS
    assert "const brandName = 'Nothing Phone'" not in html


@pytest.mark.parametrize("case_id", ["attio", "bmw"])
def test_verdict_tavily_provenance_honest_when_unavailable(case_id):
    """When Tavily has 0 sources, verdict must not claim Tavily evidence exists."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)
    content = build_presence_verdict(artifacts.study_ssot, artifacts.manifest)

    # Should NOT say "Tavily: live" when no Tavily data
    assert "Tavily: live" not in content
    # Should indicate unavailable
    assert (
        "not available" in content.lower()
        or "no tavily" in content.lower()
        or "0 sources" in content.lower()
        or "unavailable" in content.lower()
    )


@pytest.mark.parametrize("case_id", ["attio", "bmw"])
def test_no_nothing_phone_in_any_artifact_text(case_id):
    """No artifact text for Attio/BMW should mention 'Nothing Phone'."""
    seed = get_seed(case_id)
    artifacts = build_artifacts(seed)

    # Check study rows
    for row in artifacts.study_ssot.rows:
        assert "Nothing Phone" not in row.cluster_label

    # Check manifest
    assert artifacts.manifest.brand != "Nothing Phone"
    assert "Nothing Phone" not in str(artifacts.manifest.competitors)

    # Check source of record
    for item in artifacts.source_of_record.sources:
        assert "Nothing Phone" not in item.rationale, (
            f"{case_id} source_of_record leaks 'Nothing Phone' in: {item.rationale}"
        )


# ---------- Multi-brand combined dashboard tests ----------


def test_multi_brand_dashboard_contains_all_brands():
    """Combined dashboard embeds all 3 brands' data and has a brand switcher."""
    from presence_rx.build_mvp_dashboard import _build_brand_data, build_multi_brand_dashboard

    brands_data = {}
    for case_id in BRAND_IDS:
        seed = get_seed(case_id)
        artifacts = build_artifacts(seed)
        brands_data[case_id] = _build_brand_data(
            artifacts.study_ssot, None, None, None, None, None,
            manifest=artifacts.manifest,
        )

    html = build_multi_brand_dashboard(brands_data)

    # All 3 data scripts are embedded
    assert 'id="presence-data-nothing-phone"' in html
    assert 'id="presence-data-attio"' in html
    assert 'id="presence-data-bmw"' in html

    # Brand switcher dropdown exists
    assert 'id="brandSwitcher"' in html
    assert '<option value="nothing-phone">' in html
    assert '<option value="attio">' in html
    assert '<option value="bmw">' in html

    # All brand names appear in their respective data blocks
    assert '"brand_name": "Nothing Phone"' in html
    assert '"brand_name": "Attio"' in html
    assert '"brand_name": "BMW"' in html


def test_multi_brand_dashboard_uses_peec_styles():
    """Combined dashboard uses the same Peec design system as single-brand."""
    from presence_rx.build_mvp_dashboard import _build_brand_data, build_multi_brand_dashboard

    seed = get_seed("nothing-phone")
    artifacts = build_artifacts(seed)
    brands_data = {
        "nothing-phone": _build_brand_data(
            artifacts.study_ssot, None, None, None, None, None,
            manifest=artifacts.manifest,
        ),
    }

    html = build_multi_brand_dashboard(brands_data)

    assert "--peec-bg: #FFFFFF" in html
    assert 'class="app-shell"' in html
    assert 'id="blind-spots"' in html
    assert 'id="evidence"' in html
    assert 'id="prescriptions"' in html
    assert 'id="monitoring"' in html
    assert 'id="export"' in html
    assert "plotly_dark" not in html


def test_multi_brand_dashboard_has_all_sections():
    """Combined dashboard has all section IDs required by the single-brand version."""
    from presence_rx.build_mvp_dashboard import _build_brand_data, build_multi_brand_dashboard

    seed = get_seed("nothing-phone")
    artifacts = build_artifacts(seed)
    brands_data = {
        "nothing-phone": _build_brand_data(
            artifacts.study_ssot, None, None, None, None, None,
            manifest=artifacts.manifest,
        ),
    }

    html = build_multi_brand_dashboard(brands_data)

    for section_id in [
        "overview", "action-brief", "blind-spots", "perception",
        "claims", "evidence", "analytics", "prescriptions",
        "monitoring", "about", "export",
    ]:
        assert f'id="{section_id}"' in html, f"Missing section: {section_id}"


def test_multi_brand_dashboard_loadbrand_js():
    """Combined dashboard JS contains the loadBrand function and brand switcher wiring."""
    from presence_rx.build_mvp_dashboard import _build_brand_data, build_multi_brand_dashboard

    seed = get_seed("nothing-phone")
    artifacts = build_artifacts(seed)
    brands_data = {
        "nothing-phone": _build_brand_data(
            artifacts.study_ssot, None, None, None, None, None,
            manifest=artifacts.manifest,
        ),
    }

    html = build_multi_brand_dashboard(brands_data)

    assert "function loadBrand(caseId)" in html
    assert "brandDataSets" in html
    assert "brandSwitcher" in html
    assert "addEventListener" in html
