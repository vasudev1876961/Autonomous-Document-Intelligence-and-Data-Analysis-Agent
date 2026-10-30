"""
Unit tests for Causal Knowledge Graph multi-hop paths and shock propagation.
"""
import pytest
from src.retrieval.knowledge_graph import (
    DocumentKnowledgeGraph,
    EntityNode,
    RelationEdge,
)
from src.tools.numerical_analysis import NumericalAnalyzer

def test_causal_graph_paths_and_shock():
    kg = DocumentKnowledgeGraph()
    sample_segments = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segments, "₹ lakh")
    kg.populate_from_investigation(
        chunks=[],
        period_data=None,
        segment_data=seg_summary,
        source_claims=[]
    )

    # Add a root driver manually
    kg.add_entity(EntityNode(
        node_id="driver_supply_chain",
        name="Supply Chain Disruption",
        entity_type="Driver"
    ))
    kg.add_relation(RelationEdge(
        source_id="driver_supply_chain",
        target_id="segment_segment_a",
        relation_type="CAUSED_BY",
        weight=0.9
    ))

    # Test path from driver to consolidated revenue
    paths = kg.find_paths_between("driver_supply_chain", "metric_revenue")
    assert len(paths) >= 1
    assert paths[0][0] == "Supply Chain Disruption"
    assert paths[0][-1] == "Consolidated Revenue"

    # Test shock simulation
    shock_res = kg.simulate_causal_shock("driver_supply_chain", shock_pct=-10.0)
    assert shock_res.root_node_id == "driver_supply_chain"
    assert len(shock_res.impacted_entities) >= 2
    assert any(imp.node_id == "segment_segment_a" for imp in shock_res.impacted_entities)
    assert shock_res.net_revenue_impact_pct is not None
    assert "Supply Chain Disruption" in shock_res.narrative_implication

