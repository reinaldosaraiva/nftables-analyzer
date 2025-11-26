"""API request and response schemas."""

from typing import Any, Literal

from pydantic import BaseModel, Field

from nftables_analyzer.models import Conflict, Rule


class ParseRequest(BaseModel):
    """Request to parse nftables rules."""

    content: str = Field(..., description="Rules content (text or JSON)")
    format: Literal["text", "json"] = Field(
        default="text", description="Input format"
    )


class GraphNode(BaseModel):
    """React Flow node."""

    id: str
    type: str
    data: dict[str, Any]
    position: dict[str, float]
    style: dict[str, Any] | None = None


class GraphEdge(BaseModel):
    """React Flow edge."""

    id: str
    source: str
    target: str
    animated: bool = False
    style: dict[str, Any] | None = None


class GraphData(BaseModel):
    """Graph data for React Flow visualization."""

    nodes: list[GraphNode]
    edges: list[GraphEdge]


class ParseResponse(BaseModel):
    """Response from parsing rules."""

    rules: list[Rule]
    graph: GraphData
    count: int


class QueryRequest(BaseModel):
    """Request to evaluate a query."""

    rules_content: str = Field(..., description="Rules content")
    rules_format: Literal["text", "json"] = Field(default="text")

    # Query can be provided as text or structured
    query_text: str | None = Field(
        default=None, description="Natural language query"
    )

    # Or structured query
    src_ip: str | None = None
    dst_ip: str | None = None
    src_port: int | None = None
    dst_port: int | None = None
    protocol: str | None = None
    direction: Literal["in", "out", "forward"] | None = None


class QueryResponse(BaseModel):
    """Response from query evaluation."""

    verdict: Literal["ALLOW", "BLOCK", "NO_MATCH", "CONFLICT"]
    explanation: str
    matched_rules: list[Rule]
    conflicts: list[Conflict]
    trace: list[str]
    graph: GraphData


class RedundancyResponse(BaseModel):
    """Response from redundancy check."""

    redundant_count: int
    redundant_pairs: list[dict[str, Any]]
