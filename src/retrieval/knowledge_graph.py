"""
Autonomous Knowledge Graph and Causal Entity-Relationship Network (KG-RAG).
Extracts domain entities (segments, metrics, periods, external drivers, operational events)
and maps causal, attributional, and temporal relationships with strict source grounding.
"""
from typing import Any, Optional
from pydantic import BaseModel, Field
import networkx as nx
from src.ingestion.metadata import ExtractedChunk, SourceLocation


class EntityNode(BaseModel):
    node_id: str
    name: str
    entity_type: str  # "Segment", "Metric", "Period", "Driver", "Risk", "Organization"
    attributes: dict[str, Any] = Field(default_factory=dict)
    source_documents: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)

class RelationEdge(BaseModel):
    source_id: str
    target_id: str
    relation_type: str  # "CONTRIBUTES_TO", "EXPERIENCED_EVENT", "REPORTED_IN", "CAUSED_BY", "DISCREPANCY_WITH"
    weight: float = 1.0
    evidence_quote: str = ""
    citation: str = ""

class KnowledgeGraphSummary(BaseModel):
    total_nodes: int
    total_edges: int
    node_types: dict[str, int]
    relation_types: dict[str, int]
    key_hubs: list[dict[str, Any]]
    causal_paths: list[list[str]]

