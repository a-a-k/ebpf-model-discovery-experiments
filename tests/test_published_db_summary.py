"""The hand-maintained semantic summary must agree with immutable published metrics."""
import json
from pathlib import Path


def test_semantic_db_summary_counts_network_forecasts_and_unknowns():
    root = Path(__file__).resolve().parents[1]
    report = json.loads((root / 'results/correction-publication.json').read_bytes())
    semantic = json.loads((root / 'results/semantic-correction.json').read_bytes())['prospective_correction']
    groups = report['statistics']['comparison_by_mode_collector_source_view']
    known = sum(g['database_down']['known'] for g in groups)
    unknown = sum(g['database_down']['unknown'] for g in groups)
    assert semantic['graph_database_down_forecasts_available'] == known == 48
    assert semantic['graph_database_down_forecasts_unavailable'] == unknown == 816
    assert known + unknown == report['statistics']['source_view_rows']
    assert {g['view'] for g in groups if g['database_down']['known']} == {'network_scope'}
    assert {g['source'] for g in groups if g['database_down']['known']} == {'combined', 'context-baseline'}
    assert all(g['database_down']['max_error'] == 0 for g in groups if g['database_down']['known'])


def test_latest_database_total_replaces_the_original_social_network_rows():
    root = Path(__file__).resolve().parents[1]
    original = json.loads((root / 'results/literal-results.json').read_bytes())
    known_other = sum(row['database_down_prediction'] is not None
                      for c in original['cells'] if c['key'][0] != 'deathstarbench'
                      for row in c['literal_evaluation']['rows'])
    assert known_other == 201
    semantic = json.loads((root / 'results/semantic-correction.json').read_bytes())['prospective_correction']
    assert semantic['latest108_graph_database_down_forecasts_available'] == known_other + 48 == 249
