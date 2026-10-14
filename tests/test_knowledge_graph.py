"""
Unit tests for the Autonomous Knowledge Graph & Causal Entity-Relationship Network.
"""
from src.retrieval.knowledge_graph import DocumentKnowledgeGraph, EntityNode, RelationEdge
from src.ingestion.metadata import ExtractedChunk, SourceLocation, FileType
from src.tools.numerical_analysis import NumericalAnalyzer

def test_knowledge_graph_construction():
    kg = DocumentKnowledgeGraph()
    
    # Create sample segments
    sample_segs = [
        {"segment": "Segment A", "p1": 500.0, "p2": 420.0},
        {"segment": "Segment B", "p1": 300.0, "p2": 280.0},
        {"segment": "Segment C", "p1": 200.0, "p2": 200.0},
    ]
    seg_summary = NumericalAnalyzer.analyze_segment_contributions("Revenue", sample_segs, "₹ lakh")
    
    # Create sample narrative chunk
    loc = SourceLocation(
        document_id="doc1",
        file_name="Quarterly_Report.pdf",
        file_type=FileType.PDF,
        page_number=2
    )
    ch = ExtractedChunk(
        chunk_id="ch_1",
        document_id="doc1",
        file_name="Quarterly_Report.pdf",
        content="Segment A experienced significant supply chain and component shortage issues leading to delayed orders.",
        content_type="text",
        location=loc
    )
    
    kg.populate_from_investigation(
        chunks=[ch],
        segment_data=seg_summary
    )
    
    summary = kg.get_summary()
    assert summary.total_nodes >= 5
    assert summary.total_edges >= 3
    assert "Segment" in summary.node_types
    assert "Metric" in summary.node_types
    
    # Causal path tracing
    causal_paths = kg.find_causal_chains("metric_revenue")
    assert len(causal_paths) >= 1
    
    # Cytoscape export
    cyto = kg.to_cytoscape_elements()
    assert len(cyto) == summary.total_nodes + summary.total_edges