class DocumentKnowledgeGraph:
    """
    Constructs, queries, and visualizes an attributed Knowledge Graph over document evidence.
    """
    def __init__(self):
        self.graph = nx.DiGraph()
        self.nodes_data: dict[str, EntityNode] = {}
        self.edges_data: list[RelationEdge] = []

    def add_entity(self, node: EntityNode) -> None:
        self.nodes_data[node.node_id] = node
        self.graph.add_node(
            node.node_id,
            name=node.name,
            entity_type=node.entity_type,
            attributes=node.attributes,
            citations=node.citations
        )

    def add_relation(self, edge: RelationEdge) -> None:
        self.edges_data.append(edge)
        self.graph.add_edge(
            edge.source_id,
            edge.target_id,
            relation_type=edge.relation_type,
            weight=edge.weight,
            evidence=edge.evidence_quote,
            citation=edge.citation
        )

    def populate_from_investigation(
        self,
        chunks: list[ExtractedChunk],
        period_data: Optional[Any] = None,
        segment_data: Optional[Any] = None,
        source_claims: Optional[list[Any]] = None
    ) -> None:
        """
        Mines entities, financial metrics, and causal drivers directly from chunks and structured results.
        """
        # 1. Base Metric & Period Nodes
        self.add_entity(EntityNode(
            node_id="metric_revenue",
            name="Consolidated Revenue",
            entity_type="Metric",
            attributes={"unit": "₹ lakh", "formula": "Sum of Segment Revenues"}
        ))

        self.add_entity(EntityNode(
            node_id="period_q1",
            name="Q1 (Baseline)",
            entity_type="Period",
            attributes={"period_index": 1}
        ))

        self.add_entity(EntityNode(
            node_id="period_q2",
            name="Q2 (Comparative)",
            entity_type="Period",
            attributes={"period_index": 2}
        ))

        # 2. Add Segment Nodes & Contribution Edges
        if segment_data and hasattr(segment_data, "segments"):
            for seg in segment_data.segments:
                seg_id = f"segment_{seg.segment_name.lower().replace(' ', '_')}"
                self.add_entity(EntityNode(
                    node_id=seg_id,
                    name=seg.segment_name,
                    entity_type="Segment",
                    attributes={
                        "period_1_val": seg.period_1_value,
                        "period_2_val": seg.period_2_value,
                        "delta": seg.absolute_change,
                        "contribution_pct": seg.contribution_percentage,
                        "direction": seg.direction
                    }
                ))

                # Edge: Segment -> Metric (CONTRIBUTES_TO)
                self.add_relation(RelationEdge(
                    source_id=seg_id,
                    target_id="metric_revenue",
                    relation_type="CONTRIBUTES_TO",
                    weight=abs(seg.contribution_percentage) / 100.0,
                    evidence_quote=f"{seg.segment_name} contributed {seg.contribution_percentage:.1f}% to the overall revenue delta ({seg.absolute_change:+.1f} lakh)."
                ))

        # 3. Mine Narrative Drivers & External Factors from text chunks
        driver_keywords = {
            "supply chain": ("driver_supply_chain", "Supply Chain Disruption", "Driver"),
            "component shortage": ("driver_component_shortage", "Hardware Component Shortage", "Risk"),
            "logistics delay": ("driver_logistics_delay", "Logistics & Shipping Delays", "Driver"),
            "demand": ("driver_market_demand", "Macro Market Demand Softening", "Driver"),
            "regulatory": ("driver_regulatory", "Regulatory Compliance Changes", "Risk"),
            "pricing pressure": ("driver_pricing_pressure", "Competitive Pricing Pressure", "Driver")
        }

        for ch in chunks:
            ch_text_lower = ch.content.lower()
            citation_str = ch.location.to_citation_str() if ch.location else ch.file_name

            for kw, (node_id, formal_name, ent_type) in driver_keywords.items():
                if kw in ch_text_lower:
                    if node_id not in self.nodes_data:
                        self.add_entity(EntityNode(
                            node_id=node_id,
                            name=formal_name,
                            entity_type=ent_type,
                            source_documents=[ch.file_name],
                            citations=[citation_str]
                        ))

                    # Connect causal driver to Segment A or B if mentioned in proximity
                    target_seg = None
                    if "segment a" in ch_text_lower:
                        target_seg = "segment_segment_a"
                    elif "segment b" in ch_text_lower:
                        target_seg = "segment_segment_b"
                    elif "segment c" in ch_text_lower:
                        target_seg = "segment_segment_c"
                    else:
                        target_seg = "metric_revenue"

                    if target_seg in self.nodes_data or target_seg == "metric_revenue":
                        self.add_relation(RelationEdge(
                            source_id=node_id,
                            target_id=target_seg,
                            relation_type="CAUSED_BY" if target_seg != "metric_revenue" else "IMPACTED",
                            weight=0.85,
                            evidence_quote=ch.content[:160].replace("\n", " "),
                            citation=citation_str
                        ))

        # 4. Connect Cross-Document Discrepancies if claims exist
        if source_claims:
            for c in source_claims:
                claim_id = f"claim_{c.metric_name}_{c.period}_{c.document_name}".replace(" ", "_").lower()
                self.add_entity(EntityNode(
                    node_id=claim_id,
                    name=f"{c.document_name}: {c.metric_name} ({c.period}) = {c.reported_value}",
                    entity_type="Claim",
                    attributes={"val": c.reported_value, "doc": c.document_name},
                    citations=[c.source_location.to_citation_str() if c.source_location else c.document_name]
                ))

    def find_causal_chains(self, target_node: str = "metric_revenue") -> list[list[str]]:
        """
        Traces multi-hop causal paths leading into the target node.
        """
        if target_node not in self.graph:
            return []

        paths: list[list[str]] = []
        for n in self.graph.nodes:
            if n != target_node and self.graph.in_degree(n) == 0:
                # Potential root causes
                try:
                    all_p = list(nx.all_simple_paths(self.graph, source=n, target=target_node, cutoff=4))
                    paths.extend(all_p)
                except (nx.NetworkXNoPath, nx.NodeNotFound):
                    pass

        # Format path names
        named_paths = []
        for p in paths:
            named_p = [self.nodes_data.get(node_id, EntityNode(node_id=node_id, name=node_id, entity_type="Unknown")).name for node_id in p]
            named_paths.append(named_p)
        return named_paths

    def get_summary(self) -> KnowledgeGraphSummary:
        node_types: dict[str, int] = {}
        for n in self.nodes_data.values():
            node_types[n.entity_type] = node_types.get(n.entity_type, 0) + 1

        rel_types: dict[str, int] = {}
        for e in self.edges_data:
            rel_types[e.relation_type] = rel_types.get(e.relation_type, 0) + 1

        # Centrality
        degree_dict = dict(self.graph.degree())
        sorted_hubs = sorted(degree_dict.items(), key=lambda x: x[1], reverse=True)[:5]
        key_hubs = [
            {
                "node_id": k,
                "name": self.nodes_data[k].name if k in self.nodes_data else k,
                "type": self.nodes_data[k].entity_type if k in self.nodes_data else "Unknown",
                "connections": v
            }
            for k, v in sorted_hubs
        ]

        causal_paths = self.find_causal_chains("metric_revenue")

        return KnowledgeGraphSummary(
            total_nodes=self.graph.number_of_nodes(),
            total_edges=self.graph.number_of_edges(),
            node_types=node_types,
            relation_types=rel_types,
            key_hubs=key_hubs,
            causal_paths=causal_paths
        )

    def to_cytoscape_elements(self) -> list[dict[str, Any]]:
        """
        Exports graph elements in Cytoscape JSON format for interactive visual rendering.
        """
        elements = []
        for n_id, n in self.nodes_data.items():
            elements.append({
                "data": {
                    "id": n_id,
                    "label": n.name,
                    "type": n.entity_type,
                    "citations": ", ".join(n.citations)
                }
            })
        for idx, e in enumerate(self.edges_data):
            elements.append({
                "data": {
                    "id": f"edge_{idx}",
                    "source": e.source_id,
                    "target": e.target_id,
                    "label": e.relation_type,
                    "weight": e.weight,
                    "evidence": e.evidence_quote
                }
            })
        return elements
