"use client";

import { memo } from "react";
import type { TreeNodeData } from "@/lib/types";

interface TreeNodeProps {
  node: TreeNodeData;
  isExpanded: boolean;
  hasChildren: boolean;
  isSelected: boolean;
  isMatch: boolean;
  isQueryMatch?: boolean;
  highlightClasses?: string;
  onToggle: () => void;
  onClick: () => void;
}

const getNodeIcon = (type: TreeNodeData["type"]) => {
  switch (type) {
    case "table":
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M3 10h18M3 14h18m-9-4v8m-7 0h14a2 2 0 002-2V8a2 2 0 00-2-2H5a2 2 0 00-2 2v8a2 2 0 002 2z"
          />
        </svg>
      );
    case "chain":
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M13.828 10.172a4 4 0 00-5.656 0l-4 4a4 4 0 105.656 5.656l1.102-1.101m-.758-4.899a4 4 0 005.656 0l4-4a4 4 0 00-5.656-5.656l-1.1 1.1"
          />
        </svg>
      );
    case "rule":
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M9 12l2 2 4-4m5.618-4.016A11.955 11.955 0 0112 2.944a11.955 11.955 0 01-8.618 3.04A12.02 12.02 0 003 9c0 5.591 3.824 10.29 9 11.622 5.176-1.332 9-6.03 9-11.622 0-1.042-.133-2.052-.382-3.016z"
          />
        </svg>
      );
    case "set":
      return (
        <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"
          />
        </svg>
      );
  }
};

const getActionColor = (action: string | undefined) => {
  switch (action) {
    case "accept":
      return "text-green-400";
    case "drop":
      return "text-red-400";
    case "reject":
      return "text-orange-400";
    case "jump":
      return "text-blue-400";
    case "return":
      return "text-purple-400";
    case "counter":
      return "text-slate-400";
    case "log":
      return "text-yellow-400";
    default:
      return "text-gray-400";
  }
};

const getNodeColor = (type: TreeNodeData["type"]) => {
  switch (type) {
    case "table":
      return "text-blue-400";
    case "chain":
      return "text-cyan-400";
    case "set":
      return "text-amber-400";
    case "rule":
      return "text-gray-300";
  }
};

function TreeNode({
  node,
  isExpanded,
  hasChildren,
  isSelected,
  isMatch,
  isQueryMatch,
  highlightClasses,
  onToggle,
  onClick,
}: TreeNodeProps) {
  const paddingLeft = 12 + node.depth * 20;
  const action = node.metadata.action as string | undefined;

  // Use provided highlight classes or fall back to default behavior
  const baseClasses = highlightClasses || (
    isSelected
      ? "bg-blue-900/50 border-l-4 border-blue-500"
      : isQueryMatch
        ? action === "accept"
          ? "bg-green-900/30 border-l-4 border-green-500"
          : action === "drop"
            ? "bg-red-900/30 border-l-4 border-red-500"
            : "bg-blue-900/30 border-l-4 border-blue-500"
        : isMatch
          ? "bg-yellow-900/30 border-l-4 border-yellow-500"
          : "hover:bg-gray-700/50"
  );

  return (
    <div
      className={`flex items-center h-9 cursor-pointer transition-colors ${baseClasses}`}
      style={{ paddingLeft }}
      onClick={onClick}
    >
      {/* Expand/Collapse button */}
      {hasChildren ? (
        <button
          onClick={(e) => {
            e.stopPropagation();
            onToggle();
          }}
          className="w-5 h-5 flex items-center justify-center mr-1 hover:bg-gray-600 rounded"
        >
          <svg
            className={`w-3 h-3 transition-transform ${isExpanded ? "rotate-90" : ""}`}
            fill="currentColor"
            viewBox="0 0 20 20"
          >
            <path
              fillRule="evenodd"
              d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z"
              clipRule="evenodd"
            />
          </svg>
        </button>
      ) : (
        <div className="w-5 mr-1" />
      )}

      {/* Icon */}
      <span className={`mr-2 ${getNodeColor(node.type)}`}>{getNodeIcon(node.type)}</span>

      {/* Label */}
      <span className={`text-sm truncate flex-1 ${getNodeColor(node.type)}`}>
        {node.label}
      </span>

      {/* Metadata badges */}
      <div className="flex items-center gap-1 mr-2">
        {node.type === "rule" && action && (
          <span
            className={`text-xs px-1.5 py-0.5 rounded ${getActionColor(action)} bg-gray-700/50`}
          >
            {action}
          </span>
        )}
        {node.type === "table" && (
          <span className="text-xs text-gray-500">
            {node.metadata.chain_count as number} chains, {node.metadata.rule_count as number}{" "}
            rules
          </span>
        )}
        {node.type === "chain" && (
          <span className="text-xs text-gray-500">
            {node.metadata.rule_count as number} rules
          </span>
        )}
        {node.type === "set" && (
          <span className="text-xs text-gray-500">
            {node.metadata.element_count as number} elements
          </span>
        )}
      </div>
    </div>
  );
}

export default memo(TreeNode);
