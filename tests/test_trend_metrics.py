from datetime import UTC, datetime

from presence_rx.build_competitor_landscape import build_competitor_landscape
from presence_rx.build_mvp_dashboard import build_dashboard
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.contracts import TavilyEvidence
from presence_rx.ingest_peec import SNAPSHOT_REF, build_artifacts, nothing_phone_seed

POISON = "POISON_TAVILY_SNIPPET_DO_NOT_EMBED"


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def test_value_metrics_include_public_safe_trend_routing() -> None:
    artifacts = _artifacts()

    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    rows = {row.cluster_id: row for row in metrics.rows}

    minimalist = rows["cluster:minimalist-hardware"]
    assert minimalist.parent_topic == "minimalist_category_language"
    assert minimalist.trend_zone == "proof_gap"
    assert minimalist.zone_basis == "proof_coverage"
    assert minimalist.decision_bucket == "test_next"
    assert minimalist.primary_gap == "MISSING_ASSOCIATION"
    assert "private" not in minimalist.recommended_next_move.lower()

    stronghold = rows["cluster:smartphone-design"]
    assert stronghold.trend_label == "stronghold"
    assert stronghold.decision_bucket == "monitor"
    assert stronghold.primary_gap == "NONE_STRONGHOLD"


def test_target_owned_landscape_topic_is_confirmed_without_gap_classification() -> None:
    artifacts = _artifacts()

    landscape = build_competitor_landscape(artifacts.study_ssot, artifacts.manifest)
    topics = {topic.cluster_id: topic for topic in landscape.topics}

    assert topics["cluster:smartphone-design"].ownership_status == "target_owned"
    assert topics["cluster:smartphone-design"].classification_status == "confirmed"


def test_dashboard_embeds_only_tavily_aggregates() -> None:
    artifacts = _artifacts()
    tavily = TavilyEvidence.model_validate(
        {
            "metadata": {
                "generated_at": datetime.now(UTC).isoformat(),
                "source_manifest_ref": SNAPSHOT_REF,
                "peec_snapshot_id": SNAPSHOT_REF,
                "run_mode": "test",
                "sdk_package": "tavily-python",
                "sdk_version": "test",
                "query_template_version": "test",
                "search_depth": "basic",
                "max_results": 5,
                "query_timeout_seconds": 10,
                "include_raw_content": False,
                "include_answer": False,
                "include_images": False,
                "include_usage": True,
                "request_count": 1,
                "successful_query_count": 1,
                "failed_query_count": 0,
                "failed_query_ref": None,
            },
            "summary": {
                "analyzed_rows": 1,
                "planned_queries": 1,
                "sources": 1,
                "supported_findings": 1,
                "conflicted_findings": 0,
                "insufficient_findings": 0,
            },
            "findings": [
                {
                    "finding_id": "tavily:test:minimalist-hardware",
                    "cluster_id": "cluster:minimalist-hardware",
                    "cluster_label": "Minimalist Hardware",
                    "gap_type": "perception",
                    "source_of_record": "tavily",
                    "target_query": "Nothing Phone minimalist hardware",
                    "competitor_query": "Apple minimalist hardware",
                    "public_proof_support": "supports",
                    "proof_gap_summary": "Public proof summary.",
                    "rationale": "Public proof supports the directional gap.",
                    "evidence_refs": ["tavily:evidence:minimalist-hardware:test"],
                    "sources": [
                        {
                            "source_ref": "tavily:source:test",
                            "title": "Public source",
                            "url": "https://example.com/public-source",
                            "domain": "example.com",
                            "snippet": POISON,
                            "score": 0.9,
                            "query_ref": "query:test",
                            "source_role": "target",
                        }
                    ],
                }
            ],
        }
    )

    html = build_dashboard(artifacts.study_ssot, tavily=tavily)

    assert POISON not in html
    assert "successful_query_count" in html


def test_dashboard_uses_peec_style_shell() -> None:
    artifacts = _artifacts()

    html = build_dashboard(artifacts.study_ssot)

    assert "--peec-bg: #FFFFFF" in html
    assert 'class="app-shell"' in html
    assert 'class="filter-pill">Brand: Nothing Phone' in html
    assert 'class="journey-rail"' in html
    assert 'id="blind-spots"' in html
    assert 'id="evidence"' in html
    assert 'id="prescriptions"' in html
    assert 'id="monitoring"' in html
    assert 'id="export"' in html
    assert "Claim review" in html
    assert "Show audit trail" in html
    assert "Source-of-record references" not in html
    assert "plotly_dark" not in html
    assert "#0f1117" not in html


def test_dashboard_uses_named_cluster_owner_copy() -> None:
    artifacts = _artifacts()
    landscape = build_competitor_landscape(artifacts.study_ssot, artifacts.manifest)

    html = build_dashboard(artifacts.study_ssot, landscape=landscape)

    assert "Cluster owner" in html
    assert "brandName} owns" in html
    assert "name} owns" in html
    assert "Competitor-owned prompt cluster" not in html
    assert "Competitor owner" not in html
