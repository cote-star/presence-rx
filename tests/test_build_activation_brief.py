from presence_rx.brand_config import load_brand_config
from presence_rx.build_activation_brief import build_activation_brief
from presence_rx.build_value_metrics import build_value_added_metrics
from presence_rx.classify_gaps import build_gap_classification
from presence_rx.ingest_peec import build_artifacts, nothing_phone_seed

POISON = "POISON_TAVILY_SNIPPET_DO_NOT_EMBED"


def _artifacts():
    return build_artifacts(nothing_phone_seed())


def _brand_config():
    return load_brand_config("nothing-phone")


def test_activation_brief_has_owned_earned_sections() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    brand_config = _brand_config()

    content = build_activation_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        metrics=metrics,
        brand_config=brand_config,
    )
    assert "Owned Content Brief" in content
    assert "Earned Media Angle" in content


def test_activation_brief_groups_by_gap_type() -> None:
    artifacts = _artifacts()
    classification = build_gap_classification(artifacts.study_ssot, artifacts.manifest)
    metrics = build_value_added_metrics(artifacts.study_ssot, artifacts.manifest)
    brand_config = _brand_config()

    content = build_activation_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        classification=classification,
        metrics=metrics,
        brand_config=brand_config,
    )
    assert "Perception Gaps" in content
    assert "Indexing Gaps" in content


def test_activation_brief_uses_brand_config_channels() -> None:
    artifacts = _artifacts()
    brand_config = _brand_config()

    content = build_activation_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        brand_config=brand_config,
    )
    # Brand config channels should appear
    for channel in brand_config.channels_to_activate:
        assert channel in content, f"Channel '{channel}' not found in activation brief"


def test_activation_brief_no_raw_snippets() -> None:
    artifacts = _artifacts()
    brand_config = _brand_config()

    content = build_activation_brief(
        artifacts.study_ssot,
        artifacts.manifest,
        brand_config=brand_config,
    )
    assert POISON not in content
