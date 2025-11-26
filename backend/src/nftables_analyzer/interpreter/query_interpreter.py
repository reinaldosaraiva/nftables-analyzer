"""Interprets natural language queries into Query objects."""

import re

from nftables_analyzer.models import Query


class QueryInterpreter:
    """Converts natural language to Query objects."""

    @staticmethod
    def parse(text: str) -> Query:
        """Parse natural language query into Query object."""
        text = text.lower().strip()

        # Extract source IP
        src_ip = QueryInterpreter._extract_ip(text, ["from", "source"])

        # Extract destination IP
        dst_ip = QueryInterpreter._extract_ip(text, ["to", "destination", "dest"])

        # Extract source port
        src_port = QueryInterpreter._extract_port(text, ["from port", "source port", "sport"])

        # Extract destination port
        dst_port = QueryInterpreter._extract_port(
            text, ["to port", "port", "destination port", "dport", "on port"]
        )

        # Extract protocol
        protocol = QueryInterpreter._extract_protocol(text)

        # Extract direction
        direction = QueryInterpreter._extract_direction(text)

        return Query(
            src_ip=src_ip,
            dst_ip=dst_ip,
            src_port=src_port,
            dst_port=dst_port,
            protocol=protocol,
            direction=direction,
        )

    @staticmethod
    def _extract_ip(text: str, keywords: list[str]) -> str | None:
        """Extract IP address after keywords."""
        for keyword in keywords:
            # Match IP address (with optional CIDR)
            pattern = rf"{keyword}\s+([\d\.\/]+)"
            match = re.search(pattern, text)
            if match:
                return match.group(1)
        return None

    @staticmethod
    def _extract_port(text: str, keywords: list[str]) -> int | None:
        """Extract port number after keywords."""
        for keyword in keywords:
            pattern = rf"{keyword}\s+(\d+)"
            match = re.search(pattern, text)
            if match:
                return int(match.group(1))
        return None

    @staticmethod
    def _extract_protocol(text: str) -> str | None:
        """Extract protocol from text."""
        protocols = ["tcp", "udp", "icmp"]
        for proto in protocols:
            if re.search(rf"\b{proto}\b", text):
                return proto
        return None

    @staticmethod
    def _extract_direction(text: str) -> str:
        """Extract traffic direction from text."""
        if re.search(r"\b(incoming|inbound|in)\b", text):
            return "in"
        elif re.search(r"\b(outgoing|outbound|out)\b", text):
            return "out"
        elif re.search(r"\bforward", text):
            return "forward"
        return "in"  # Default

    @staticmethod
    def help_text() -> str:
        """Return help text for query syntax."""
        return """
Natural Language Query Examples:

  "from 192.168.1.10 to 10.0.0.5 port 80 tcp"
  "incoming traffic from 192.168.0.0/24 to port 443"
  "outgoing tcp to 8.8.8.8 port 53"
  "from 172.16.0.1 source port 12345 to 192.168.1.1 port 22"

Keywords:
  - Source: from, source
  - Destination: to, destination, dest
  - Port: port, dport, sport, on port
  - Protocol: tcp, udp, icmp
  - Direction: in/incoming/inbound, out/outgoing/outbound, forward
"""
