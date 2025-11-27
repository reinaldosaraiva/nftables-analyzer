"use client";

import React, { useRef } from "react";
import { parseRulesHierarchical } from "@/lib/api";
import type { HierarchicalParseResponse, QueryResponse } from "@/lib/types";
import TreeView from "@/components/hierarchy/TreeView";
import SearchBar from "@/components/hierarchy/SearchBar";
import StatsPanel from "@/components/hierarchy/StatsPanel";
import RuleGraph from "@/components/RuleGraph";
import ConfigViewer from "@/components/ConfigViewer";
import QueryForm from "@/components/QueryForm";
import ResultPanel from "@/components/ResultPanel";
import { useUIStore } from "@/store/uiStore";

export default function Home() {
  const {
    viewMode,
    setViewMode,
    selectedNodeId,
    setExpanded,
    rawConfigContent,
    setRawConfigContent,
    syncViewWithQuery,
    clearQueryMatches,
    setHighlightedLine,
  } = useUIStore();

  const treeContainerRef = useRef<HTMLDivElement>(null);

  const [hierarchyData, setHierarchyData] = React.useState<HierarchicalParseResponse | null>(null);
  const [rulesText, setRulesText] = React.useState<string>("");
  const [queryResult, setQueryResult] = React.useState<QueryResponse | null>(null);
  const [error, setError] = React.useState<string>("");
  const [loading, setLoading] = React.useState(false);

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;
    const text = await file.text();
    setRulesText(text);
  };

  const handleParse = async () => {
    if (!rulesText.trim()) return;
    setLoading(true);
    setError("");
    clearQueryMatches();

    try {
      const data = await parseRulesHierarchical(rulesText);
      setHierarchyData(data);
      setRawConfigContent(rulesText);
      const tableIds = data.tree_nodes.filter((n) => n.type === "table").map((n) => n.id);
      setExpanded(tableIds);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Failed to parse rules");
    } finally {
      setLoading(false);
    }
  };

  const handleNodeSelect = (nodeId: string) => {
    const rule = hierarchyData?.rules.find((r) => `rule-${r.line_number}` === nodeId);
    if (rule) {
      setHighlightedLine(rule.line_number);
    }
  };

  const handleQueryResult = (result: QueryResponse) => {
    setQueryResult(result);
    setError("");
    const matchedIds = result.matched_rules.map((r) => `rule-${r.line_number}`);
    syncViewWithQuery(matchedIds);
  };

  const handleConfigLineClick = (lineNumber: number) => {
    const rule = hierarchyData?.rules.find((r) => r.line_number === lineNumber);
    if (rule) {
      useUIStore.getState().selectNode(`rule-${rule.line_number}`);
    }
  };

  return (
    <div className="h-screen flex flex-col overflow-hidden">
      {/* Header - Fixed */}
      <header className="flex-shrink-0 bg-gray-800 border-b border-gray-700 px-6 py-3">
        <div className="flex items-center justify-between">
          <div>
            <h1 className="text-xl font-bold text-white">NFTables Analyzer</h1>
            <p className="text-xs text-gray-400">Visualize and analyze nftables firewall rules</p>
          </div>
          {hierarchyData && (
            <div className="flex items-center gap-2">
              <ViewModeButton mode="tree" current={viewMode} onClick={() => setViewMode("tree")} icon="tree" label="Tree" />
              <ViewModeButton mode="graph" current={viewMode} onClick={() => setViewMode("graph")} icon="graph" label="Graph" />
              <ViewModeButton mode="config" current={viewMode} onClick={() => setViewMode("config")} icon="config" label="Config" />
            </div>
          )}
        </div>
      </header>

      {/* Main Layout - Fill remaining height */}
      <div className="flex-1 flex min-h-0">
        {/* Left Sidebar - Fixed width, internal scroll */}
        <aside className="w-72 flex-shrink-0 bg-gray-800 border-r border-gray-700 flex flex-col overflow-hidden">
          {/* Upload Section - Fixed */}
          <div className="flex-shrink-0 p-3 border-b border-gray-700">
            <h2 className="text-xs font-semibold text-gray-400 uppercase mb-2">Upload Rules</h2>
            <textarea
              value={rulesText}
              onChange={(e) => setRulesText(e.target.value)}
              className="w-full h-16 bg-gray-900 text-gray-100 rounded p-2 text-xs font-mono focus:ring-1 focus:ring-blue-500 outline-none resize-none border border-gray-700"
              placeholder="Paste nftables rules here..."
            />
            <div className="flex gap-2 mt-2">
              <label className="flex-1 cursor-pointer">
                <span className="block text-center bg-gray-700 hover:bg-gray-600 text-gray-300 text-xs py-1.5 rounded transition">
                  Upload
                </span>
                <input type="file" accept=".txt,.conf,.nft" onChange={handleFileUpload} className="hidden" />
              </label>
              <button
                onClick={handleParse}
                disabled={loading || !rulesText.trim()}
                className="flex-1 bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white text-xs py-1.5 rounded transition"
              >
                {loading ? "..." : "Parse"}
              </button>
            </div>
          </div>

          {/* Stats - Fixed */}
          {hierarchyData && (
            <div className="flex-shrink-0 p-3 border-b border-gray-700">
              <StatsPanel stats={hierarchyData.stats} />
            </div>
          )}

          {/* Search - Fixed */}
          {hierarchyData && (
            <div className="flex-shrink-0 p-3 border-b border-gray-700">
              <SearchBar placeholder="Search rules, IPs, ports..." />
            </div>
          )}

          {/* Tree View - Scrollable, with minimum height */}
          {hierarchyData && (
            <div ref={treeContainerRef} className="flex-1 overflow-y-auto overflow-x-hidden" style={{ minHeight: "200px" }}>
              <TreeView
                nodes={hierarchyData.tree_nodes}
                onNodeSelect={handleNodeSelect}
                containerRef={treeContainerRef as React.RefObject<HTMLDivElement>}
              />
            </div>
          )}

          {/* Query Form - Fixed at bottom */}
          {hierarchyData && (
            <div className="flex-shrink-0 p-3 border-t border-gray-700 bg-gray-800">
              <QueryForm rulesContent={rulesText} onQueryResult={handleQueryResult} onError={setError} />
            </div>
          )}
        </aside>

        {/* Main Content - Fills remaining width, internal scroll */}
        <main className="flex-1 flex flex-col min-h-0 min-w-0 bg-gray-900">
          {/* Error/Result - Fixed at top */}
          {(error || queryResult) && (
            <div className="flex-shrink-0 p-3 space-y-2">
              {error && (
                <div className="bg-red-900/30 border border-red-700 rounded p-3">
                  <p className="text-red-300 text-sm">{error}</p>
                </div>
              )}
              {queryResult && <ResultPanel result={queryResult} />}
            </div>
          )}

          {/* Content Area - Scrollable */}
          {hierarchyData ? (
            <div className="flex-1 min-h-0 overflow-auto p-4">
              {viewMode === "graph" && (
                <RuleGraph
                  graphData={queryResult?.graph || hierarchyData.graph}
                  highlightedNodes={queryResult?.matched_rules.map((r) => `rule-${r.line_number}`) || []}
                />
              )}

              {viewMode === "config" && (
                <div className="h-full">
                  <ConfigViewer
                    content={rawConfigContent}
                    rules={hierarchyData.rules}
                    sets={hierarchyData.sets}
                    onLineClick={handleConfigLineClick}
                  />
                </div>
              )}

              {viewMode === "tree" && (
                <>
                  {selectedNodeId ? (
                    <RuleDetailsPanel nodeId={selectedNodeId} hierarchyData={hierarchyData} />
                  ) : (
                    <div className="bg-gray-800 rounded-lg p-8 text-center">
                      <p className="text-gray-400">Select a rule from the tree view to see details</p>
                    </div>
                  )}
                </>
              )}
            </div>
          ) : (
            <div className="flex-1 flex items-center justify-center">
              <div className="text-center">
                <svg className="w-16 h-16 mx-auto text-gray-600 mb-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={1.5}
                    d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
                </svg>
                <h2 className="text-xl font-semibold text-gray-400 mb-2">No Rules Loaded</h2>
                <p className="text-gray-500">Upload or paste nftables rules to get started</p>
              </div>
            </div>
          )}
        </main>
      </div>
    </div>
  );
}

