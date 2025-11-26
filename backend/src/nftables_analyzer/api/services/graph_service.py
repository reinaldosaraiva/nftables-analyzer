"""Service to convert rules to React Flow graph format."""

from nftables_analyzer.api.schemas import GraphData, GraphEdge, GraphNode
from nftables_analyzer.models import Rule


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
