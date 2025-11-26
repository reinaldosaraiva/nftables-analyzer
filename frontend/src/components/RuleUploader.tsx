"use client";

import { useState } from "react";
import { parseRules } from "@/lib/api";
import type { ParseResponse } from "@/lib/types";

interface RuleUploaderProps {
  onRulesLoaded: (data: ParseResponse, rulesText: string) => void;
  onError: (error: string) => void;
}

export default function RuleUploader({ onRulesLoaded, onError }: RuleUploaderProps) {
  const [rulesText, setRulesText] = useState("");
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!rulesText.trim()) return;

    setLoading(true);
    try {
      const data = await parseRules(rulesText);
      onRulesLoaded(data, rulesText);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Failed to parse rules");
    } finally {
      setLoading(false);
    }
  };

  const handleFileUpload = async (e: React.ChangeEvent<HTMLInputElement>) => {
    const file = e.target.files?.[0];
    if (!file) return;

    const text = await file.text();
    setRulesText(text);
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Upload Rules</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">
            Paste Rules or Upload File
          </label>
          <textarea
            value={rulesText}
            onChange={(e) => setRulesText(e.target.value)}
            className="w-full h-32 bg-gray-700 text-white rounded-lg p-3 focus:ring-2 focus:ring-blue-500 outline-none font-mono text-sm"
            placeholder="add rule inet filter input tcp dport 22 accept&#10;add rule inet filter input tcp dport 80 accept"
          />
        </div>

        <div>
          <input
            type="file"
            accept=".txt,.conf"
            onChange={handleFileUpload}
            className="block w-full text-sm text-gray-400 file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:text-sm file:font-semibold file:bg-blue-600 file:text-white hover:file:bg-blue-700 cursor-pointer"
          />
        </div>

        <button
          type="submit"
          disabled={loading || !rulesText.trim()}
          className="w-full bg-blue-600 hover:bg-blue-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          {loading ? "Parsing..." : "Parse Rules"}
        </button>
      </form>
    </div>
  );
}