function ViewModeButton({ mode, current, onClick, icon, label }: {
  mode: string; current: string; onClick: () => void; icon: string; label: string
}) {
  const icons: Record<string, React.ReactNode> = {
    tree: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M4 6h16M4 10h16M4 14h16M4 18h16" />
    </svg>,
    graph: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M13 10V3L4 14h7v7l9-11h-7z" />
    </svg>,
    config: <svg className="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
      <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M10 20l4-16m4 4l4 4-4 4M6 16l-4-4 4-4" />
    </svg>,
  };

  return (
    <button
      onClick={onClick}
      className={`px-3 py-1.5 rounded text-sm flex items-center gap-1.5 transition ${
        mode === current ? "bg-blue-600 text-white" : "bg-gray-700 text-gray-300 hover:bg-gray-600"
      }`}
    >
      {icons[icon]}
      {label}
    </button>
  );
}

function RuleDetailsPanel({ nodeId, hierarchyData }: { nodeId: string; hierarchyData: HierarchicalParseResponse }) {
  const node = hierarchyData.tree_nodes.find((n) => n.id === nodeId);
  if (!node) return null;

  const rule = hierarchyData.rules.find((r) => `rule-${r.line_number}` === nodeId);
  const referencedSets = rule?.sets_referenced
    ? hierarchyData.sets.filter((s) => rule.sets_referenced.includes(s.name))
    : [];

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-white mb-4">
        {node.type === "rule" ? `Rule Line ${node.metadata.line_number}` : node.label}
      </h3>

      {node.type === "rule" && rule && (
        <div className="space-y-4">
          <div className="grid grid-cols-2 gap-3">
            <InfoItem label="Action" value={rule.action} highlight={rule.action} />
            <InfoItem label="Protocol" value={rule.protocol || "any"} />
            <InfoItem label="Table" value={rule.table} />
            <InfoItem label="Chain" value={rule.chain} />
            <InfoItem label="Source" value={rule.source || "any"} />
            <InfoItem label="Destination" value={rule.destination || "any"} />
            <InfoItem label="Source Port" value={rule.sport || "any"} />
            <InfoItem label="Dest Port" value={rule.dport || "any"} />
            <InfoItem label="Input Interface" value={rule.iif || "any"} />
            <InfoItem label="Output Interface" value={rule.oif || "any"} />
          </div>

          {referencedSets.length > 0 && (
            <div>
              <h4 className="text-sm font-medium text-gray-400 mb-2">Referenced Sets</h4>
              <div className="space-y-2">
                {referencedSets.map((setDef) => (
                  <SetDetailCard key={setDef.name} set={setDef} />
                ))}
              </div>
            </div>
          )}

          <div>
            <h4 className="text-sm font-medium text-gray-400 mb-2">Raw Rule</h4>
            <pre className="bg-gray-900 p-3 rounded text-sm text-gray-100 overflow-x-auto font-mono">{rule.raw}</pre>
          </div>
        </div>
      )}

      {node.type === "table" && (
        <div className="grid grid-cols-2 gap-3">
          <InfoItem label="Family" value={node.metadata.family as string} />
          <InfoItem label="Chains" value={String(node.metadata.chain_count)} />
          <InfoItem label="Sets" value={String(node.metadata.set_count)} />
          <InfoItem label="Rules" value={String(node.metadata.rule_count)} />
        </div>
      )}

      {node.type === "chain" && (
        <div className="grid grid-cols-2 gap-3">
          <InfoItem label="Type" value={(node.metadata.type as string) || "N/A"} />
          <InfoItem label="Hook" value={(node.metadata.hook as string) || "N/A"} />
          <InfoItem label="Policy" value={(node.metadata.policy as string) || "accept"} />
          <InfoItem label="Rules" value={String(node.metadata.rule_count)} />
        </div>
      )}

      {node.type === "set" && (() => {
        // Find the full set data from hierarchyData.sets
        const setData = hierarchyData.sets.find((s) => s.name === node.label);
        return (
          <SetDetailCard
            set={{
              name: node.label,
              type: setData?.type || (node.metadata.type as string) || "unknown",
              flags: setData?.flags || (node.metadata.flags as string[]) || [],
              elements: setData?.elements || (node.metadata.elements as string[]) || [],
            }}
          />
        );
      })()}
    </div>
  );
}

