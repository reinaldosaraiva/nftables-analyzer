"""Tests for IPMatcher class."""

import pytest

from nftables_analyzer.evaluator.ip_matcher import IPMatcher


class TestIPMatches:
    """Tests for ip_matches method."""

    def test_exact_match(self):
        """Test exact IP address match."""
        assert IPMatcher.ip_matches("192.168.1.10", "192.168.1.10") is True
        assert IPMatcher.ip_matches("192.168.1.10", "192.168.1.11") is False

    def test_cidr_match(self):
        """Test CIDR range matching."""
        assert IPMatcher.ip_matches("192.168.1.10", "192.168.1.0/24") is True
        assert IPMatcher.ip_matches("192.168.2.10", "192.168.1.0/24") is False
        assert IPMatcher.ip_matches("192.168.1.255", "192.168.1.0/24") is True

    def test_cidr_edge_cases(self):
        """Test CIDR edge cases."""
        # /32 network (single IP)
        assert IPMatcher.ip_matches("192.168.1.1", "192.168.1.1/32") is True
        assert IPMatcher.ip_matches("192.168.1.2", "192.168.1.1/32") is False

        # /0 network (all IPs)
        assert IPMatcher.ip_matches("1.2.3.4", "0.0.0.0/0") is True
        assert IPMatcher.ip_matches("255.255.255.255", "0.0.0.0/0") is True

    def test_none_rule_ip(self):
        """Test when rule IP is None (no restriction)."""
        assert IPMatcher.ip_matches("192.168.1.10", None) is True
        assert IPMatcher.ip_matches(None, None) is True

    def test_none_packet_ip(self):
        """Test when packet IP is None."""
        assert IPMatcher.ip_matches(None, "192.168.1.0/24") is False

    def test_invalid_ip(self):
        """Test invalid IP addresses."""
        assert IPMatcher.ip_matches("invalid", "192.168.1.0/24") is False
        assert IPMatcher.ip_matches("192.168.1.10", "invalid") is False
        assert IPMatcher.ip_matches("999.999.999.999", "192.168.1.0/24") is False


class TestPortMatches:
    """Tests for port_matches method."""

    def test_exact_match(self):
        """Test exact port match."""
        assert IPMatcher.port_matches(80, "80") is True
        assert IPMatcher.port_matches(80, "443") is False

    def test_port_range(self):
        """Test port range matching."""
        assert IPMatcher.port_matches(443, "80-443") is True
        assert IPMatcher.port_matches(80, "80-443") is True
        assert IPMatcher.port_matches(200, "80-443") is True
        assert IPMatcher.port_matches(79, "80-443") is False
        assert IPMatcher.port_matches(444, "80-443") is False

    def test_none_rule_port(self):
        """Test when rule port is None (no restriction)."""
        assert IPMatcher.port_matches(80, None) is True
        assert IPMatcher.port_matches(65535, None) is True

    def test_none_packet_port(self):
        """Test when packet port is None."""
        assert IPMatcher.port_matches(None, "80") is False
        assert IPMatcher.port_matches(None, "80-443") is False

    def test_invalid_port(self):
        """Test invalid port values."""
        assert IPMatcher.port_matches(80, "invalid") is False
        assert IPMatcher.port_matches(80, "80-invalid") is False


class TestProtocolMatches:
    """Tests for protocol_matches method."""

    def test_exact_match(self):
        """Test exact protocol match."""
        assert IPMatcher.protocol_matches("tcp", "tcp") is True
        assert IPMatcher.protocol_matches("udp", "udp") is True
        assert IPMatcher.protocol_matches("tcp", "udp") is False

    def test_case_insensitive(self):
        """Test case-insensitive matching."""
        assert IPMatcher.protocol_matches("TCP", "tcp") is True
        assert IPMatcher.protocol_matches("tcp", "TCP") is True
        assert IPMatcher.protocol_matches("UdP", "udp") is True

    def test_any_protocol(self):
        """Test 'any' protocol matching."""
        assert IPMatcher.protocol_matches("tcp", "any") is True
        assert IPMatcher.protocol_matches("udp", "any") is True
        assert IPMatcher.protocol_matches("icmp", "any") is True

    def test_none_rule_protocol(self):
        """Test when rule protocol is None (no restriction)."""
        assert IPMatcher.protocol_matches("tcp", None) is True
        assert IPMatcher.protocol_matches("udp", None) is True

    def test_none_packet_protocol(self):
        """Test when packet protocol is None."""
        assert IPMatcher.protocol_matches(None, "tcp") is False


class TestMatches:
    """Tests for combined matches method."""

    def test_all_criteria_match(self):
        """Test when all criteria match."""
        assert (
            IPMatcher.matches(
                packet_ip="192.168.1.10",
                packet_port=80,
                packet_proto="tcp",
                rule_ip="192.168.1.0/24",
                rule_port="80",
                rule_proto="tcp",
            )
            is True
        )

    def test_one_criteria_fails(self):
        """Test when one criteria fails."""
        assert (
            IPMatcher.matches(
                packet_ip="192.168.1.10",
                packet_port=80,
                packet_proto="tcp",
                rule_ip="10.0.0.0/8",  # Different network
                rule_port="80",
                rule_proto="tcp",
            )
            is False
        )

    def test_all_none_rules(self):
        """Test when all rules are None (no restrictions)."""
        assert (
            IPMatcher.matches(
                packet_ip="192.168.1.10",
                packet_port=80,
                packet_proto="tcp",
                rule_ip=None,
                rule_port=None,
                rule_proto=None,
            )
            is True
        )
