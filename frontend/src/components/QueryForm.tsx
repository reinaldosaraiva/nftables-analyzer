"use client";

import { useState } from "react";
import { queryRules } from "@/lib/api";
import type { QueryResponse } from "@/lib/types";

interface QueryFormProps {
  rulesContent: string;
  onQueryResult: (result: QueryResponse) => void;
  onError: (error: string) => void;
}

export default function QueryForm({ rulesContent, onQueryResult, onError }: QueryFormProps) {
  const [formData, setFormData] = useState({
    src_ip: "192.168.1.10",
    dst_ip: "10.0.0.5",
    port: 22,
    protocol: "tcp",
  });
  const [loading, setLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setLoading(true);

    try {
      const result = await queryRules(rulesContent, formData);
      onQueryResult(result);
    } catch (err) {
      onError(err instanceof Error ? err.message : "Failed to query rules");
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h2 className="text-xl font-semibold mb-4">Query Rules</h2>
      <form onSubmit={handleSubmit} className="space-y-4">
        <div>
          <label className="block text-sm font-medium mb-2">Source IP</label>
          <input
            type="text"
            value={formData.src_ip}
            onChange={(e) => setFormData({ ...formData, src_ip: e.target.value })}
            className="w-full bg-gray-700 text-white rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="192.168.1.10"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Destination IP</label>
          <input
            type="text"
            value={formData.dst_ip}
            onChange={(e) => setFormData({ ...formData, dst_ip: e.target.value })}
            className="w-full bg-gray-700 text-white rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="10.0.0.5"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Port</label>
          <input
            type="number"
            value={formData.port}
            onChange={(e) => setFormData({ ...formData, port: parseInt(e.target.value) })}
            className="w-full bg-gray-700 text-white rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
            placeholder="22"
          />
        </div>

        <div>
          <label className="block text-sm font-medium mb-2">Protocol</label>
          <select
            value={formData.protocol}
            onChange={(e) => setFormData({ ...formData, protocol: e.target.value })}
            className="w-full bg-gray-700 text-white rounded-lg p-2 focus:ring-2 focus:ring-blue-500 outline-none"
          >
            <option value="tcp">TCP</option>
            <option value="udp">UDP</option>
            <option value="icmp">ICMP</option>
          </select>
        </div>

        <button
          type="submit"
          disabled={loading}
          className="w-full bg-green-600 hover:bg-green-700 disabled:bg-gray-600 disabled:cursor-not-allowed text-white font-semibold py-2 px-4 rounded-lg transition"
        >
          {loading ? "Querying..." : "Query"}
        </button>
      </form>
    </div>
  );
}
