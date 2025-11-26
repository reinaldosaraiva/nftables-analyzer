"""Parser for nftables rules from JSON or text format."""

import json
import re
from pathlib import Path
from typing import Any

from nftables_analyzer.models import Chain, Rule, Table


class RuleParser:
    """Parses nftables rules from various formats."""

    @staticmethod
    def parse_file(path: Path) -> list[Rule]:
        """Parse rules from a file (JSON or text format)."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text()

        # Try JSON first
        if path.suffix == ".json":
            return RuleParser.parse_json(content)

        # Otherwise parse as text
        return RuleParser.parse_text(content)

    @staticmethod
    def parse_json(json_str: str) -> list[Rule]:
        """Parse nftables JSON output."""
        data = json.loads(json_str)
        rules: list[Rule] = []
        line_number = 1

        # Handle nftables JSON format
        if "nftables" in data:
            for item in data["nftables"]:
                if "rule" in item:
                    rule_data = item["rule"]
                    rule = RuleParser._parse_json_rule(rule_data, line_number)
                    if rule:
                        rules.append(rule)
                        line_number += 1
        # Handle simple list format
        elif isinstance(data, list):
            for rule_data in data:
                rule = RuleParser._parse_json_rule(rule_data, line_number)
                if rule:
                    rules.append(rule)
                    line_number += 1

        return rules

    @staticmethod
    def _parse_json_rule(rule_data: dict[str, Any], line_number: int) -> Rule | None:
        """Parse a single rule from JSON data."""
        try:
            # Extract action (verdict)
            action = "accept"
            if "expr" in rule_data:
                for expr in rule_data["expr"]:
                    if "accept" in expr:
                        action = "accept"
                    elif "drop" in expr:
                        action = "drop"
                    elif "reject" in expr:
                        action = "reject"
                    elif "jump" in expr:
                        action = "jump"
                    elif "return" in expr:
                        action = "return"

            # Extract match criteria
            source = None
            destination = None
            sport = None
            dport = None
            protocol = None

            if "expr" in rule_data:
                for expr in rule_data["expr"]:
                    if "match" in expr:
                        match = expr["match"]
                        if "left" in match and "right" in match:
                            left = match["left"]
                            right = match["right"]

                            # IP addresses
                            if "payload" in left:
                                payload = left["payload"]
                                if payload.get("field") == "saddr":
                                    source = right if isinstance(right, str) else str(right)
                                elif payload.get("field") == "daddr":
                                    destination = right if isinstance(right, str) else str(right)
                                elif payload.get("field") == "sport":
                                    sport = str(right)
                                elif payload.get("field") == "dport":
                                    dport = str(right)
                                elif payload.get("field") == "protocol":
                                    protocol = right if isinstance(right, str) else str(right)

            return Rule(
                action=action,
                chain=rule_data.get("chain", "input"),
                table=rule_data.get("table", "filter"),
                source=source,
                destination=destination,
                sport=sport,
                dport=dport,
                protocol=protocol,
                line_number=line_number,
                raw=json.dumps(rule_data),
            )
        except Exception as e:
            print(f"Warning: Failed to parse rule: {e}")
            return None

    @staticmethod
    def parse_text(text: str) -> list[Rule]:
        """Parse nftables rules from text format."""
        rules: list[Rule] = []
        current_table = "filter"
        current_chain = "input"
        line_number = 0

        for line in text.split("\n"):
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            line_number += 1

            # Table declaration
            if line.startswith("table"):
                match = re.match(r"table\s+(\w+)\s+(\w+)", line)
                if match:
                    current_table = match.group(2)
                continue

            # Chain declaration
            if line.startswith("chain"):
                match = re.match(r"chain\s+(\w+)", line)
                if match:
                    current_chain = match.group(1)
                continue

            # Rule parsing
            rule = RuleParser._parse_text_rule(line, current_table, current_chain, line_number)
            if rule:
                rules.append(rule)

        return rules

    @staticmethod
    def _parse_text_rule(
        line: str, table: str, chain: str, line_number: int
    ) -> Rule | None:
        """Parse a single rule from text format."""
        try:
            # Extract action
            action = "accept"
            if "accept" in line:
                action = "accept"
            elif "drop" in line:
                action = "drop"
            elif "reject" in line:
                action = "reject"
            elif "jump" in line:
                action = "jump"
            elif "return" in line:
                action = "return"

            # Extract protocol
            protocol = None
            proto_match = re.search(r"(?:tcp|udp|icmp)\s+(?:dport|sport)", line)
            if proto_match:
                protocol = proto_match.group(0).split()[0]

            # Extract IP addresses
            source = None
            src_match = re.search(r"(?:ip\s+)?saddr\s+([\d\.\/]+)", line)
            if src_match:
                source = src_match.group(1)

            destination = None
            dst_match = re.search(r"(?:ip\s+)?daddr\s+([\d\.\/]+)", line)
            if dst_match:
                destination = dst_match.group(1)

            # Extract ports
            sport = None
            sport_match = re.search(r"sport\s+(\d+)", line)
            if sport_match:
                sport = sport_match.group(1)

            dport = None
            dport_match = re.search(r"dport\s+(\d+)", line)
            if dport_match:
                dport = dport_match.group(1)

            return Rule(
                action=action,
                chain=chain,
                table=table,
                source=source,
                destination=destination,
                sport=sport,
                dport=dport,
                protocol=protocol,
                line_number=line_number,
                raw=line,
            )
        except Exception as e:
            print(f"Warning: Failed to parse line {line_number}: {e}")
            return None

    @staticmethod
    def build_table(rules: list[Rule]) -> Table:
        """Build a Table structure from a list of rules."""
        table = Table()

        for rule in rules:
            chain = table.get_chain(rule.chain)
            if not chain:
                chain = Chain(name=rule.chain, table=rule.table)
                table.add_chain(chain)
            chain.add_rule(rule)

        return table
