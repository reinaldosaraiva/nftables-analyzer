"""Tests for QueryInterpreter class."""

import pytest

from nftables_analyzer.interpreter.query_interpreter import QueryInterpreter


class TestParseQuery:
    """Tests for parse method."""

    def test_simple_query(self):
        """Test parsing simple query."""
        query = QueryInterpreter.parse("from 192.168.1.10 to 10.0.0.5 port 80")

        assert query.src_ip == "192.168.1.10"
        assert query.dst_ip == "10.0.0.5"
        assert query.dst_port == 80

    def test_with_protocol(self):
        """Test parsing query with protocol."""
        query = QueryInterpreter.parse("tcp from 192.168.1.10 to 10.0.0.5 port 80")

        assert query.protocol == "tcp"
        assert query.src_ip == "192.168.1.10"
        assert query.dst_ip == "10.0.0.5"
        assert query.dst_port == 80

    def test_cidr_notation(self):
        """Test parsing CIDR notation."""
        query = QueryInterpreter.parse("from 192.168.1.0/24 to 10.0.0.0/8")

        assert query.src_ip == "192.168.1.0/24"
        assert query.dst_ip == "10.0.0.0/8"

    def test_both_ports(self):
        """Test parsing source and destination ports."""
        query = QueryInterpreter.parse("from port 8080 to 10.0.0.5 port 80")

        assert query.src_port == 8080
        assert query.dst_port == 80

    def test_direction_incoming(self):
        """Test parsing incoming direction."""
        query = QueryInterpreter.parse("incoming traffic from 192.168.1.10")

        assert query.direction == "in"
        assert query.src_ip == "192.168.1.10"

    def test_direction_outgoing(self):
        """Test parsing outgoing direction."""
        query = QueryInterpreter.parse("outgoing traffic to 8.8.8.8")

        assert query.direction == "out"
        assert query.dst_ip == "8.8.8.8"

    def test_direction_forward(self):
        """Test parsing forward direction."""
        query = QueryInterpreter.parse("forward from 192.168.1.10 to 10.0.0.5")

        assert query.direction == "forward"

    def test_udp_protocol(self):
        """Test parsing UDP protocol."""
        query = QueryInterpreter.parse("udp from 192.168.1.10 to 10.0.0.5 port 53")

        assert query.protocol == "udp"
        assert query.dst_port == 53

    def test_icmp_protocol(self):
        """Test parsing ICMP protocol."""
        query = QueryInterpreter.parse("icmp from 192.168.1.10 to 10.0.0.5")

        assert query.protocol == "icmp"

    def test_case_insensitive(self):
        """Test case-insensitive parsing."""
        query = QueryInterpreter.parse("FROM 192.168.1.10 TO 10.0.0.5 PORT 80 TCP")

        assert query.src_ip == "192.168.1.10"
        assert query.dst_ip == "10.0.0.5"
        assert query.dst_port == 80
        assert query.protocol == "tcp"

    def test_alternative_keywords(self):
        """Test alternative keywords."""
        query = QueryInterpreter.parse("source 192.168.1.10 destination 10.0.0.5 dport 80")

        assert query.src_ip == "192.168.1.10"
        assert query.dst_ip == "10.0.0.5"
        assert query.dst_port == 80

    def test_minimal_query(self):
        """Test minimal query."""
        query = QueryInterpreter.parse("port 80")

        assert query.dst_port == 80
        assert query.src_ip is None
        assert query.dst_ip is None

    def test_empty_query(self):
        """Test empty query."""
        query = QueryInterpreter.parse("")

        assert query.src_ip is None
        assert query.dst_ip is None
        assert query.src_port is None
        assert query.dst_port is None
        assert query.protocol is None
        assert query.direction == "in"  # Default

    def test_on_port_keyword(self):
        """Test 'on port' keyword."""
        query = QueryInterpreter.parse("to 10.0.0.5 on port 443")

        assert query.dst_ip == "10.0.0.5"
        assert query.dst_port == 443


class TestHelpText:
    """Tests for help_text method."""

    def test_help_text_exists(self):
        """Test that help text is provided."""
        help_text = QueryInterpreter.help_text()

        assert isinstance(help_text, str)
        assert len(help_text) > 0
        assert "from" in help_text.lower()
        assert "port" in help_text.lower()
