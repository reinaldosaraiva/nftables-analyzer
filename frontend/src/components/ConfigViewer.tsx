"use client";

import { useEffect, useRef, useMemo, useCallback } from "react";
import CodeMirror from "@uiw/react-codemirror";
import { EditorView } from "@codemirror/view";
import { useUIStore } from "@/store/uiStore";
import { nftablesSyntax } from "@/lib/nftables-lang";
import type { Rule, SetDefinition } from "@/lib/types";

interface ConfigViewerProps {
  content: string;
  rules?: Rule[];
  sets?: SetDefinition[];
  onLineClick?: (lineNumber: number) => void;
}

// Dark theme with high contrast for nftables
const nftablesTheme = EditorView.theme({
  "&": {
    backgroundColor: "#0f172a",
    color: "#e2e8f0",
  },
  ".cm-content": {
    fontFamily: "ui-monospace, SFMono-Regular, 'SF Mono', Menlo, Consolas, monospace",
    fontSize: "14px",
    lineHeight: "1.7",
    caretColor: "#fff",
  },
  ".cm-gutters": {
    backgroundColor: "#1e293b",
    color: "#64748b",
    border: "none",
    borderRight: "1px solid #334155",
  },
  ".cm-lineNumbers .cm-gutterElement": {
    padding: "0 16px 0 12px",
    minWidth: "50px",
  },
  ".cm-activeLine": {
    backgroundColor: "#1e3a5f",
  },
  ".cm-activeLineGutter": {
    backgroundColor: "#1e3a5f",
    color: "#94a3b8",
  },
  ".cm-selectionBackground": {
    backgroundColor: "#3b82f6 !important",
  },
  "&.cm-focused .cm-selectionBackground": {
    backgroundColor: "#3b82f6 !important",
  },
  ".cm-cursor": {
    borderLeftColor: "#fff",
    borderLeftWidth: "2px",
  },
  ".cm-line": {
    color: "#e2e8f0",
  },
}, { dark: true });


export default function ConfigViewer({
  content,
  rules = [],
  sets = [],
  onLineClick,
}: ConfigViewerProps) {
  const editorRef = useRef<HTMLDivElement>(null);
  const {
    highlightedLine,
    queryMatchedIds,
    matchedNodeIds,
    selectedNodeId,
    setHighlightedLine,
  } = useUIStore();

  // Build line number to rule mapping
  const lineToRule = useMemo(() => {
    const map = new Map<number, Rule>();
    rules.forEach((rule) => {
      map.set(rule.line_number, rule);
    });
    return map;
  }, [rules]);

  // Build line number to set mapping
  const lineToSet = useMemo(() => {
    const map = new Map<number, SetDefinition>();
    sets.forEach((set) => {
      map.set(set.line_number, set);
    });
    return map;
  }, [sets]);

  // Get lines that should be highlighted
  const highlightedLines = useMemo(() => {
    const lines: { line: number; type: "search" | "query-accept" | "query-drop" | "selected" }[] = [];

    // Add query matches
    queryMatchedIds.forEach((nodeId) => {
      const match = nodeId.match(/rule-(\d+)/);
      if (match) {
        const lineNum = parseInt(match[1], 10);
        const rule = lineToRule.get(lineNum);
        const type = rule?.action === "accept" ? "query-accept" : "query-drop";
        lines.push({ line: lineNum, type });
      }
    });

    // Add search matches
    matchedNodeIds.forEach((nodeId) => {
      const match = nodeId.match(/rule-(\d+)/);
      if (match) {
        const lineNum = parseInt(match[1], 10);
        if (!lines.some((l) => l.line === lineNum)) {
          lines.push({ line: lineNum, type: "search" });
        }
      }
    });

    // Add selected line
    if (highlightedLine && !lines.some((l) => l.line === highlightedLine)) {
      lines.push({ line: highlightedLine, type: "selected" });
    }

    return lines;
  }, [queryMatchedIds, matchedNodeIds, highlightedLine, lineToRule]);

  // Handle line click
  const handleClick = useCallback(
    (e: React.MouseEvent) => {
      // Get line number from click position
      const target = e.target as HTMLElement;
      const lineElement = target.closest(".cm-line");
      if (lineElement) {
        const parent = lineElement.parentElement;
        if (parent) {
          const lines = parent.querySelectorAll(".cm-line");
          const index = Array.from(lines).indexOf(lineElement);
          if (index >= 0) {
            const lineNum = index + 1;
            setHighlightedLine(lineNum);
            onLineClick?.(lineNum);
          }
        }
      }
    },
    [setHighlightedLine, onLineClick]
  );

  // Scroll to highlighted line when it changes
  useEffect(() => {
    if (highlightedLine && editorRef.current) {
      const lineElement = editorRef.current.querySelector(
        `.cm-line:nth-child(${highlightedLine})`
      );
      if (lineElement) {
        lineElement.scrollIntoView({ behavior: "smooth", block: "center" });
      }
    }
  }, [highlightedLine]);

  // Create extensions with nftables syntax highlighting
  const extensions = useMemo(() => {
    return [
      EditorView.lineWrapping,
      EditorView.editable.of(false),
      nftablesTheme,
      ...nftablesSyntax,
    ];
  }, []);

  return (
    <div className="h-full flex flex-col bg-gray-800 rounded-lg overflow-hidden">
      {/* Toolbar */}
      <div className="flex items-center justify-between px-4 py-2 bg-gray-900 border-b border-gray-700">
        <div className="flex items-center gap-2">
          <svg className="w-4 h-4 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
              d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
          <span className="text-sm text-gray-300">Raw Configuration</span>
          <span className="text-xs text-gray-500">({content.split("\n").length} lines)</span>
        </div>

        {/* Legend */}
        <div className="flex items-center gap-3 text-xs">
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-green-500/30 border-l-2 border-green-500"></span>
            <span className="text-gray-400">Accept</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-red-500/30 border-l-2 border-red-500"></span>
            <span className="text-gray-400">Drop</span>
          </div>
          <div className="flex items-center gap-1">
            <span className="w-3 h-3 bg-yellow-500/30 border-l-2 border-yellow-500"></span>
            <span className="text-gray-400">Search</span>
          </div>
        </div>
      </div>

      {/* Editor */}
      <div ref={editorRef} className="flex-1 overflow-auto" onClick={handleClick}>
        <CodeMirror
          value={content}
          height="100%"
          extensions={extensions}
          basicSetup={{
            lineNumbers: true,
            highlightActiveLineGutter: true,
            highlightActiveLine: true,
            foldGutter: false,
            dropCursor: false,
            allowMultipleSelections: false,
            indentOnInput: false,
            bracketMatching: true,
            closeBrackets: false,
            autocompletion: false,
            rectangularSelection: false,
            crosshairCursor: false,
            highlightSelectionMatches: true,
            closeBracketsKeymap: false,
            searchKeymap: true,
          }}
          editable={false}
        />
      </div>

      {/* Status bar */}
      {highlightedLines.length > 0 && (
        <div className="px-4 py-1 bg-gray-900 border-t border-gray-700 text-xs text-gray-400">
          {highlightedLines.length} highlighted line(s)
          {highlightedLine && ` • Line ${highlightedLine} selected`}
        </div>
      )}
    </div>
  );
}
