"use client";

import type { RuleStats } from "@/lib/types";

interface StatsPanelProps {
  stats: RuleStats;
}

export default function StatsPanel({ stats }: StatsPanelProps) {
  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-4">
      <h3 className="text-sm font-semibold text-gray-300 mb-3">Statistics</h3>

      {/* Summary */}
      <div className="grid grid-cols-2 gap-2 mb-4">
        <div className="bg-gray-700/50 rounded p-2 text-center">
          <div className="text-2xl font-bold text-white">{stats.total_rules}</div>
          <div className="text-xs text-gray-400">Rules</div>
        </div>
        <div className="bg-gray-700/50 rounded p-2 text-center">
          <div className="text-2xl font-bold text-white">{stats.total_tables}</div>
          <div className="text-xs text-gray-400">Tables</div>
        </div>
        <div className="bg-gray-700/50 rounded p-2 text-center">
          <div className="text-2xl font-bold text-white">{stats.total_chains}</div>
          <div className="text-xs text-gray-400">Chains</div>
        </div>
        <div className="bg-gray-700/50 rounded p-2 text-center">
          <div className="text-2xl font-bold text-white">{stats.total_sets}</div>
          <div className="text-xs text-gray-400">Sets</div>
        </div>
      </div>

      {/* Actions breakdown */}
      {Object.keys(stats.rules_by_action).length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-medium text-gray-400 mb-2">By Action</h4>
          <div className="flex flex-wrap gap-1">
            {Object.entries(stats.rules_by_action).map(([action, count]) => (
              <span
                key={action}
                className={`text-xs px-2 py-1 rounded ${getActionBgColor(action)}`}
              >
                {action}: {count}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Protocol breakdown */}
      {Object.keys(stats.rules_by_protocol).length > 0 && (
        <div className="mb-3">
          <h4 className="text-xs font-medium text-gray-400 mb-2">By Protocol</h4>
          <div className="flex flex-wrap gap-1">
            {Object.entries(stats.rules_by_protocol).map(([protocol, count]) => (
              <span
                key={protocol}
                className="text-xs px-2 py-1 rounded bg-gray-700 text-gray-300"
              >
                {protocol.toUpperCase()}: {count}
              </span>
            ))}
          </div>
        </div>
      )}

      {/* Table breakdown */}
      {Object.keys(stats.rules_by_table).length > 0 && (
        <div>
          <h4 className="text-xs font-medium text-gray-400 mb-2">By Table</h4>
          <div className="flex flex-wrap gap-1">
            {Object.entries(stats.rules_by_table).map(([table, count]) => (
              <span
                key={table}
                className="text-xs px-2 py-1 rounded bg-blue-900/50 text-blue-300"
              >
                {table}: {count}
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function getActionBgColor(action: string): string {
  switch (action) {
    case "accept":
      return "bg-green-900/50 text-green-300";
    case "drop":
      return "bg-red-900/50 text-red-300";
    case "reject":
      return "bg-orange-900/50 text-orange-300";
    case "jump":
      return "bg-blue-900/50 text-blue-300";
    case "return":
      return "bg-purple-900/50 text-purple-300";
    case "counter":
      return "bg-slate-700/50 text-slate-300";
    case "log":
      return "bg-yellow-900/50 text-yellow-300";
    default:
      return "bg-gray-700 text-gray-300";
  }
}
