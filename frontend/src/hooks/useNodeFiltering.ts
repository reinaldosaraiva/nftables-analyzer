"use client";

import { useMemo, useCallback, useEffect } from "react";
import { useUIStore, type FilterState, type SearchMode } from "@/store/uiStore";
import type { TreeNodeData } from "@/lib/types";

interface UseNodeFilteringResult {
  filteredNodes: TreeNodeData[];
  matchedIds: string[];
  matchCount: number;
  hasMatchingDescendant: (node: TreeNodeData) => boolean;
  matchesSearch: (node: TreeNodeData) => boolean;
  getMatchAtIndex: (index: number) => string | null;
}

export function useNodeFiltering(
  nodes: TreeNodeData[],
  filters: FilterState,
  searchMode: SearchMode
): UseNodeFilteringResult {
  const { setMatchedNodeIds } = useUIStore();

  // Build node map for O(1) lookups
  const nodeMap = useMemo(() => {
    const map = new Map<string, TreeNodeData>();
    nodes.forEach((node) => map.set(node.id, node));
    return map;
  }, [nodes]);

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

  // Check if node matches search query
  const matchesSearch = useCallback(
    (node: TreeNodeData): boolean => {
      const searchLower = filters.searchQuery.toLowerCase().trim();
      if (!searchLower) return false;

      // Check label
      if (node.label.toLowerCase().includes(searchLower)) return true;

      // Check metadata fields
      const metadata = node.metadata;
      const fieldsToCheck = [
        "action",
        "protocol",
        "source",
        "destination",
        "dport",
        "sport",
        "iif",
        "oif",
        "raw",
      ];

      for (const field of fieldsToCheck) {
        if (metadata[field] && String(metadata[field]).toLowerCase().includes(searchLower)) {
          return true;
        }
      }

      // Check sets referenced
      if (Array.isArray(metadata.sets_referenced)) {
        for (const setName of metadata.sets_referenced) {
          if (String(setName).toLowerCase().includes(searchLower)) {
            return true;
          }
        }
      }

      return false;
    },
    [filters.searchQuery]
  );

  // Check if node matches all active filters
  const matchesFilters = useCallback(
    (node: TreeNodeData): boolean => {
      // Action filter (only applies to rules)
      if (filters.actionFilter && node.type === "rule") {
        if (node.metadata.action !== filters.actionFilter) return false;
      }

      // Protocol filter (only applies to rules)
      if (filters.protocolFilter && node.type === "rule") {
        if (node.metadata.protocol !== filters.protocolFilter) return false;
      }

      // Table filter
      if (filters.tableFilter) {
        if (node.type === "table" && node.label !== filters.tableFilter) return false;
        // For non-table nodes, check if they belong to the filtered table
        if (node.type !== "table" && !node.id.includes(filters.tableFilter)) return false;
      }

      // Chain filter
      if (filters.chainFilter) {
        if (node.type === "chain" && node.label !== filters.chainFilter) return false;
        if (node.type === "rule" && !node.id.includes(filters.chainFilter)) return false;
      }

      return true;
    },
    [filters.actionFilter, filters.protocolFilter, filters.tableFilter, filters.chainFilter]
  );

  // Check if node has any matching descendants
  const hasMatchingDescendant = useCallback(
    (node: TreeNodeData): boolean => {
      if (matchesSearch(node) && matchesFilters(node)) return true;

      const children = childrenMap.get(node.id) || [];
      return children.some((child) => hasMatchingDescendant(child));
    },
    [childrenMap, matchesSearch, matchesFilters]
  );

  // Compute matched node IDs
  const matchedIds = useMemo(() => {
    if (!filters.searchQuery.trim()) return [];

    const matched: string[] = [];
    nodes.forEach((node) => {
      if (matchesSearch(node) && matchesFilters(node)) {
        matched.push(node.id);
      }
    });

    return matched;
  }, [nodes, filters.searchQuery, matchesSearch, matchesFilters]);

  // Compute filtered nodes based on search mode
  const filteredNodes = useMemo(() => {
    const result: TreeNodeData[] = [];

    // If no search and no filters, return all nodes
    if (!filters.searchQuery.trim() && !hasActiveFilters(filters)) {
      return nodes;
    }

    // In highlight mode, show all nodes but mark matches
    if (searchMode === "highlight" && !hasActiveFilters(filters)) {
      return nodes;
    }

    // In filter mode or with active filters, filter the tree
    const addNode = (node: TreeNodeData, parentVisible: boolean = true) => {
      const nodeMatchesFilters = matchesFilters(node);
      const nodeMatchesSearch = filters.searchQuery.trim()
        ? matchesSearch(node) || hasMatchingDescendant(node)
        : true;

      const shouldShow = nodeMatchesFilters && (parentVisible || nodeMatchesSearch);

      if (shouldShow) {
        result.push(node);
      }

      // Always process children to find matches
      const children = childrenMap.get(node.id) || [];
      children.forEach((child) => addNode(child, shouldShow));
    };

    // Start with root nodes
    const rootNodes = childrenMap.get(null) || [];
    rootNodes.forEach((node) => addNode(node, true));

    return result;
  }, [nodes, filters, searchMode, matchesFilters, matchesSearch, hasMatchingDescendant, childrenMap]);

  // Update store with matched IDs
  useEffect(() => {
    setMatchedNodeIds(matchedIds);
  }, [matchedIds, setMatchedNodeIds]);

  // Get match at specific index for navigation
  const getMatchAtIndex = useCallback(
    (index: number): string | null => {
      if (index < 0 || index >= matchedIds.length) return null;
      return matchedIds[index];
    },
    [matchedIds]
  );

  return {
    filteredNodes,
    matchedIds,
    matchCount: matchedIds.length,
    hasMatchingDescendant,
    matchesSearch,
    getMatchAtIndex,
  };
}

