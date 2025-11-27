"use client";

import { useCallback, useMemo, useEffect, useRef } from "react";
import { useVirtualizer } from "@tanstack/react-virtual";
import { useUIStore } from "@/store/uiStore";
import { useNodeFiltering } from "@/hooks/useNodeFiltering";
import { getNodeHighlightType, getTreeNodeHighlightClasses } from "@/utils/highlightNodes";
import type { TreeNodeData } from "@/lib/types";
import TreeNode from "./TreeNode";

interface TreeViewProps {
  nodes: TreeNodeData[];
  onNodeSelect?: (nodeId: string) => void;
  containerRef: React.RefObject<HTMLDivElement>;
}

export default function TreeView({ nodes, onNodeSelect, containerRef }: TreeViewProps) {
  const {
    expandedNodes,
    selectedNodeId,
    filters,
    searchMode,
    matchedNodeIds,
    queryMatchedIds,
    activeMatchIndex,
    toggleExpand,
    selectNode,
    setExpanded,
  } = useUIStore();

  const scrollRef = useRef<HTMLDivElement>(null);

  // Use the filtering hook
  const { filteredNodes, matchedIds, matchCount, matchesSearch, hasMatchingDescendant } =
    useNodeFiltering(nodes, filters, searchMode);

  // Build parent-children relationships
  const childrenMap = useMemo(() => {
    const map = new Map<string | null, TreeNodeData[]>();
    nodes.forEach((node) => {
      const parentId = node.parent_id;
      if (!map.has(parentId)) {
        map.set(parentId, []);
      }
      map.get(parentId)!.push(node);
    });
    return map;
  }, [nodes]);

  // Build node map for parent lookups
  const nodeMap = useMemo(() => {
    const map = new Map<string, TreeNodeData>();
    nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [nodes]);

  // Build flat list of visible nodes (respecting expand state)
  const visibleNodes = useMemo(() => {
    const result: TreeNodeData[] = [];
    const nodesToProcess = searchMode === "filter" && filters.searchQuery ? filteredNodes : nodes;

    const addNode = (node: TreeNodeData) => {
      // In filter mode with search, show nodes that match or have matching descendants
      if (searchMode === "filter" && filters.searchQuery) {
        const nodeMatches = matchesSearch(node);
        const hasMatchingChild = hasMatchingDescendant(node);
        if (!nodeMatches && !hasMatchingChild) return;
      }

      // Apply quick filters
      if (filters.actionFilter && node.type === "rule") {
        if (node.metadata.action !== filters.actionFilter) return;
      }
      if (filters.protocolFilter && node.type === "rule") {
        if (node.metadata.protocol !== filters.protocolFilter) return;
      }

      result.push(node);

      // Add children if expanded (or if it's a root node)
      const isExpanded = expandedNodes.has(node.id) || node.depth === 0;
      if (isExpanded) {
        const children = childrenMap.get(node.id) || [];
        children.forEach(addNode);
      }
    };

    // Start with root nodes
    const rootNodes = childrenMap.get(null) || [];
    rootNodes.forEach(addNode);

    return result;
  }, [
    nodes,
    filteredNodes,
    expandedNodes,
    filters,
    searchMode,
    matchesSearch,
    hasMatchingDescendant,
    childrenMap,
  ]);

  // Virtual list
  const virtualizer = useVirtualizer({
    count: visibleNodes.length,
    getScrollElement: () => containerRef.current,
    estimateSize: () => 36,
    overscan: 10,
  });

  // Auto-scroll to active match when navigating
  useEffect(() => {
    if (matchCount === 0) return;

    const matchedArray = Array.from(matchedNodeIds);
    const currentMatchId = matchedArray[activeMatchIndex];
    if (!currentMatchId) return;

    // Find index in visible nodes
    const nodeIndex = visibleNodes.findIndex((n) => n.id === currentMatchId);
    if (nodeIndex >= 0) {
      virtualizer.scrollToIndex(nodeIndex, { align: "center", behavior: "smooth" });
    } else {
      // Node not visible - expand parent nodes
      const targetNode = nodeMap.get(currentMatchId);
      if (targetNode) {
        const parentsToExpand = getParentChain(targetNode, nodeMap);
        const newExpanded = new Set([...expandedNodes, ...parentsToExpand]);
        setExpanded(Array.from(newExpanded));
      }
    }
  }, [activeMatchIndex, matchedNodeIds, matchCount, visibleNodes, virtualizer, nodeMap, expandedNodes, setExpanded]);

  // Auto-scroll to query matched nodes
  useEffect(() => {
    if (queryMatchedIds.size === 0) return;

    const firstMatch = Array.from(queryMatchedIds)[0];
    const nodeIndex = visibleNodes.findIndex((n) => n.id === firstMatch);

    if (nodeIndex >= 0) {
      virtualizer.scrollToIndex(nodeIndex, { align: "center", behavior: "smooth" });
    } else {
      // Expand parents to show matched node
      const targetNode = nodeMap.get(firstMatch);
      if (targetNode) {
        const parentsToExpand = getParentChain(targetNode, nodeMap);
        const newExpanded = new Set([...expandedNodes, ...parentsToExpand]);
        setExpanded(Array.from(newExpanded));
      }
    }
  }, [queryMatchedIds, visibleNodes, virtualizer, nodeMap, expandedNodes, setExpanded]);

  const handleNodeClick = useCallback(
    (nodeId: string) => {
      selectNode(nodeId);
      onNodeSelect?.(nodeId);
    },
    [selectNode, onNodeSelect]
  );

  const handleNodeToggle = useCallback(
    (nodeId: string) => {
      toggleExpand(nodeId);
    },
    [toggleExpand]
  );

  return (
    <div
      ref={scrollRef}
      style={{
        height: `${virtualizer.getTotalSize()}px`,
        width: "100%",
        position: "relative",
      }}
    >
      {virtualizer.getVirtualItems().map((virtualRow) => {
        const node = visibleNodes[virtualRow.index];
        const isExpanded = expandedNodes.has(node.id);
        const hasChildren = (childrenMap.get(node.id)?.length || 0) > 0;

        // Determine highlight type using utility
        const highlightType = getNodeHighlightType(
          node.id,
          selectedNodeId,
          matchedNodeIds,
          queryMatchedIds
        );

        const isSearchMatch = matchedNodeIds.has(node.id);
        const isQueryMatch = queryMatchedIds.has(node.id);
        const action = node.metadata.action as string | undefined;

        return (
          <div
            key={node.id}
            data-node-id={node.id}
            style={{
              position: "absolute",
              top: 0,
              left: 0,
              width: "100%",
              height: `${virtualRow.size}px`,
              transform: `translateY(${virtualRow.start}px)`,
            }}
          >
            <TreeNode
              node={node}
              isExpanded={isExpanded}
              hasChildren={hasChildren}
              isSelected={selectedNodeId === node.id}
              isMatch={isSearchMatch}
              isQueryMatch={isQueryMatch}
              highlightClasses={getTreeNodeHighlightClasses(highlightType, action)}
              onToggle={() => handleNodeToggle(node.id)}
              onClick={() => handleNodeClick(node.id)}
            />
          </div>
        );
      })}
    </div>
  );
}

// Helper to get parent chain for a node
function getParentChain(
  node: TreeNodeData,
  nodeMap: Map<string, TreeNodeData>
): string[] {
  const parents: string[] = [];
  let currentId = node.parent_id;

  while (currentId) {
    parents.push(currentId);
    const parentNode = nodeMap.get(currentId);
    currentId = parentNode?.parent_id ?? null;
  }

  return parents;
}
