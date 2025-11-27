"""Service to convert rules to React Flow graph format."""

from collections import Counter

from nftables_analyzer.api.schemas import (
    ChainSummary,
    GraphData,
    GraphEdge,
    GraphNode,
    HierarchicalParseResponse,
    RuleStats,
    TableSummary,
    TreeNodeData,
)
from nftables_analyzer.models import Rule, SetDefinition, Table
from nftables_analyzer.parser.rule_parser import ParseResult


class GraphService:
    """Converts firewall rules to graph visualization data."""

    @staticmethod
    def rules_to_graph(
        rules: list[Rule], matched_rules: list[Rule] | None = None
    ) -> GraphData:
        """Convert rules to React Flow graph format."""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        node_id_map: dict[str, str] = {}
        matched_ids = {r.line_number for r in matched_rules} if matched_rules else set()

        y_offset = 0
        vertical_spacing = 120

        for rule in rules:
            rule_id = f"rule-{rule.line_number}"
            is_matched = rule.line_number in matched_ids

            # Create rule node
            rule_style = {}
            if is_matched:
                rule_style = {
                    "background": "#fef3c7" if rule.action == "accept" else "#fecaca",
                    "border": "2px solid #f59e0b" if rule.action == "accept" else "#ef4444",
                }

            nodes.append(
                GraphNode(
                    id=rule_id,
                    type="rule",
                    data={
                        "label": f"Rule {rule.line_number}",
                        "action": rule.action,
                        "chain": rule.chain,
                        "matched": is_matched,
                    },
                    position={"x": 300, "y": y_offset},
                    style=rule_style if is_matched else None,
                )
            )

            # Source network node
            if rule.source:
                src_id = f"src-{rule.source}".replace("/", "-")
                if src_id not in node_id_map:
                    node_id_map[src_id] = src_id
                    nodes.append(
                        GraphNode(
                            id=src_id,
                            type="network",
                            data={"label": rule.source, "type": "source"},
                            position={"x": 0, "y": y_offset},
                        )
                    )
                edges.append(
                    GraphEdge(
                        id=f"e-{src_id}-{rule_id}",
                        source=src_id,
                        target=rule_id,
                        animated=is_matched,
                    )
                )

            # Destination network node
            if rule.destination:
                dst_id = f"dst-{rule.destination}".replace("/", "-")
                if dst_id not in node_id_map:
                    node_id_map[dst_id] = dst_id
                    nodes.append(
                        GraphNode(
                            id=dst_id,
                            type="network",
                            data={"label": rule.destination, "type": "destination"},
                            position={"x": 600, "y": y_offset},
                        )
                    )
                edges.append(
                    GraphEdge(
                        id=f"e-{rule_id}-{dst_id}",
                        source=rule_id,
                        target=dst_id,
                        animated=is_matched,
                        style=(
                            {"stroke": "#10b981"}
                            if rule.action == "accept"
                            else {"stroke": "#ef4444"}
                        ),
                    )
                )

            # Port node
            if rule.dport:
                port_id = f"port-{rule.dport}"
                protocol_label = f"{rule.dport}/{rule.protocol or 'tcp'}"

                if port_id not in node_id_map:
                    node_id_map[port_id] = port_id
                    nodes.append(
                        GraphNode(
                            id=port_id,
                            type="port",
                            data={"label": protocol_label, "port": rule.dport},
                            position={"x": 450, "y": y_offset + 60},
                        )
                    )
                edges.append(
                    GraphEdge(
                        id=f"e-{rule_id}-{port_id}",
                        source=rule_id,
                        target=port_id,
                        animated=is_matched,
                    )
                )

            y_offset += vertical_spacing

        return GraphData(nodes=nodes, edges=edges)

    @staticmethod
    def parse_result_to_hierarchical(
        parse_result: ParseResult,
        matched_rules: list[Rule] | None = None,
    ) -> HierarchicalParseResponse:
        """Convert ParseResult to HierarchicalParseResponse with tree nodes."""
        tables_list: list[TableSummary] = []
        tree_nodes: list[TreeNodeData] = []
        all_sets: list[SetDefinition] = []
        all_rules: list[Rule] = []

        # Stats counters
        action_counter: Counter = Counter()
        protocol_counter: Counter = Counter()
        table_rule_counter: Counter = Counter()

        # Layout constants
        table_y_offset = 0
        table_height_base = 100
        chain_height = 80
        rule_height = 60
        table_spacing = 50

        # Build hierarchy
        for table_key, table in parse_result.tables.items():
            table_id = f"table-{table.family}-{table.name}"

            # Build chain summaries
            chain_summaries: list[ChainSummary] = []
            table_total_rules = 0

            for chain_name, chain in table.chains.items():
                chain_summaries.append(
                    ChainSummary(
                        name=chain.name,
                        type=chain.type,
                        hook=chain.hook,
                        policy=chain.policy,
                        rule_count=chain.rule_count,
                        line_number=chain.line_number,
                    )
                )
                table_total_rules += chain.rule_count

                # Collect rules and stats
                for rule in chain.rules:
                    all_rules.append(rule)
                    action_counter[rule.action] += 1
                    if rule.protocol:
                        protocol_counter[rule.protocol] += 1
                    table_rule_counter[table.name] += 1

            # Add table summary
            tables_list.append(
                TableSummary(
                    name=table.name,
                    family=table.family,
                    chains=chain_summaries,
                    sets=list(table.sets.values()),
                    chain_count=table.chain_count,
                    set_count=table.set_count,
                    rule_count=table_total_rules,
                    line_number=table.line_number,
                )
            )

            # Collect sets
            all_sets.extend(table.sets.values())

            # Build tree nodes for this table
            tree_nodes.append(
                TreeNodeData(
                    id=table_id,
                    type="table",
                    label=f"{table.family} {table.name}",
                    depth=0,
                    parent_id=None,
                    children_count=table.chain_count + table.set_count,
                    metadata={
                        "family": table.family,
                        "chain_count": table.chain_count,
                        "set_count": table.set_count,
                        "rule_count": table_total_rules,
                    },
                )
            )

            # Add chain tree nodes
            for chain in table.chains.values():
                chain_id = f"chain-{table.family}-{table.name}-{chain.name}"
                tree_nodes.append(
                    TreeNodeData(
                        id=chain_id,
                        type="chain",
                        label=chain.name,
                        depth=1,
                        parent_id=table_id,
                        children_count=chain.rule_count,
                        metadata={
                            "type": chain.type,
                            "hook": chain.hook,
                            "policy": chain.policy,
                            "rule_count": chain.rule_count,
                        },
                    )
                )

                # Add rule tree nodes
                for rule in chain.rules:
                    rule_id = f"rule-{rule.line_number}"
                    rule_label = _build_rule_label(rule)
                    tree_nodes.append(
                        TreeNodeData(
                            id=rule_id,
                            type="rule",
                            label=rule_label,
                            depth=2,
                            parent_id=chain_id,
                            children_count=0,
                            metadata={
                                "action": rule.action,
                                "line_number": rule.line_number,
                                "protocol": rule.protocol,
                                "source": rule.source,
                                "destination": rule.destination,
                                "dport": rule.dport,
                                "sport": rule.sport,
                            },
                        )
                    )

            # Add set tree nodes
            for set_def in table.sets.values():
                set_id = f"set-{table.family}-{table.name}-{set_def.name}"
                tree_nodes.append(
                    TreeNodeData(
                        id=set_id,
                        type="set",
                        label=set_def.name,
                        depth=1,
                        parent_id=table_id,
                        children_count=len(set_def.elements),
                        metadata={
                            "type": set_def.type,
                            "flags": set_def.flags,
                            "element_count": len(set_def.elements),
                        },
                    )
                )

            table_y_offset += table_height_base + (table.chain_count * chain_height) + table_spacing

        # Sort rules by line number
        all_rules.sort(key=lambda r: r.line_number)

        # Build stats
        stats = RuleStats(
            total_rules=len(all_rules),
            total_tables=len(parse_result.tables),
            total_chains=sum(t.chain_count for t in tables_list),
            total_sets=len(all_sets),
            rules_by_action=dict(action_counter),
            rules_by_protocol=dict(protocol_counter),
            rules_by_table=dict(table_rule_counter),
        )

        # Generate hierarchical graph
        graph = GraphService._build_hierarchical_graph(parse_result, matched_rules)

        return HierarchicalParseResponse(
            tables=tables_list,
            sets=all_sets,
            rules=all_rules,
            tree_nodes=tree_nodes,
            graph=graph,
            stats=stats,
        )

    @staticmethod
    def _build_hierarchical_graph(
        parse_result: ParseResult,
        matched_rules: list[Rule] | None = None,
    ) -> GraphData:
        """Build React Flow graph with table/chain grouping."""
        nodes: list[GraphNode] = []
        edges: list[GraphEdge] = []
        matched_ids = {r.line_number for r in matched_rules} if matched_rules else set()

        # Layout constants
        table_x = 50
        table_y = 50
        table_width = 800
        chain_x_offset = 30
        chain_y_offset = 60
        rule_x_offset = 60
        rule_y_offset = 50
        rule_height = 40

        for table_key, table in parse_result.tables.items():
            table_id = f"table-{table.family}-{table.name}"

            # Calculate table height based on content
            total_rules = sum(c.rule_count for c in table.chains.values())
            table_height = max(200, chain_y_offset + (len(table.chains) * 100) + (total_rules * rule_height))

            # Table group node
            nodes.append(
                GraphNode(
                    id=table_id,
                    type="tableGroup",
                    data={
                        "label": f"{table.family} {table.name}",
                        "family": table.family,
                        "collapsed": False,
                        "chain_count": table.chain_count,
                        "set_count": table.set_count,
                        "rule_count": total_rules,
                    },
                    position={"x": table_x, "y": table_y},
                    style={
                        "width": table_width,
                        "height": table_height,
                        "backgroundColor": "rgba(30, 41, 59, 0.8)",
                        "borderRadius": 8,
                        "border": "1px solid #475569",
                    },
                )
            )

            chain_y = table_y + chain_y_offset
            for chain in table.chains.values():
                chain_id = f"chain-{table.family}-{table.name}-{chain.name}"
                chain_height = max(80, rule_y_offset + (chain.rule_count * rule_height))

                # Chain group node
                nodes.append(
                    GraphNode(
                        id=chain_id,
                        type="chainGroup",
                        data={
                            "label": chain.name,
                            "type": chain.type,
                            "hook": chain.hook,
                            "policy": chain.policy,
                            "collapsed": False,
                            "rule_count": chain.rule_count,
                        },
                        position={"x": table_x + chain_x_offset, "y": chain_y},
                        style={
                            "width": table_width - (chain_x_offset * 2),
                            "height": chain_height,
                            "backgroundColor": "rgba(51, 65, 85, 0.6)",
                            "borderRadius": 6,
                            "border": "1px solid #64748b",
                        },
                        parentId=table_id,
                    )
                )

                # Rule nodes inside chain
                rule_y = chain_y + rule_y_offset
                for rule in chain.rules:
                    rule_id = f"rule-{rule.line_number}"
                    is_matched = rule.line_number in matched_ids

                    rule_style: dict = {
                        "backgroundColor": _get_action_color(rule.action),
                        "borderRadius": 4,
                        "padding": 4,
                    }
                    if is_matched:
                        rule_style["border"] = "2px solid #f59e0b"
                        rule_style["boxShadow"] = "0 0 10px rgba(245, 158, 11, 0.5)"

                    nodes.append(
                        GraphNode(
                            id=rule_id,
                            type="rule",
                            data={
                                "label": _build_rule_label(rule),
                                "action": rule.action,
                                "chain": chain.name,
                                "table": table.name,
                                "matched": is_matched,
                                "line_number": rule.line_number,
                                "protocol": rule.protocol,
                                "source": rule.source,
                                "destination": rule.destination,
                                "dport": rule.dport,
                            },
                            position={"x": table_x + rule_x_offset, "y": rule_y},
                            style=rule_style,
                            parentId=chain_id,
                        )
                    )

                    rule_y += rule_height

                chain_y += chain_height + 20

            table_y += table_height + 50

        return GraphData(nodes=nodes, edges=edges)


