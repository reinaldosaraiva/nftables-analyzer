"""Tests for RuleEvaluator class."""

import pytest

from nftables_analyzer.evaluator.rule_evaluator import RuleEvaluator
from nftables_analyzer.models.query import Query
from nftables_analyzer.models.rule import Rule


class TestEvaluate:
    """Tests for evaluate method."""

    def test_simple_allow(self, sample_rules):
        """Test simple allow case."""
        evaluator = RuleEvaluator(sample_rules)
        query = Query(
            src_ip="192.168.1.10",
            dst_port=80,
            protocol="tcp",
            direction="in",
        )

        result = evaluator.evaluate(query)

        assert result.verdict == "ALLOW"
        assert len(result.matched_rules) == 1
        assert result.matched_rules[0].action == "accept"

    def test_simple_block(self, sample_rules):
        """Test simple block case."""
        evaluator = RuleEvaluator(sample_rules)
        query = Query(
            src_ip="10.0.0.50",
            dst_port=22,
            protocol="tcp",
            direction="in",
        )

        result = evaluator.evaluate(query)

        assert result.verdict == "BLOCK"
        assert len(result.matched_rules) == 1
        assert result.matched_rules[0].action == "drop"

    def test_no_match(self, sample_rules):
        """Test no matching rules."""
        evaluator = RuleEvaluator(sample_rules)
        query = Query(
            src_ip="1.2.3.4",
            dst_port=9999,
            protocol="tcp",
            direction="in",
        )

        result = evaluator.evaluate(query)

        assert result.verdict == "NO_MATCH"
        assert len(result.matched_rules) == 0

    def test_chain_filtering(self, sample_rules):
        """Test chain-based filtering."""
        evaluator = RuleEvaluator(sample_rules)
        query = Query(
            dst_ip="8.8.8.8",
            protocol="udp",
            direction="out",
        )

        result = evaluator.evaluate(query)

        assert result.verdict == "ALLOW"
        assert result.matched_rules[0].chain == "output"

    def test_first_match_wins(self):
        """Test first match wins policy."""
        rules = [
            Rule(
                action="accept",
                chain="input",
                table="filter",
                dport="80",
                protocol="tcp",
                line_number=1,
            ),
            Rule(
                action="drop",
                chain="input",
                table="filter",
                dport="80",
                protocol="tcp",
                line_number=2,
            ),
        ]
        evaluator = RuleEvaluator(rules)
        query = Query(dst_port=80, protocol="tcp", direction="in")

        result = evaluator.evaluate(query)

        assert result.verdict == "ALLOW"
        assert len(result.matched_rules) == 1
        assert result.matched_rules[0].line_number == 1

    def test_trace_logging(self, sample_rules):
        """Test that trace is populated."""
        evaluator = RuleEvaluator(sample_rules)
        query = Query(src_ip="192.168.1.10", dst_port=80, protocol="tcp")

        result = evaluator.evaluate(query)

        assert len(result.trace) > 0
        assert any("Evaluating query" in step for step in result.trace)


class TestRuleMatchesQuery:
    """Tests for _rule_matches_query method."""

    def test_exact_match(self):
        """Test exact matching."""
        rule = Rule(
            action="accept",
            chain="input",
            source="192.168.1.10",
            destination="10.0.0.5",
            sport="8080",
            dport="80",
            protocol="tcp",
            line_number=1,
        )
        query = Query(
            src_ip="192.168.1.10",
            dst_ip="10.0.0.5",
            src_port=8080,
            dst_port=80,
            protocol="tcp",
        )
        evaluator = RuleEvaluator([rule])

        assert evaluator._rule_matches_query(rule, query) is True

    def test_cidr_match(self):
        """Test CIDR matching."""
        rule = Rule(
            action="accept",
            chain="input",
            source="192.168.1.0/24",
            dport="80",
            protocol="tcp",
            line_number=1,
        )
        query = Query(src_ip="192.168.1.50", dst_port=80, protocol="tcp")
        evaluator = RuleEvaluator([rule])

        assert evaluator._rule_matches_query(rule, query) is True

    def test_partial_match_fails(self):
        """Test that partial matches fail."""
        rule = Rule(
            action="accept",
            chain="input",
            source="192.168.1.0/24",
            dport="80",
            protocol="tcp",
            line_number=1,
        )
        query = Query(
            src_ip="192.168.1.50",
            dst_port=443,  # Different port
            protocol="tcp",
        )
        evaluator = RuleEvaluator([rule])

        assert evaluator._rule_matches_query(rule, query) is False


class TestConflictDetection:
    """Tests for conflict detection."""

    def test_conflicting_actions(self):
        """Test detection of conflicting actions."""
        rules = [
            Rule(
                action="accept",
                chain="input",
                dport="80",
                protocol="tcp",
                line_number=1,
            ),
            Rule(
                action="accept",
                chain="input",
                dport="80",
                protocol="tcp",
                line_number=2,
            ),
        ]
        # Manually change second rule action to create conflict
        rules[1].action = "drop"

        evaluator = RuleEvaluator(rules)
        query = Query(dst_port=80, protocol="tcp")

        # First match wins, so it will be ALLOW, but should not report conflict
        # since first match terminates evaluation
        result = evaluator.evaluate(query)
        assert result.verdict == "ALLOW"


class TestRedundantRules:
    """Tests for redundant rule detection."""

    def test_find_redundant_rules(self):
        """Test finding redundant rules."""
        rules = [
            Rule(
                action="accept",
                chain="input",
                source="192.168.1.0/24",
                dport="80",
                protocol="tcp",
                line_number=1,
            ),
            Rule(
                action="accept",
                chain="input",
                source="192.168.1.10",  # More specific
                dport="80",
                protocol="tcp",
                line_number=2,
            ),
        ]
        evaluator = RuleEvaluator(rules)

        redundant = evaluator.find_redundant_rules()

        assert len(redundant) == 1
        assert redundant[0][0].line_number == 1  # General rule
        assert redundant[0][1].line_number == 2  # Specific rule

    def test_different_actions_not_redundant(self):
        """Test that different actions are not considered redundant."""
        rules = [
            Rule(
                action="accept",
                chain="input",
                source="192.168.1.0/24",
                line_number=1,
            ),
            Rule(
                action="drop",
                chain="input",
                source="192.168.1.10",
                line_number=2,
            ),
        ]
        evaluator = RuleEvaluator(rules)

        redundant = evaluator.find_redundant_rules()

        assert len(redundant) == 0


class TestGetChainForDirection:
    """Tests for _get_chain_for_direction method."""

    def test_direction_mapping(self):
        """Test direction to chain mapping."""
        evaluator = RuleEvaluator([])

        assert evaluator._get_chain_for_direction("in") == "input"
        assert evaluator._get_chain_for_direction("out") == "output"
        assert evaluator._get_chain_for_direction("forward") == "forward"
        assert evaluator._get_chain_for_direction("unknown") == "input"  # Default
