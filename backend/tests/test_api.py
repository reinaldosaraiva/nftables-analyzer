"""Tests for the API endpoints."""

import pytest
from fastapi.testclient import TestClient

from nftables_analyzer.api.main import app


@pytest.fixture
def client():
    """Create test client."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests for the health endpoint."""

    def test_health_check(self, client):
        """Test health endpoint returns healthy status."""
        response = client.get("/api/v1/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        assert data["service"] == "nftables-analyzer"


class TestParseEndpoint:
    """Tests for the parse endpoint."""

    def test_parse_simple_rules(self, client):
        """Test parsing simple rules."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["count"] == 2
        assert len(data["rules"]) == 2
        assert "graph" in data

    def test_parse_empty_content(self, client):
        """Test parsing empty content returns error."""
        response = client.post(
            "/api/v1/rules/parse",
            json={"content": "", "format": "text"},
        )

        assert response.status_code == 400

    def test_parse_invalid_format(self, client):
        """Test parsing with only comments."""
        response = client.post(
            "/api/v1/rules/parse",
            json={"content": "# Just a comment", "format": "text"},
        )

        assert response.status_code == 400


class TestParseHierarchyEndpoint:
    """Tests for the hierarchical parse endpoint."""

    def test_parse_hierarchy_basic(self, client):
        """Test hierarchical parsing returns expected structure."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check tables
        assert len(data["tables"]) == 1
        table = data["tables"][0]
        assert table["name"] == "filter"
        assert table["family"] == "inet"

        # Check chains
        assert len(table["chains"]) == 1
        chain = table["chains"][0]
        assert chain["name"] == "input"
        assert chain["type"] == "filter"
        assert chain["hook"] == "input"
        assert chain["policy"] == "drop"
        assert chain["rule_count"] == 1

        # Check stats
        stats = data["stats"]
        assert stats["total_rules"] == 1
        assert stats["total_tables"] == 1
        assert stats["total_chains"] == 1

        # Check tree_nodes
        assert len(data["tree_nodes"]) > 0
        node_types = [n["type"] for n in data["tree_nodes"]]
        assert "table" in node_types
        assert "chain" in node_types
        assert "rule" in node_types

    def test_parse_hierarchy_with_sets(self, client):
        """Test hierarchical parsing includes sets."""
        content = """table inet filter {
    set allowed_ips {
        type ipv4_addr
        elements = { 192.168.1.1, 192.168.1.2 }
    }

    chain input {
        type filter hook input priority 0; policy drop;
        ip saddr @allowed_ips accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        # Check sets in table
        table = data["tables"][0]
        assert table["set_count"] == 1
        assert len(table["sets"]) == 1

        # Check sets in response
        assert len(data["sets"]) == 1
        set_def = data["sets"][0]
        assert set_def["name"] == "allowed_ips"

        # Check stats
        assert data["stats"]["total_sets"] == 1

        # Check set tree node
        set_nodes = [n for n in data["tree_nodes"] if n["type"] == "set"]
        assert len(set_nodes) == 1

    def test_parse_hierarchy_multiple_tables(self, client):
        """Test hierarchical parsing with multiple tables."""
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
}
table inet nat {
    chain postrouting {
        type nat hook postrouting priority 100; policy accept;
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        assert data["stats"]["total_tables"] == 3
        table_names = [t["name"] for t in data["tables"]]
        assert "mangle" in table_names
        assert "filter" in table_names
        assert "nat" in table_names

    def test_parse_hierarchy_stats_by_action(self, client):
        """Test that stats include rules grouped by action."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 23 drop
        tcp dport 24 reject
        tcp dport 25 accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        stats = data["stats"]
        assert stats["rules_by_action"]["accept"] == 2
        assert stats["rules_by_action"]["drop"] == 1
        assert stats["rules_by_action"]["reject"] == 1

    def test_parse_hierarchy_stats_by_protocol(self, client):
        """Test that stats include rules grouped by protocol."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
        udp dport 53 accept
        icmp type echo-request accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        stats = data["stats"]
        assert stats["rules_by_protocol"]["tcp"] == 2
        assert stats["rules_by_protocol"]["udp"] == 1
        assert stats["rules_by_protocol"]["icmp"] == 1

    def test_parse_hierarchy_tree_node_structure(self, client):
        """Test that tree nodes have correct parent-child relationships."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
    }
}"""
        response = client.post(
            "/api/v1/rules/parse/hierarchy",
            json={"content": content, "format": "text"},
        )

        assert response.status_code == 200
        data = response.json()

        nodes = {n["id"]: n for n in data["tree_nodes"]}

        # Find table node
        table_nodes = [n for n in data["tree_nodes"] if n["type"] == "table"]
        assert len(table_nodes) == 1
        table_node = table_nodes[0]
        assert table_node["depth"] == 0
        assert table_node["parent_id"] is None

        # Find chain node
        chain_nodes = [n for n in data["tree_nodes"] if n["type"] == "chain"]
        assert len(chain_nodes) == 1
        chain_node = chain_nodes[0]
        assert chain_node["depth"] == 1
        assert chain_node["parent_id"] == table_node["id"]

        # Find rule node
        rule_nodes = [n for n in data["tree_nodes"] if n["type"] == "rule"]
        assert len(rule_nodes) == 1
        rule_node = rule_nodes[0]
        assert rule_node["depth"] == 2
        assert rule_node["parent_id"] == chain_node["id"]


class TestQueryEndpoint:
    """Tests for the query endpoint."""

    def test_query_matching_rule(self, client):
        """Test querying rules that match."""
        content = """table inet filter {
    chain input {
        type filter hook input priority 0; policy drop;
        tcp dport 22 accept
        tcp dport 80 accept
    }
}"""
        response = client.post(
            "/api/v1/rules/query",
            json={
                "rules_content": content,
                "rules_format": "text",
                "dst_port": 22,
                "protocol": "tcp",
            },
        )

        assert response.status_code == 200
        data = response.json()
        assert data["verdict"] in ["ALLOW", "BLOCK", "NO_MATCH", "CONFLICT"]