def _build_rule_label(rule: Rule) -> str:
    """Build a concise label for a rule."""
    parts = []

    if rule.protocol:
        parts.append(rule.protocol.upper())

    if rule.source:
        parts.append(f"src:{rule.source[:15]}..." if len(rule.source) > 15 else f"src:{rule.source}")

    if rule.destination:
        parts.append(f"dst:{rule.destination[:15]}..." if len(rule.destination) > 15 else f"dst:{rule.destination}")

    if rule.dport:
        parts.append(f"dport:{rule.dport}")

    if rule.sport:
        parts.append(f"sport:{rule.sport}")

    parts.append(f"→ {rule.action}")

    if not parts[:-1]:  # Only action
        return f"L{rule.line_number}: {rule.action}"

    return f"L{rule.line_number}: {' '.join(parts)}"


def _get_action_color(action: str) -> str:
    """Get background color for action type."""
    colors = {
        "accept": "rgba(34, 197, 94, 0.3)",  # Green
        "drop": "rgba(239, 68, 68, 0.3)",  # Red
        "reject": "rgba(249, 115, 22, 0.3)",  # Orange
        "jump": "rgba(59, 130, 246, 0.3)",  # Blue
        "return": "rgba(168, 85, 247, 0.3)",  # Purple
        "counter": "rgba(100, 116, 139, 0.3)",  # Slate
        "log": "rgba(234, 179, 8, 0.3)",  # Yellow
    }
    return colors.get(action, "rgba(100, 116, 139, 0.3)")
