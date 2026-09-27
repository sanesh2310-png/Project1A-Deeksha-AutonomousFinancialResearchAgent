from synthesis import conflict_resolver


def test_detect_conflicts_flags_large_spread():
    data_points = [
        {"metric": "op_margin", "value": 20.0, "source_type": "financial_data_api"},
        {"metric": "op_margin", "value": 30.0, "source_type": "news_outlet"},
    ]
    conflicts = conflict_resolver.detect_conflicts(data_points)
    assert len(conflicts) == 1
    assert conflicts[0]["metric"] == "op_margin"


def test_detect_conflicts_ignores_small_spread():
    data_points = [
        {"metric": "op_margin", "value": 20.0, "source_type": "financial_data_api"},
        {"metric": "op_margin", "value": 20.5, "source_type": "news_outlet"},
    ]
    conflicts = conflict_resolver.detect_conflicts(data_points)
    assert conflicts == []


def test_resolve_conflict_prefers_sec_filing_over_news():
    conflict = {
        "metric": "op_margin",
        "spread_pct": 15.0,
        "points": [
            {"metric": "op_margin", "value": 30.0, "source_type": "news_outlet"},
            {"metric": "op_margin", "value": 20.0, "source_type": "sec_filing"},
        ],
    }
    resolution = conflict_resolver.resolve_conflict(conflict)
    assert resolution["chosen_value"] == 20.0
    assert resolution["chosen_source_type"] == "sec_filing"


def test_source_reliability_hierarchy_ranks_news_above_social_media():
    """
    Regression test for ERROR_LOG.md Error 7: the brief's original hierarchy
    ranked social media above major news outlets. This locks in the fix.
    """
    from config import settings
    assert settings.SOURCE_RELIABILITY_TIERS["news_outlet"] < settings.SOURCE_RELIABILITY_TIERS["social_media"]


def test_triangulate_majority_agreement():
    result = conflict_resolver.triangulate([10.0, 10.2, 15.0])
    assert result["agreement"] == "majority"


def test_triangulate_no_agreement():
    result = conflict_resolver.triangulate([10.0, 15.0, 20.0])
    assert result["agreement"] == "none"
