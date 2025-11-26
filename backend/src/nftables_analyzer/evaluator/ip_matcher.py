"""IP and port matching logic using CIDR notation."""

import ipaddress
from typing import Any


class IPMatcher:
    """Matches IP addresses and ports against rules."""

    @staticmethod
    def ip_matches(packet_ip: str | None, rule_ip: str | None) -> bool:
        """Check if packet IP matches rule IP (supports CIDR)."""
        if rule_ip is None:
            return True  # No restriction
        if packet_ip is None:
            return False  # No packet IP provided

        try:
            # Parse packet IP
            packet_addr = ipaddress.ip_address(packet_ip)

            # Check if rule is a network (CIDR)
            if "/" in rule_ip:
                rule_network = ipaddress.ip_network(rule_ip, strict=False)
                return packet_addr in rule_network
            else:
                # Exact IP match
                rule_addr = ipaddress.ip_address(rule_ip)
                return packet_addr == rule_addr
        except ValueError:
            return False

    @staticmethod
    def port_matches(packet_port: int | None, rule_port: str | None) -> bool:
        """Check if packet port matches rule port (supports ranges)."""
        if rule_port is None:
            return True  # No restriction
        if packet_port is None:
            return False  # No packet port provided

        try:
            # Handle port ranges (e.g., "80-443")
            if "-" in rule_port:
                start, end = rule_port.split("-")
                return int(start) <= packet_port <= int(end)
            else:
                # Exact port match
                return packet_port == int(rule_port)
        except ValueError:
            return False

    @staticmethod
    def protocol_matches(packet_proto: str | None, rule_proto: str | None) -> bool:
        """Check if packet protocol matches rule protocol."""
        if rule_proto is None or rule_proto == "any":
            return True  # No restriction
        if packet_proto is None:
            return False  # No packet protocol provided

        return packet_proto.lower() == rule_proto.lower()

    @staticmethod
    def matches(
        packet_ip: str | None,
        packet_port: int | None,
        packet_proto: str | None,
        rule_ip: str | None,
        rule_port: str | None,
        rule_proto: str | None,
    ) -> bool:
        """Check if all criteria match."""
        return (
            IPMatcher.ip_matches(packet_ip, rule_ip)
            and IPMatcher.port_matches(packet_port, rule_port)
            and IPMatcher.protocol_matches(packet_proto, rule_proto)
        )
