"""Evaluates queries against nftables rules."""

from nftables_analyzer.evaluator.ip_matcher import IPMatcher
from nftables_analyzer.models import EvaluationResult, Query, Rule


class RuleEvaluator:
    """Evaluates packet queries against firewall rules."""

    def __init__(self, rules: list[Rule]) -> None:
        """Initialize with a list of rules."""
        self.rules = rules

    def evaluate(self, query: Query) -> EvaluationResult:
        """Evaluate a query against all rules."""
        result = EvaluationResult(
            verdict="NO_MATCH",
            explanation="No matching rules found",
        )

        result.add_trace(f"Evaluating query: {query}")
        result.add_trace(f"Total rules to check: {len(self.rules)}")

        # Filter rules by direction (chain)
        chain_name = self._get_chain_for_direction(query.direction)
        relevant_rules = [r for r in self.rules if r.chain.lower() == chain_name]

        result.add_trace(f"Relevant rules for chain '{chain_name}': {len(relevant_rules)}")

        matched_rules: list[Rule] = []
        last_action = None

        for rule in relevant_rules:
            if self._rule_matches_query(rule, query):
                matched_rules.append(rule)
                result.add_trace(
                    f"Rule {rule.line_number} matches: {rule.action} "
                    f"(src={rule.source}, dst={rule.destination}, "
                    f"sport={rule.sport}, dport={rule.dport})"
                )
                last_action = rule.action

                # First match wins in nftables (unless jump/return)
                if last_action not in ["jump", "return"]:
                    break

        # Determine verdict
        if matched_rules:
            result.matched_rules = matched_rules

            if len(matched_rules) > 1:
                # Check for conflicts
                self._detect_conflicts(matched_rules, result)

            if last_action in ["accept"]:
                result.verdict = "ALLOW"
                result.explanation = f"Traffic allowed by rule {matched_rules[-1].line_number}"
            elif last_action in ["drop", "reject"]:
                result.verdict = "BLOCK"
                result.explanation = f"Traffic blocked by rule {matched_rules[-1].line_number}"
            else:
                result.verdict = "NO_MATCH"
                result.explanation = "Matched jump/return rules only"
        else:
            result.verdict = "NO_MATCH"
            result.explanation = f"No rules matched for chain '{chain_name}'"
            result.add_trace("Default policy would apply (usually ACCEPT)")

        return result

    def _rule_matches_query(self, rule: Rule, query: Query) -> bool:
        """Check if a rule matches the query."""
        # Match source IP and port
        src_ip_match = IPMatcher.ip_matches(query.src_ip, rule.source)
        src_port_match = IPMatcher.port_matches(query.src_port, rule.sport)

        # Match destination IP and port
        dst_ip_match = IPMatcher.ip_matches(query.dst_ip, rule.destination)
        dst_port_match = IPMatcher.port_matches(query.dst_port, rule.dport)

        # Match protocol
        proto_match = IPMatcher.protocol_matches(query.protocol, rule.protocol)

        return (
            src_ip_match
            and src_port_match
            and dst_ip_match
            and dst_port_match
            and proto_match
        )

    def _get_chain_for_direction(self, direction: str) -> str:
        """Map direction to chain name."""
        mapping = {
            "in": "input",
            "out": "output",
            "forward": "forward",
        }
        return mapping.get(direction, "input")

    def _detect_conflicts(
        self, matched_rules: list[Rule], result: EvaluationResult
    ) -> None:
        """Detect conflicts between matched rules."""
        for i in range(len(matched_rules) - 1):
            rule1 = matched_rules[i]
            rule2 = matched_rules[i + 1]

            if rule1.action != rule2.action:
                reason = (
                    f"Rule {rule1.line_number} ({rule1.action}) conflicts with "
                    f"rule {rule2.line_number} ({rule2.action})"
                )
                result.add_conflict(rule1, rule2, reason)
                result.verdict = "CONFLICT"
                result.explanation = f"Conflicting actions: {rule1.action} vs {rule2.action}"

    def find_redundant_rules(self) -> list[tuple[Rule, Rule]]:
        """Find redundant rules (one rule makes another unreachable)."""
        redundant: list[tuple[Rule, Rule]] = []

        for i, rule1 in enumerate(self.rules):
            for rule2 in self.rules[i + 1 :]:
                # Same chain only
                if rule1.chain != rule2.chain:
                    continue

                # If rule1 is more general than rule2
                if self._rule_shadows(rule1, rule2):
                    redundant.append((rule1, rule2))

        return redundant

    def _rule_shadows(self, general: Rule, specific: Rule) -> bool:
        """Check if general rule shadows specific rule."""
        # Same action required to be considered shadowing
        if general.action != specific.action:
            return False

        # Check if general rule matches all traffic that specific rule matches
        if general.source is None or (
            specific.source and self._ip_contains(general.source, specific.source)
        ):
            if general.destination is None or (
                specific.destination
                and self._ip_contains(general.destination, specific.destination)
            ):
                if general.sport is None or general.sport == specific.sport:
                    if general.dport is None or general.dport == specific.dport:
                        if general.protocol is None or general.protocol == specific.protocol:
                            return True
        return False

    def _ip_contains(self, general: str, specific: str) -> bool:
        """Check if general CIDR contains specific IP/CIDR."""
        try:
            import ipaddress

            if "/" in general:
                general_net = ipaddress.ip_network(general, strict=False)
                if "/" in specific:
                    specific_net = ipaddress.ip_network(specific, strict=False)
                    return specific_net.subnet_of(general_net)
                else:
                    specific_addr = ipaddress.ip_address(specific)
                    return specific_addr in general_net
            else:
                return general == specific
        except ValueError:
            return False
