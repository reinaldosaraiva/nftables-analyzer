"use client";

import type { QueryResponse } from "@/lib/types";

interface ResultPanelProps {
  result: QueryResponse;
}

export default function ResultPanel({ result }: ResultPanelProps) {
  const isAllow = result.verdict === "ALLOW";
  const isBlock = result.verdict === "BLOCK";
  const isNoMatch = result.verdict === "NO_MATCH";

  const getVerdictColor = () => {
    if (isAllow) return "bg-green-900/30 border-green-700 text-green-400";
    if (isBlock) return "bg-red-900/30 border-red-700 text-red-400";
    if (isNoMatch) return "bg-yellow-900/30 border-yellow-700 text-yellow-400";
    return "bg-orange-900/30 border-orange-700 text-orange-400";
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Query Result</h2>

      <div className={`rounded-lg p-4 mb-4 border ${getVerdictColor()}`}>
        <div className="flex items-center gap-2 mb-2">
          <span className="text-2xl font-bold">{result.verdict}</span>
        </div>
        <p className="text-sm text-gray-300">{result.explanation}</p>
      </div>

      {result.matched_rules.length > 0 && (
        <div className="bg-gray-700 rounded-lg p-4 mb-4">
          <h3 className="text-sm font-semibold mb-2 text-gray-300">
            Matched Rules ({result.matched_rules.length}):
          </h3>
          <div className="space-y-2">
            {result.matched_rules.map((rule, idx) => (
              <div key={idx} className="text-xs">
                <code className="text-blue-300 break-all block">{rule.raw}</code>
                <span className="text-gray-400">
                  Line {rule.line_number} | Action: {rule.action}
                </span>
              </div>
            ))}
          </div>
        </div>
      )}

      {result.trace.length > 0 && (
        <div className="bg-gray-700 rounded-lg p-4">
          <h3 className="text-sm font-semibold mb-2 text-gray-300">Trace:</h3>
          <ul className="text-xs text-gray-400 space-y-1">
            {result.trace.map((step, idx) => (
              <li key={idx}>{step}</li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}
