"use client";

import { useCallback, useEffect, useMemo } from "react";
import {
  ReactFlow,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import NetworkNode from "./nodes/NetworkNode";
import RuleNode from "./nodes/RuleNode";
import PortNode from "./nodes/PortNode";

interface RuleGraphProps {
  graphData: {
    nodes: Array<{
      id: string;
      type: string;
      data: { label: string; [key: string]: unknown };
      position: { x: number; y: number };
    }>;
    edges: Array<{
      id: string;
      source: string;
      target: string;
      label?: string;
    }>;
  };
  highlightedNodes: string[];
}

const nodeTypes = {
  network: NetworkNode,
  rule: RuleNode,
  port: PortNode,
};

export default function RuleGraph({ graphData, highlightedNodes }: RuleGraphProps) {
  const [nodes, setNodes, onNodesChange] = useNodesState([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState([]);

  useEffect(() => {
    const flowNodes: Node[] = graphData.nodes.map((node) => ({
      id: node.id,
      type: node.type,
      data: node.data,
      position: node.position,
      className: highlightedNodes.includes(node.id) ? "highlighted" : "",
    }));

    const flowEdges: Edge[] = graphData.edges.map((edge) => ({
      id: edge.id,
      source: edge.source,
      target: edge.target,
      label: edge.label,
      className: highlightedNodes.some(
        (nodeId) => nodeId === edge.source || nodeId === edge.target
      )
        ? "highlighted"
        : "",
    }));

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [graphData, highlightedNodes, setNodes, setEdges]);

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden" style={{ height: "600px" }}>
      <ReactFlow
        nodes={nodes}
        edges={edges}
        onNodesChange={onNodesChange}
        onEdgesChange={onEdgesChange}
        nodeTypes={nodeTypes}
        proOptions={proOptions}
        fitView
        className="bg-gray-900"
      >
        <Background color="#374151" gap={16} />
        <Controls className="bg-gray-700" />
        <MiniMap className="bg-gray-700" nodeColor="#6b7280" />
      </ReactFlow>
    </div>
  );
}
