"use client";

import { useCallback, useEffect, useMemo } from "react";
import {
  ReactFlow,
  ReactFlowProvider,
  Background,
  Controls,
  MiniMap,
  useNodesState,
  useEdgesState,
  useReactFlow,
  type Node,
  type Edge,
} from "@xyflow/react";
import "@xyflow/react/dist/style.css";
import { useUIStore } from "@/store/uiStore";
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
  highlightedNodes?: string[];
}

const nodeTypes = {
  network: NetworkNode,
  rule: RuleNode,
  port: PortNode,
};

function RuleGraphInner({ graphData, highlightedNodes = [] }: RuleGraphProps) {
  const { queryMatchedIds, matchedNodeIds, selectedNodeId, selectNode } = useUIStore();
  const { fitView } = useReactFlow();

  const [nodes, setNodes, onNodesChange] = useNodesState<Node>([]);
  const [edges, setEdges, onEdgesChange] = useEdgesState<Edge>([]);

  // Combine all highlighted nodes
  const allHighlightedIds = useMemo(() => {
    const combined = new Set<string>([
      ...highlightedNodes,
      ...queryMatchedIds,
      ...matchedNodeIds,
    ]);
    return combined;
  }, [highlightedNodes, queryMatchedIds, matchedNodeIds]);

  // Update nodes and edges when data or highlights change
  useEffect(() => {
    const flowNodes: Node[] = graphData.nodes.map((node) => {
      const isQueryMatch = queryMatchedIds.has(node.id);
      const isSearchMatch = matchedNodeIds.has(node.id);
      const isSelected = selectedNodeId === node.id;
      const isHighlighted = allHighlightedIds.has(node.id);

      // Determine highlight class based on priority
      let className = "";
      if (isSelected) {
        className = "selected-node ring-2 ring-blue-500";
      } else if (isQueryMatch) {
        const action = node.data.action as string | undefined;
        if (action === "accept") {
          className = "query-match-accept ring-2 ring-green-500 animate-pulse";
        } else if (action === "drop") {
          className = "query-match-drop ring-2 ring-red-500 animate-pulse";
        } else {
          className = "query-match ring-2 ring-blue-500 animate-pulse";
        }
      } else if (isSearchMatch) {
        className = "search-match ring-2 ring-yellow-500";
      } else if (isHighlighted) {
        className = "highlighted";
      }

      return {
        id: node.id,
        type: node.type,
        data: {
          ...node.data,
          isQueryMatch,
          isSearchMatch,
          isSelected,
        },
        position: node.position,
        className,
      };
    });

    const flowEdges: Edge[] = graphData.edges.map((edge) => {
      const sourceMatch = queryMatchedIds.has(edge.source);
      const targetMatch = queryMatchedIds.has(edge.target);
      const isHighlightedEdge = sourceMatch || targetMatch;

      return {
        id: edge.id,
        source: edge.source,
        target: edge.target,
        label: edge.label,
        animated: sourceMatch && targetMatch,
        className: isHighlightedEdge ? "highlighted-edge" : "",
        style: isHighlightedEdge
          ? {
              stroke: sourceMatch && targetMatch ? "#22c55e" : "#eab308",
              strokeWidth: sourceMatch && targetMatch ? 3 : 2,
            }
          : undefined,
      };
    });

    setNodes(flowNodes);
    setEdges(flowEdges);
  }, [graphData, queryMatchedIds, matchedNodeIds, selectedNodeId, allHighlightedIds, setNodes, setEdges]);

  // Fit view to matched nodes when query results change
  useEffect(() => {
    if (queryMatchedIds.size > 0) {
      const matchedNodeIdArray = Array.from(queryMatchedIds);
      // Delay fitView to ensure nodes are rendered
      setTimeout(() => {
        fitView({
          nodes: matchedNodeIdArray.map((id) => ({ id })),
          duration: 800,
          padding: 0.2,
        });
      }, 100);
    }
  }, [queryMatchedIds, fitView]);

  const handleNodeClick = useCallback(
    (_: React.MouseEvent, node: Node) => {
      selectNode(node.id);
    },
    [selectNode]
  );

  const proOptions = useMemo(() => ({ hideAttribution: true }), []);

  return (
    <ReactFlow
      nodes={nodes}
      edges={edges}
      onNodesChange={onNodesChange}
      onEdgesChange={onEdgesChange}
      onNodeClick={handleNodeClick}
      nodeTypes={nodeTypes}
      proOptions={proOptions}
      fitView
      className="bg-gray-900"
    >
      <Background color="#374151" gap={16} />
      <Controls className="bg-gray-700" />
      <MiniMap
        className="bg-gray-700"
        nodeColor={(node) => {
          if (queryMatchedIds.has(node.id)) {
            const action = (node.data as { action?: string }).action;
            return action === "accept" ? "#22c55e" : action === "drop" ? "#ef4444" : "#3b82f6";
          }
          if (matchedNodeIds.has(node.id)) return "#eab308";
          return "#6b7280";
        }}
      />
    </ReactFlow>
  );
}

export default function RuleGraph(props: RuleGraphProps) {
  return (
    <div className="bg-gray-800 rounded-lg overflow-hidden" style={{ height: "600px" }}>
      <ReactFlowProvider>
        <RuleGraphInner {...props} />
      </ReactFlowProvider>
    </div>
  );
}
