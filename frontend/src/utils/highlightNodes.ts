/**
 * Utility functions for consistent node highlighting across Tree and Graph views
 */

export type HighlightType = "search" | "query" | "selected" | "none";

export interface HighlightStyle {
  className: string;
  borderColor: string;
  backgroundColor: string;
}

// Color scheme based on action type for query matches
const actionColors: Record<string, { border: string; bg: string }> = {
  accept: { border: "border-green-500", bg: "bg-green-900/30" },
  drop: { border: "border-red-500", bg: "bg-red-900/30" },
  reject: { border: "border-orange-500", bg: "bg-orange-900/30" },
  default: { border: "border-blue-500", bg: "bg-blue-900/30" },
};

/**
 * Determine the highlight type for a node
 */
export function getNodeHighlightType(
  nodeId: string,
  selectedNodeId: string | null,
  searchMatchedIds: Set<string>,
  queryMatchedIds: Set<string>
): HighlightType {
  if (selectedNodeId === nodeId) return "selected";
  if (queryMatchedIds.has(nodeId)) return "query";
  if (searchMatchedIds.has(nodeId)) return "search";
  return "none";
}

/**
 * Get CSS classes for tree node highlighting
 */
export function getTreeNodeHighlightClasses(
  highlightType: HighlightType,
  action?: string
): string {
  switch (highlightType) {
    case "selected":
      return "bg-blue-900/50 border-l-4 border-blue-500";
    case "query": {
      const colors = action ? actionColors[action] || actionColors.default : actionColors.default;
      return `${colors.bg} border-l-4 ${colors.border}`;
    }
    case "search":
      return "bg-yellow-900/30 border-l-4 border-yellow-500";
    case "none":
    default:
      return "hover:bg-gray-700/50";
  }
}

/**
 * Get CSS classes for graph node highlighting
 */
export function getGraphNodeHighlightClasses(
  highlightType: HighlightType,
  action?: string
): string {
  switch (highlightType) {
    case "selected":
      return "ring-2 ring-blue-500 ring-offset-2 ring-offset-gray-900";
    case "query": {
      const ringColor = action === "accept" ? "ring-green-500" : action === "drop" ? "ring-red-500" : "ring-blue-500";
      return `ring-2 ${ringColor} ring-offset-2 ring-offset-gray-900 animate-pulse`;
    }
    case "search":
      return "ring-2 ring-yellow-500 ring-offset-2 ring-offset-gray-900";
    case "none":
    default:
      return "";
  }
}

/**
 * Get edge highlight classes based on connected nodes
 */
export function getEdgeHighlightClasses(
  sourceId: string,
  targetId: string,
  queryMatchedIds: Set<string>
): string {
  const sourceMatched = queryMatchedIds.has(sourceId);
  const targetMatched = queryMatchedIds.has(targetId);

  if (sourceMatched && targetMatched) {
    return "stroke-green-500 stroke-[3px] animated";
  }
  if (sourceMatched || targetMatched) {
    return "stroke-yellow-500 stroke-[2px]";
  }
  return "";
}

/**
 * Check if a node should be visually emphasized
 */
export function shouldEmphasizeNode(
  nodeId: string,
  searchMatchedIds: Set<string>,
  queryMatchedIds: Set<string>
): boolean {
  return searchMatchedIds.has(nodeId) || queryMatchedIds.has(nodeId);
}

/**
 * Get badge color for action type
 */
export function getActionBadgeColor(action: string): string {
  switch (action) {
    case "accept":
      return "bg-green-600 text-white";
    case "drop":
      return "bg-red-600 text-white";
    case "reject":
      return "bg-orange-600 text-white";
    case "jump":
      return "bg-blue-600 text-white";
    case "return":
      return "bg-purple-600 text-white";
    case "counter":
      return "bg-slate-600 text-white";
    case "log":
      return "bg-yellow-600 text-black";
    default:
      return "bg-gray-600 text-white";
  }
}

/**
 * Calculate parent node IDs that need to be expanded to show a match
 */
export function getParentChain(
  nodeId: string,
  nodeMap: Map<string, { parent_id: string | null }>
): string[] {
  const parents: string[] = [];
  let currentId: string | null = nodeId;

  while (currentId) {
    const node = nodeMap.get(currentId);
    if (!node || !node.parent_id) break;
    parents.push(node.parent_id);
    currentId = node.parent_id;
  }

  return parents;
}
