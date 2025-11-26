"""Rules API endpoints."""

from fastapi import APIRouter, HTTPException

from nftables_analyzer.api.schemas import (
    GraphData,
    ParseRequest,
    ParseResponse,
    QueryRequest,
    QueryResponse,
    RedundancyResponse,
)
from nftables_analyzer.api.services.graph_service import GraphService
from nftables_analyzer.evaluator.rule_evaluator import RuleEvaluator
from nftables_analyzer.interpreter.query_interpreter import QueryInterpreter
from nftables_analyzer.models import Query
from nftables_analyzer.parser.rule_parser import RuleParser

router = APIRouter()


@router.post("/parse", response_model=ParseResponse)
async def parse_rules(request: ParseRequest) -> ParseResponse:
    """Parse nftables rules from text or JSON and return rules with graph data."""
    try:
        # Parse rules
        if request.format == "json":
            rules = RuleParser.parse_json(request.content)
        else:
            rules = RuleParser.parse_text(request.content)

        if not rules:
            raise HTTPException(status_code=400, detail="No valid rules found")

        # Generate graph data
        graph_data = GraphService.rules_to_graph(rules)

        return ParseResponse(
            rules=rules,
            graph=graph_data,
            count=len(rules),
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Parse error: {str(e)}")


@router.post("/query", response_model=QueryResponse)
async def evaluate_query(request: QueryRequest) -> QueryResponse:
    """Evaluate a query against parsed rules."""
    try:
        # Parse rules
        if request.rules_format == "json":
            rules = RuleParser.parse_json(request.rules_content)
        else:
            rules = RuleParser.parse_text(request.rules_content)

        if not rules:
            raise HTTPException(status_code=400, detail="No valid rules found")

        # Parse query
        if request.query_text:
            query = QueryInterpreter.parse(request.query_text)
        else:
            query = Query(
                src_ip=request.src_ip,
                dst_ip=request.dst_ip,
                src_port=request.src_port,
                dst_port=request.dst_port,
                protocol=request.protocol,
                direction=request.direction or "in",
            )

        # Evaluate
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate(query)

        # Generate graph with highlighted nodes
        graph_data = GraphService.rules_to_graph(
            rules, matched_rules=result.matched_rules
        )

        return QueryResponse(
            verdict=result.verdict,
            explanation=result.explanation,
            matched_rules=result.matched_rules,
            conflicts=result.conflicts,
            trace=result.trace,
            graph=graph_data,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Evaluation error: {str(e)}")


@router.get("/redundant", response_model=RedundancyResponse)
async def check_redundancy(rules_content: str, rules_format: str = "text") -> RedundancyResponse:
    """Check for redundant rules."""
    try:
        # Parse rules
        if rules_format == "json":
            rules = RuleParser.parse_json(rules_content)
        else:
            rules = RuleParser.parse_text(rules_content)

        if not rules:
            raise HTTPException(status_code=400, detail="No valid rules found")

        # Find redundant rules
        evaluator = RuleEvaluator(rules)
        redundant = evaluator.find_redundant_rules()

        redundant_pairs = [
            {
                "shadowing_rule": general,
                "shadowed_rule": specific,
                "reason": f"Rule {general.line_number} shadows rule {specific.line_number}",
            }
            for general, specific in redundant
        ]

        return RedundancyResponse(
            redundant_count=len(redundant),
            redundant_pairs=redundant_pairs,
        )
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Redundancy check error: {str(e)}")
