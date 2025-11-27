"""Parser for nftables rules from JSON or text format."""

import json
import re
from pathlib import Path
from typing import Any

from nftables_analyzer.models import Chain, Rule, SetDefinition, Table


class ParseResult:
    """Result of parsing nftables configuration."""

    def __init__(self) -> None:
        self.tables: dict[str, Table] = {}
        self.rules: list[Rule] = []

    def add_table(self, table: Table) -> None:
        """Add or update a table."""
        key = f"{table.family}_{table.name}"
        if key not in self.tables:
            self.tables[key] = table
        else:
            # Merge sets and chains
            existing = self.tables[key]
            for name, chain in table.chains.items():
                existing.chains[name] = chain
            for name, set_def in table.sets.items():
                existing.sets[name] = set_def

    def get_all_rules(self) -> list[Rule]:
        """Get flat list of all rules across all tables/chains."""
        rules = []
        for table in self.tables.values():
            for chain in table.chains.values():
                rules.extend(chain.rules)
        return sorted(rules, key=lambda r: r.line_number)

    def get_all_sets(self) -> list[SetDefinition]:
        """Get flat list of all sets."""
        sets = []
        for table in self.tables.values():
            sets.extend(table.sets.values())
        return sets


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
    def parse_file_hierarchical(path: Path) -> ParseResult:
        """Parse rules from a file and return hierarchical structure."""
        if not path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        content = path.read_text()

        if path.suffix == ".json":
            return RuleParser.parse_json_hierarchical(content)

        return RuleParser.parse_text_hierarchical(content)

    @staticmethod
    def parse_json(json_str: str) -> list[Rule]:
        """Parse nftables JSON output."""
        result = RuleParser.parse_json_hierarchical(json_str)
        return result.get_all_rules()

    @staticmethod
    def parse_json_hierarchical(json_str: str) -> ParseResult:
        """Parse nftables JSON output with full hierarchy."""
        data = json.loads(json_str)
        result = ParseResult()
        line_number = 1

        # Handle nftables JSON format
        if "nftables" in data:
            for item in data["nftables"]:
                if "rule" in item:
                    rule_data = item["rule"]
                    rule = RuleParser._parse_json_rule(rule_data, line_number)
                    if rule:
                        result.rules.append(rule)
                        line_number += 1
        elif isinstance(data, list):
            for rule_data in data:
                rule = RuleParser._parse_json_rule(rule_data, line_number)
                if rule:
                    result.rules.append(rule)
                    line_number += 1

        return result

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
        result = RuleParser.parse_text_hierarchical(text)
        return result.get_all_rules()

    @staticmethod
    def parse_text_hierarchical(text: str) -> ParseResult:
        """Parse nftables text format with full hierarchy extraction."""
        result = ParseResult()

        current_table: Table | None = None
        current_chain: Chain | None = None
        current_set: SetDefinition | None = None

        in_set_block = False
        set_elements: list[str] = []
        brace_depth = 0

        lines = text.split("\n")
        line_number = 0

        for line in lines:
            line_number += 1
            original_line = line
            line = line.strip()

            if not line or line.startswith("#"):
                continue

            # Track brace depth
            brace_depth += line.count("{") - line.count("}")

            # Table declaration: "table inet filter {"
            table_match = re.match(r"table\s+(\w+)\s+(\w+)\s*\{?", line)
            if table_match:
                family = table_match.group(1)
                table_name = table_match.group(2)
                current_table = Table(
                    name=table_name,
                    family=family,
                    line_number=line_number
                )
                result.add_table(current_table)
                current_chain = None
                current_set = None
                in_set_block = False
                continue

            # Set declaration: "set setname {"
            set_match = re.match(r"set\s+([\w\-]+)\s*\{?", line)
            if set_match and current_table and not in_set_block:
                set_name = set_match.group(1)
                current_set = SetDefinition(
                    name=set_name,
                    table=current_table.name,
                    family=current_table.family,
                    type="unknown",
                    line_number=line_number
                )
                in_set_block = True
                set_elements = []
                continue

            # Inside set block
            if in_set_block and current_set:
                # Type declaration
                type_match = re.match(r"type\s+(.+)", line)
                if type_match:
                    current_set.type = type_match.group(1).strip()
                    continue

                # Flags declaration
                flags_match = re.match(r"flags\s+(.+)", line)
                if flags_match:
                    current_set.flags = [f.strip() for f in flags_match.group(1).split(",")]
                    continue

                # Elements declaration (can span multiple lines)
                elements_match = re.match(r"elements\s*=\s*\{(.+)\}?", line)
                if elements_match:
                    elem_str = elements_match.group(1)
                    # Parse elements (handle quotes and commas)
                    for elem in re.findall(r'"([^"]+)"|([^,\s\}]+)', elem_str):
                        e = elem[0] or elem[1]
                        if e and e not in ("{", "}"):
                            set_elements.append(e.strip())
                    continue

                # Multi-line elements
                if "elements" not in line and not line.startswith("type") and not line.startswith("flags"):
                    for elem in re.findall(r'"([^"]+)"|([^,\s\}]+)', line):
                        e = elem[0] or elem[1]
                        if e and e not in ("{", "}"):
                            set_elements.append(e.strip())

                # End of set block
                if "}" in line:
                    current_set.elements = set_elements
                    if current_table:
                        current_table.add_set(current_set)
                    in_set_block = False
                    current_set = None
                continue

            # Chain declaration: "chain chainname {"
            chain_match = re.match(r"chain\s+([\w\-]+)\s*\{?", line)
            if chain_match and current_table:
                chain_name = chain_match.group(1)
                current_chain = Chain(
                    name=chain_name,
                    table=current_table.name,
                    family=current_table.family,
                    line_number=line_number
                )
                current_table.add_chain(current_chain)
                continue

            # Chain type/hook/policy: "type filter hook input priority filter; policy accept;"
            if current_chain and line.startswith("type"):
                type_match = re.match(
                    r"type\s+(\w+)\s+hook\s+(\w+)\s+priority\s+([^;]+);\s*(?:policy\s+(\w+);)?",
                    line
                )
                if type_match:
                    current_chain.type = type_match.group(1)
                    current_chain.hook = type_match.group(2)
                    current_chain.priority = type_match.group(3)
                    if type_match.group(4):
                        current_chain.policy = type_match.group(4)
                continue

            # End of block (closing brace only)
            if line == "}":
                if brace_depth == 1:
                    current_chain = None
                elif brace_depth == 0:
                    current_table = None
                continue

            # Rule parsing (anything else inside a chain)
            if current_chain and current_table:
                rule = RuleParser._parse_text_rule(
                    original_line,
                    current_table.name,
                    current_chain.name,
                    current_table.family,
                    line_number,
                )
                if rule:
                    # Find set references in the rule
                    set_refs = re.findall(r"@([\w\-]+)", original_line)
                    rule.sets_referenced = list(set(set_refs))

                    current_chain.add_rule(rule)
                    result.rules.append(rule)

        return result

    @staticmethod
    def _parse_text_rule(
        line: str, table: str, chain: str, family: str, line_number: int
    ) -> Rule | None:
        """Parse a single rule from text format."""
        try:
            line_stripped = line.strip()

            # Skip chain metadata lines
            if line_stripped.startswith("type ") or line_stripped == "}" or line_stripped == "{":
                return None

            # Extract action
            action = "accept"
            if " accept" in line_stripped:
                action = "accept"
            elif " drop" in line_stripped:
                action = "drop"
            elif " reject" in line_stripped:
                action = "reject"
            elif " jump " in line_stripped:
                action = "jump"
            elif " return" in line_stripped:
                action = "return"
            elif " counter " in line_stripped or line_stripped.endswith("counter"):
                action = "counter"
            elif " log " in line_stripped:
                action = "log"
            else:
                # No recognizable action, might be a counter-only or incomplete rule
                if not any(kw in line_stripped for kw in ["tcp", "udp", "icmp", "ip", "iif", "oif", "ct"]):
                    return None
                action = "accept"  # Default

            # Extract protocol
            protocol = None
            if "tcp " in line_stripped or " tcp" in line_stripped:
                protocol = "tcp"
            elif "udp " in line_stripped or " udp" in line_stripped:
                protocol = "udp"
            elif "icmp " in line_stripped or " icmp" in line_stripped:
                protocol = "icmp"
            elif "icmpv6 " in line_stripped:
                protocol = "icmpv6"
            elif " ah " in line_stripped or " ah" in line_stripped:
                protocol = "ah"
            elif " esp " in line_stripped or " esp" in line_stripped:
                protocol = "esp"

            # Extract IP addresses
            source = None
            src_match = re.search(r"(?:ip|ip6)?\s*saddr\s+([\d\./a-fA-F:]+|\@[\w\-]+)", line_stripped)
            if src_match:
                source = src_match.group(1)

            destination = None
            dst_match = re.search(r"(?:ip|ip6)?\s*daddr\s+([\d\./a-fA-F:]+|\@[\w\-]+)", line_stripped)
            if dst_match:
                destination = dst_match.group(1)

            # Extract ports
            sport = None
            sport_match = re.search(r"sport\s+(\d+(?:-\d+)?|\@[\w\-]+)", line_stripped)
            if sport_match:
                sport = sport_match.group(1)

            dport = None
            dport_match = re.search(r"dport\s+(\d+(?:-\d+)?|\@[\w\-]+)", line_stripped)
            if dport_match:
                dport = dport_match.group(1)

            # Extract interfaces
            iif = None
            iif_match = re.search(r"iif\s+([\w\-]+|\@[\w\-]+)", line_stripped)
            if iif_match:
                iif = iif_match.group(1)

            oif = None
            oif_match = re.search(r"oif\s+([\w\-]+|\@[\w\-]+)", line_stripped)
            if oif_match:
                oif = oif_match.group(1)

            return Rule(
                action=action,
                chain=chain,
                table=table,
                family=family,
                source=source,
                destination=destination,
                sport=sport,
                dport=dport,
                protocol=protocol,
                line_number=line_number,
                raw=line.strip(),
                iif=iif,
                oif=oif,
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
