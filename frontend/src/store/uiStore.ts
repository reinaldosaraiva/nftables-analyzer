import { create } from "zustand";

export interface FilterState {
  searchQuery: string;
  actionFilter: string | null;
  protocolFilter: string | null;
  tableFilter: string | null;
  chainFilter: string | null;
  selectedSets: string[];
}

export type SearchMode = "highlight" | "filter";
export type ViewMode = "tree" | "graph" | "config";

interface UIState {
  // Expand/collapse state
  expandedNodes: Set<string>;

  // Selection
  selectedNodeId: string | null;

  // Filters
  filters: FilterState;

  // Breadcrumb navigation
  breadcrumb: string[];

  // Search modal
  isSearchOpen: boolean;

  // Search mode: highlight matches vs filter tree
  searchMode: SearchMode;

  // View mode: tree, graph, or config viewer
  viewMode: ViewMode;

  // Matched nodes from search (for highlighting)
  matchedNodeIds: Set<string>;

  // Matched rules from query (for highlighting across views)
  queryMatchedIds: Set<string>;

  // Current match index for Ctrl+G navigation
  activeMatchIndex: number;

  // Raw config content for viewer
  rawConfigContent: string;

  // Highlighted line in config viewer
  highlightedLine: number | null;

  // Actions
  toggleExpand: (nodeId: string) => void;
  expandAll: () => void;
  collapseAll: () => void;
  setExpanded: (nodeIds: string[]) => void;

  selectNode: (nodeId: string | null) => void;

  setFilter: (filter: Partial<FilterState>) => void;
  clearFilters: () => void;

  setBreadcrumb: (path: string[]) => void;

  setSearchOpen: (open: boolean) => void;

  // New actions
  setSearchMode: (mode: SearchMode) => void;
  setViewMode: (mode: ViewMode) => void;
  setMatchedNodeIds: (ids: string[]) => void;
  setQueryMatchedIds: (ids: string[]) => void;
  clearQueryMatches: () => void;
  nextMatch: () => void;
  prevMatch: () => void;
  setRawConfigContent: (content: string) => void;
  setHighlightedLine: (line: number | null) => void;
  syncViewWithQuery: (matchedRuleIds: string[]) => void;
}

const initialFilters: FilterState = {
  searchQuery: "",
  actionFilter: null,
  protocolFilter: null,
  tableFilter: null,
  chainFilter: null,
  selectedSets: [],
};

export const useUIStore = create<UIState>((set, get) => ({
  expandedNodes: new Set<string>(),
  selectedNodeId: null,
  filters: initialFilters,
  breadcrumb: [],
  isSearchOpen: false,
  searchMode: "highlight",
  viewMode: "tree",
  matchedNodeIds: new Set<string>(),
  queryMatchedIds: new Set<string>(),
  activeMatchIndex: 0,
  rawConfigContent: "",
  highlightedLine: null,

  toggleExpand: (nodeId) =>
    set((state) => {
      const newExpanded = new Set(state.expandedNodes);
      if (newExpanded.has(nodeId)) {
        newExpanded.delete(nodeId);
      } else {
        newExpanded.add(nodeId);
      }
      return { expandedNodes: newExpanded };
    }),

  expandAll: () =>
    set(() => ({
      expandedNodes: new Set<string>(),
    })),

  collapseAll: () =>
    set(() => ({
      expandedNodes: new Set<string>(),
    })),

  setExpanded: (nodeIds) =>
    set(() => ({
      expandedNodes: new Set(nodeIds),
    })),

  selectNode: (nodeId) =>
    set(() => ({
      selectedNodeId: nodeId,
    })),

  setFilter: (filter) =>
    set((state) => ({
      filters: { ...state.filters, ...filter },
    })),

  clearFilters: () =>
    set(() => ({
      filters: initialFilters,
    })),

  setBreadcrumb: (path) =>
    set(() => ({
      breadcrumb: path,
    })),

  setSearchOpen: (open) =>
    set(() => ({
      isSearchOpen: open,
    })),

  setSearchMode: (mode) =>
    set(() => ({
      searchMode: mode,
    })),

  setViewMode: (mode) =>
    set(() => ({
      viewMode: mode,
    })),

  setMatchedNodeIds: (ids) =>
    set(() => ({
      matchedNodeIds: new Set(ids),
      activeMatchIndex: 0,
    })),

  setQueryMatchedIds: (ids) =>
    set(() => ({
      queryMatchedIds: new Set(ids),
    })),

  clearQueryMatches: () =>
    set(() => ({
      queryMatchedIds: new Set<string>(),
    })),

  nextMatch: () =>
    set((state) => {
      const matchCount = state.matchedNodeIds.size;
      if (matchCount === 0) return state;
      return {
        activeMatchIndex: (state.activeMatchIndex + 1) % matchCount,
      };
    }),

  prevMatch: () =>
    set((state) => {
      const matchCount = state.matchedNodeIds.size;
      if (matchCount === 0) return state;
      return {
        activeMatchIndex:
          state.activeMatchIndex === 0
            ? matchCount - 1
            : state.activeMatchIndex - 1,
      };
    }),

  setRawConfigContent: (content) =>
    set(() => ({
      rawConfigContent: content,
    })),

  setHighlightedLine: (line) =>
    set(() => ({
      highlightedLine: line,
    })),

  syncViewWithQuery: (matchedRuleIds) =>
    set((state) => {
      // Convert rule IDs to node IDs format
      const nodeIds = matchedRuleIds.map((id) =>
        id.startsWith("rule-") ? id : `rule-${id}`
      );
      return {
        queryMatchedIds: new Set(nodeIds),
        // Auto-expand parent nodes to show matches
        expandedNodes: new Set([...state.expandedNodes, ...getParentIds(nodeIds)]),
      };
    }),
}));

// Helper to get parent IDs from matched node IDs
function getParentIds(nodeIds: string[]): string[] {
  const parents: string[] = [];
  nodeIds.forEach((id) => {
    // Extract table and chain from rule ID pattern: rule-{line}
    // We need to expand the parent chain/table nodes
    const parts = id.split("-");
    if (parts[0] === "rule") {
      // Pattern varies, but we'll handle common cases
    }
  });
  return parents;
}