// Helper to check if any filters are active
function hasActiveFilters(filters: FilterState): boolean {
  return !!(
    filters.actionFilter ||
    filters.protocolFilter ||
    filters.tableFilter ||
    filters.chainFilter
  );
}

// Hook to get current match for navigation
export function useMatchNavigation() {
  const { matchedNodeIds, activeMatchIndex, nextMatch, prevMatch, selectNode, setExpanded, expandedNodes } =
    useUIStore();

  const matchedArray = useMemo(() => Array.from(matchedNodeIds), [matchedNodeIds]);

  const currentMatchId = matchedArray[activeMatchIndex] || null;

  const goToNextMatch = useCallback(() => {
    nextMatch();
    const nextId = matchedArray[(activeMatchIndex + 1) % matchedArray.length];
    if (nextId) {
      selectNode(nextId);
      // Scroll into view would be handled by the component
    }
  }, [nextMatch, matchedArray, activeMatchIndex, selectNode]);

  const goToPrevMatch = useCallback(() => {
    prevMatch();
    const prevIdx = activeMatchIndex === 0 ? matchedArray.length - 1 : activeMatchIndex - 1;
    const prevId = matchedArray[prevIdx];
    if (prevId) {
      selectNode(prevId);
    }
  }, [prevMatch, matchedArray, activeMatchIndex, selectNode]);

  const focusMatch = useCallback(
    (nodeId: string, parentIds: string[]) => {
      // Expand all parent nodes to make the match visible
      const newExpanded = new Set([...expandedNodes, ...parentIds]);
      setExpanded(Array.from(newExpanded));
      selectNode(nodeId);
    },
    [expandedNodes, setExpanded, selectNode]
  );

  return {
    currentMatchId,
    matchCount: matchedArray.length,
    activeMatchIndex,
    goToNextMatch,
    goToPrevMatch,
    focusMatch,
  };
}
