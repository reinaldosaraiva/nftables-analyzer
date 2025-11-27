"use client";

import { useEffect, useCallback } from "react";
import { useUIStore } from "@/store/uiStore";
import { useMatchNavigation } from "@/hooks/useNodeFiltering";

interface SearchBarProps {
  placeholder?: string;
}

export default function SearchBar({ placeholder = "Search rules..." }: SearchBarProps) {
  const { filters, setFilter, clearFilters, searchMode, setSearchMode } = useUIStore();
  const { matchCount, activeMatchIndex, goToNextMatch, goToPrevMatch } = useMatchNavigation();

  // Keyboard shortcuts
  useEffect(() => {
    const handleKeyDown = (e: KeyboardEvent) => {
      // Ctrl+G or Cmd+G for next match
      if ((e.ctrlKey || e.metaKey) && e.key === "g") {
        e.preventDefault();
        if (e.shiftKey) {
          goToPrevMatch();
        } else {
          goToNextMatch();
        }
      }
      // Ctrl+F or Cmd+F to focus search
      if ((e.ctrlKey || e.metaKey) && e.key === "f") {
        e.preventDefault();
        document.getElementById("search-input")?.focus();
      }
      // Escape to clear search
      if (e.key === "Escape") {
        setFilter({ searchQuery: "" });
      }
    };

    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [goToNextMatch, goToPrevMatch, setFilter]);

  const handleSearchChange = useCallback(
    (e: React.ChangeEvent<HTMLInputElement>) => {
      setFilter({ searchQuery: e.target.value });
    },
    [setFilter]
  );

  return (
    <div className="space-y-3">
      {/* Search input with match counter */}
      <div className="relative">
        <svg
          className="absolute left-3 top-1/2 -translate-y-1/2 w-4 h-4 text-gray-400"
          fill="none"
          stroke="currentColor"
          viewBox="0 0 24 24"
        >
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"
          />
        </svg>
        <input
          id="search-input"
          type="text"
          value={filters.searchQuery}
          onChange={handleSearchChange}
          placeholder={placeholder}
          className="w-full bg-gray-700 text-white rounded-lg pl-10 pr-24 py-2 text-sm focus:ring-2 focus:ring-blue-500 outline-none"
        />

        {/* Match counter and navigation */}
        {filters.searchQuery && (
          <div className="absolute right-2 top-1/2 -translate-y-1/2 flex items-center gap-1">
            {matchCount > 0 ? (
              <>
                <span className="text-xs text-gray-400">
                  {activeMatchIndex + 1}/{matchCount}
                </span>
                <button
                  onClick={goToPrevMatch}
                  className="p-1 hover:bg-gray-600 rounded"
                  title="Previous match (Ctrl+Shift+G)"
                >
                  <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 15l7-7 7 7" />
                  </svg>
                </button>
                <button
                  onClick={goToNextMatch}
                  className="p-1 hover:bg-gray-600 rounded"
                  title="Next match (Ctrl+G)"
                >
                  <svg className="w-3 h-3 text-gray-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M19 9l-7 7-7-7" />
                  </svg>
                </button>
              </>
            ) : (
              <span className="text-xs text-red-400">No matches</span>
            )}
            <button
              onClick={() => setFilter({ searchQuery: "" })}
              className="p-1 hover:bg-gray-600 rounded text-gray-400 hover:text-white"
            >
              <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>
        )}
      </div>

      {/* Search mode toggle */}
      <div className="flex items-center gap-2">
        <span className="text-xs text-gray-400">Mode:</span>
        <div className="flex bg-gray-700 rounded-lg p-0.5">
          <button
            onClick={() => setSearchMode("highlight")}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              searchMode === "highlight"
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white"
            }`}
            title="Highlight matches, show full tree"
          >
            <svg className="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M9.663 17h4.673M12 3v1m6.364 1.636l-.707.707M21 12h-1M4 12H3m3.343-5.657l-.707-.707m2.828 9.9a5 5 0 117.072 0l-.548.547A3.374 3.374 0 0014 18.469V19a2 2 0 11-4 0v-.531c0-.895-.356-1.754-.988-2.386l-.548-.547z" />
            </svg>
            Highlight
          </button>
          <button
            onClick={() => setSearchMode("filter")}
            className={`px-2 py-1 text-xs rounded transition-colors ${
              searchMode === "filter"
                ? "bg-blue-600 text-white"
                : "text-gray-400 hover:text-white"
            }`}
            title="Filter tree to show only matches"
          >
            <svg className="w-3 h-3 inline mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2}
                d="M3 4a1 1 0 011-1h16a1 1 0 011 1v2.586a1 1 0 01-.293.707l-6.414 6.414a1 1 0 00-.293.707V17l-4 4v-6.586a1 1 0 00-.293-.707L3.293 7.293A1 1 0 013 6.586V4z" />
            </svg>
            Filter
          </button>
        </div>
      </div>

      {/* Active filters */}
      {(filters.actionFilter || filters.protocolFilter || filters.tableFilter) && (
        <div className="flex flex-wrap items-center gap-2">
          {filters.actionFilter && (
            <FilterChip
              label={`Action: ${filters.actionFilter}`}
              onRemove={() => setFilter({ actionFilter: null })}
            />
          )}
          {filters.protocolFilter && (
            <FilterChip
              label={`Protocol: ${filters.protocolFilter}`}
              onRemove={() => setFilter({ protocolFilter: null })}
            />
          )}
          {filters.tableFilter && (
            <FilterChip
              label={`Table: ${filters.tableFilter}`}
              onRemove={() => setFilter({ tableFilter: null })}
            />
          )}
          <button
            onClick={clearFilters}
            className="text-xs text-gray-400 hover:text-white underline"
          >
            Clear all
          </button>
        </div>
      )}

      {/* Quick filters */}
      <div className="flex flex-wrap gap-1">
        <QuickFilter
          label="accept"
          active={filters.actionFilter === "accept"}
          color="green"
          onClick={() =>
            setFilter({
              actionFilter: filters.actionFilter === "accept" ? null : "accept",
            })
          }
        />
        <QuickFilter
          label="drop"
          active={filters.actionFilter === "drop"}
          color="red"
          onClick={() =>
            setFilter({
              actionFilter: filters.actionFilter === "drop" ? null : "drop",
            })
          }
        />
        <QuickFilter
          label="TCP"
          active={filters.protocolFilter === "tcp"}
          color="blue"
          onClick={() =>
            setFilter({
              protocolFilter: filters.protocolFilter === "tcp" ? null : "tcp",
            })
          }
        />
        <QuickFilter
          label="UDP"
          active={filters.protocolFilter === "udp"}
          color="cyan"
          onClick={() =>
            setFilter({
              protocolFilter: filters.protocolFilter === "udp" ? null : "udp",
            })
          }
        />
      </div>
    </div>
  );
}

function FilterChip({ label, onRemove }: { label: string; onRemove: () => void }) {
  return (
    <span className="inline-flex items-center gap-1 text-xs bg-blue-900/50 text-blue-300 px-2 py-1 rounded">
      {label}
      <button onClick={onRemove} className="hover:text-white">
        <svg className="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path
            strokeLinecap="round"
            strokeLinejoin="round"
            strokeWidth={2}
            d="M6 18L18 6M6 6l12 12"
          />
        </svg>
      </button>
    </span>
  );
}

function QuickFilter({
  label,
  active,
  color,
  onClick,
}: {
  label: string;
  active: boolean;
  color: string;
  onClick: () => void;
}) {
  const colorClasses: Record<string, string> = {
    green: active ? "bg-green-600 text-white" : "bg-gray-700 text-green-400 hover:bg-green-900/50",
    red: active ? "bg-red-600 text-white" : "bg-gray-700 text-red-400 hover:bg-red-900/50",
    blue: active ? "bg-blue-600 text-white" : "bg-gray-700 text-blue-400 hover:bg-blue-900/50",
    cyan: active ? "bg-cyan-600 text-white" : "bg-gray-700 text-cyan-400 hover:bg-cyan-900/50",
  };

  return (
    <button
      onClick={onClick}
      className={`text-xs px-2 py-1 rounded transition-colors ${colorClasses[color]}`}
    >
      {label}
    </button>
  );
}
