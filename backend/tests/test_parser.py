"""Tests for the nftables rule parser."""

import pytest

from nftables_analyzer.parser.rule_parser import RuleParser


class TestParseTextHierarchical:
    """Tests for parse_text_hierarchical method."""

    def test_parse_single_table(self):
        """Test parsing a single table with chains."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        assert len(result.tables) == 1
        table = result.tables["inet_filter"]
        assert table.name == "filter"
        assert table.family == "inet"
        assert table.chain_count == 1
        assert table.rule_count == 2

        chain = table.chains["input"]
        assert chain.name == "input"
        assert chain.type == "filter"
        assert chain.hook == "input"
        assert chain.policy == "drop"
        assert chain.rule_count == 2

    def test_parse_multiple_tables(self):
        """Test parsing multiple tables."""
        content = """table inet mangle {
    chain prerouting {
        type filter hook prerouting priority mangle; policy accept;
    }
}
table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        assert len(result.tables) == 2
        assert "inet_mangle" in result.tables
        assert "inet_filter" in result.tables

    def test_parse_sets(self):
        """Test parsing set definitions."""
        content = """table inet filter {
    set allowed_ports {
        type inet_service
        flags interval
        elements = { 22, 80, 443 }
    }

    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport @allowed_ports accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        table = result.tables["inet_filter"]
        assert table.set_count == 1
        assert "allowed_ports" in table.sets

        set_def = table.sets["allowed_ports"]
        assert set_def.name == "allowed_ports"
        assert set_def.type == "inet_service"
        assert "interval" in set_def.flags
        assert len(set_def.elements) >= 1

    def test_parse_set_references_in_rules(self):
        """Test that set references are extracted from rules."""
        content = """table inet filter {
    set outside {
        type iface_index
        elements = { "eth0" }
    }

    chain input {
        type filter hook input priority 0; policy accept;
        iif @outside tcp dport 22 accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        assert len(rules) == 1
        assert "outside" in rules[0].sets_referenced

    def test_parse_rule_with_interfaces(self):
        """Test parsing rules with interface specifications."""
        content = """table inet filter {
    chain forward {
        type filter hook forward priority 0; policy drop;
        iif eth0 oif eth1 accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        assert len(rules) == 1
        assert rules[0].iif == "eth0"
        assert rules[0].oif == "eth1"

    def test_parse_various_actions(self):
        """Test parsing rules with different actions."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 23 drop
        tcp dport 25 reject
        tcp dport 80 counter
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        actions = [r.action for r in rules]
        assert "accept" in actions
        assert "drop" in actions
        assert "reject" in actions
        assert "counter" in actions

    def test_parse_protocols(self):
        """Test parsing rules with different protocols."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        udp dport 53 accept
        icmp type echo-request accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        protocols = [r.protocol for r in rules]
        assert "tcp" in protocols
        assert "udp" in protocols
        assert "icmp" in protocols

    def test_parse_ip_addresses(self):
        """Test parsing rules with IP address specifications."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        ip saddr 192.168.1.0/24 accept
        ip daddr 10.0.0.1 drop
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        assert rules[0].source == "192.168.1.0/24"
        assert rules[1].destination == "10.0.0.1"

    def test_get_all_rules_sorted(self):
        """Test that get_all_rules returns rules sorted by line number."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
        tcp dport 443 accept
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        rules = result.get_all_rules()
        line_numbers = [r.line_number for r in rules]
        assert line_numbers == sorted(line_numbers)

    def test_get_all_sets(self):
        """Test get_all_sets method."""
        content = """table inet filter {
    set set1 {
        type ipv4_addr
    }
    set set2 {
        type inet_service
    }
    chain input {
        type filter hook input priority 0; policy accept;
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        sets = result.get_all_sets()
        assert len(sets) == 2
        names = [s.name for s in sets]
        assert "set1" in names
        assert "set2" in names


class TestParseText:
    """Tests for the legacy parse_text method."""

    def test_returns_flat_rules_list(self):
        """Test that parse_text returns a flat list of rules."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
    }
}"""
        rules = RuleParser.parse_text(content)

        assert isinstance(rules, list)
        assert len(rules) == 2
        assert all(hasattr(r, "action") for r in rules)


class TestComplexConfiguration:
    """Tests for complex real-world configurations."""

    def test_parse_mangle_table_with_tcp_options(self):
        """Test parsing mangle table with TCP options."""
        content = """table inet mangle {
    set outside {
        type iface_index
        elements = { "vlan723", "vlan722" }
    }

    chain postrouting {
        type filter hook postrouting priority mangle; policy accept;
        oif @outside tcp flags syn / syn,rst counter packets 1240251 bytes 74304508 tcp option maxseg size set rt mtu
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        assert "inet_mangle" in result.tables
        table = result.tables["inet_mangle"]
        assert table.set_count == 1
        assert "outside" in table.sets

        # Verify set elements
        outside_set = table.sets["outside"]
        assert "vlan723" in outside_set.elements or len(outside_set.elements) > 0

    def test_parse_multiple_chain_types(self):
        """Test parsing different chain types and hooks."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
    }
    chain output {
        type filter hook output priority 0; policy accept;
    }
    chain forward {
        type filter hook forward priority 0; policy drop;
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        table = result.tables["inet_filter"]
        assert table.chain_count == 3

        assert table.chains["input"].hook == "input"
        assert table.chains["output"].hook == "output"
        assert table.chains["forward"].hook == "forward"

    def test_parse_nat_table(self):
        """Test parsing NAT table configuration."""
        content = """table inet nat {
    chain prerouting {
        type nat hook prerouting priority -100; policy accept;
    }
    chain postrouting {
        type nat hook postrouting priority 100; policy accept;
    }
}"""
        result = RuleParser.parse_text_hierarchical(content)

        assert "inet_nat" in result.tables
        table = result.tables["inet_nat"]

        prerouting = table.chains["prerouting"]
        assert prerouting.type == "nat"
        assert prerouting.hook == "prerouting"

        postrouting = table.chains["postrouting"]
        assert postrouting.type == "nat"
        assert postrouting.hook == "postrouting"
