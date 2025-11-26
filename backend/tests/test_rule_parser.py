"""Tests for RuleParser class."""

import json
import tempfile
from pathlib import Path

import pytest

from nftables_analyzer.models.rule import Rule
from nftables_analyzer.parser.rule_parser import RuleParser


class TestParseText:
    """Tests for parse_text method."""

    def test_simple_rule(self):
        """Test parsing simple rule."""
        text = "tcp dport 80 accept"
        rules = RuleParser.parse_text(text)

        assert len(rules) == 1
        assert rules[0].action == "accept"
        assert rules[0].dport == "80"
        assert rules[0].protocol == "tcp"

    def test_full_rule(self):
        """Test parsing rule with all fields."""
        text = "ip saddr 192.168.1.0/24 tcp dport 80 accept"
        rules = RuleParser.parse_text(text)

        assert len(rules) == 1
        assert rules[0].source == "192.168.1.0/24"
        assert rules[0].protocol == "tcp"
        assert rules[0].dport == "80"
        assert rules[0].action == "accept"

    def test_table_and_chain(self):
        """Test parsing with table and chain declarations."""
        text = """
        table ip filter
        chain input
        tcp dport 80 accept
        tcp dport 443 accept
        """
        rules = RuleParser.parse_text(text)

        assert len(rules) == 2
        assert rules[0].table == "filter"
        assert rules[0].chain == "input"
        assert rules[1].table == "filter"
        assert rules[1].chain == "input"

    def test_multiple_chains(self):
        """Test parsing multiple chains."""
        text = """
        chain input
        tcp dport 80 accept
        chain output
        tcp sport 80 accept
        """
        rules = RuleParser.parse_text(text)

        assert len(rules) == 2
        assert rules[0].chain == "input"
        assert rules[0].dport == "80"
        assert rules[1].chain == "output"
        assert rules[1].sport == "80"

    def test_drop_action(self):
        """Test parsing drop rules."""
        text = "tcp dport 22 drop"
        rules = RuleParser.parse_text(text)

        assert len(rules) == 1
        assert rules[0].action == "drop"

    def test_empty_input(self):
        """Test parsing empty input."""
        rules = RuleParser.parse_text("")
        assert len(rules) == 0

    def test_comments(self):
        """Test ignoring comments."""
        text = """
        # This is a comment
        tcp dport 80 accept
        # Another comment
        """
        rules = RuleParser.parse_text(text)

        assert len(rules) == 1


class TestParseJson:
    """Tests for parse_json method."""

    def test_nftables_format(self):
        """Test parsing nftables JSON format."""
        json_data = {
            "nftables": [
                {
                    "rule": {
                        "chain": "input",
                        "table": "filter",
                        "expr": [
                            {"match": {"left": {"payload": {"field": "dport"}}, "right": 80}},
                            {"accept": None},
                        ],
                    }
                }
            ]
        }
        json_str = json.dumps(json_data)
        rules = RuleParser.parse_json(json_str)

        assert len(rules) == 1
        assert rules[0].action == "accept"
        assert rules[0].chain == "input"

    def test_simple_list_format(self):
        """Test parsing simple list format."""
        json_data = [
            {
                "chain": "input",
                "table": "filter",
                "expr": [{"accept": None}],
            }
        ]
        json_str = json.dumps(json_data)
        rules = RuleParser.parse_json(json_str)

        assert len(rules) == 1
        assert rules[0].action == "accept"

    def test_empty_json(self):
        """Test parsing empty JSON."""
        rules = RuleParser.parse_json('{"nftables": []}')
        assert len(rules) == 0


class TestParseFile:
    """Tests for parse_file method."""

    def test_json_file(self):
        """Test parsing JSON file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
            json.dump({"nftables": []}, f)
            temp_path = Path(f.name)

        try:
            rules = RuleParser.parse_file(temp_path)
            assert isinstance(rules, list)
        finally:
            temp_path.unlink()

    def test_text_file(self):
        """Test parsing text file."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".txt", delete=False) as f:
            f.write("tcp dport 80 accept\n")
            temp_path = Path(f.name)

        try:
            rules = RuleParser.parse_file(temp_path)
            assert len(rules) == 1
            assert rules[0].action == "accept"
        finally:
            temp_path.unlink()

    def test_file_not_found(self):
        """Test handling non-existent file."""
        with pytest.raises(FileNotFoundError):
            RuleParser.parse_file(Path("/nonexistent/file.txt"))


class TestBuildTable:
    """Tests for build_table method."""

    def test_build_table(self, sample_rules):
        """Test building table from rules."""
        table = RuleParser.build_table(sample_rules)

        assert table.name == "filter"
        assert "input" in table.chains
        assert "output" in table.chains
        assert len(table.chains["input"].rules) == 2
        assert len(table.chains["output"].rules) == 1
