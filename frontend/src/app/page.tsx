"use client";

import { useState } from "react";
import RuleUploader from "@/components/RuleUploader";
import RuleGraph from "@/components/RuleGraph";
import QueryForm from "@/components/QueryForm";
import ResultPanel from "@/components/ResultPanel";
import type { ParseResponse, QueryResponse } from "@/lib/types";

export default function Home() {
  const [graphData, setGraphData] = useState<ParseResponse | null>(null);
  const [rulesText, setRulesText] = useState<string>("");
  const [queryResult, setQueryResult] = useState<QueryResponse | null>(null);
  const [error, setError] = useState<string>("");

  const handleRulesLoaded = (data: ParseResponse, rules: string) => {
    setGraphData(data);
    setRulesText(rules);
    setQueryResult(null);
    setError("");
  };

  const handleQueryResult = (result: QueryResponse) => {
    setQueryResult(result);
    setError("");
  };

  const handleError = (errorMessage: string) => {
    setError(errorMessage);
  };

  return (
    <div className="min-h-screen p-8">
      <header className="mb-8">
        <h1 className="text-4xl font-bold text-white mb-2">
          NFTables Analyzer
        </h1>
        <p className="text-gray-400">
          Visualize and analyze nftables firewall rules
        </p>
      </header>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Left Panel */}
        <div className="lg:col-span-1 space-y-6">
          <RuleUploader onRulesLoaded={handleRulesLoaded} onError={handleError} />
          {graphData && (
            <QueryForm
              rulesContent={rulesText}
              onQueryResult={handleQueryResult}
              onError={handleError}
            />
          )}
          {queryResult && <ResultPanel result={queryResult} />}
          {error && (
            <div className="bg-red-900/30 border border-red-700 rounded-lg p-4">
              <p className="text-red-300 text-sm">{error}</p>
            </div>
          )}
        </div>

        {/* Graph Panel */}
        <div className="lg:col-span-2">
          {graphData ? (
            <RuleGraph
              graphData={queryResult?.graph || graphData.graph}
              highlightedNodes={queryResult?.matched_rules.map(r => `rule-${r.line_number}`) || []}
            />
          ) : (
            <div className="bg-gray-800 rounded-lg p-12 text-center">
              <p className="text-gray-400 text-lg">
                Upload rules to visualize the firewall graph
              </p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