function SetDetailCard({ set }: { set: { name: string; type: string; flags: string[]; elements: string[] } }) {
  const [expanded, setExpanded] = React.useState(false);
  const isLargeSet = set.elements.length > 10;
  const displayElements = expanded ? set.elements : set.elements.slice(0, 10);

  return (
    <div className="bg-gray-900/50 rounded-lg p-3 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <div className="flex items-center gap-2">
          <span className="text-sm font-medium text-amber-400">@{set.name}</span>
          <span className="text-xs text-gray-500">({set.type})</span>
          {set.elements.length > 100 && (
            <span className="text-xs px-1.5 py-0.5 bg-yellow-900/50 text-yellow-400 rounded">Large set</span>
          )}
        </div>
        <span className="text-xs text-gray-500">{set.elements.length} elements</span>
      </div>

      {set.flags.length > 0 && (
        <div className="flex flex-wrap gap-1 mb-2">
          {set.flags.map((flag) => (
            <span key={flag} className="text-xs px-1.5 py-0.5 bg-gray-700 text-gray-300 rounded">{flag}</span>
          ))}
        </div>
      )}

      {set.elements.length > 0 && (
        <div className="mt-2">
          <div className="flex flex-wrap gap-1">
            {displayElements.map((element, idx) => (
              <span key={idx} className="text-xs px-1.5 py-0.5 bg-gray-800 text-gray-200 rounded font-mono">{element}</span>
            ))}
          </div>
          {isLargeSet && (
            <button onClick={() => setExpanded(!expanded)} className="mt-2 text-xs text-blue-400 hover:text-blue-300">
              {expanded ? "Show less" : `Show all ${set.elements.length} elements`}
            </button>
          )}
        </div>
      )}
    </div>
  );
}

function InfoItem({ label, value, highlight }: { label: string; value: string; highlight?: string }) {
  const colors: Record<string, string> = {
    accept: "text-green-400",
    drop: "text-red-400",
    reject: "text-orange-400",
  };

  return (
    <div className="bg-gray-900/30 rounded px-3 py-2">
      <span className="text-xs text-gray-500 block">{label}</span>
      <span className={`text-sm font-medium ${highlight && colors[highlight] ? colors[highlight] : "text-gray-100"}`}>
        {value}
      </span>
    </div>
  );
}
