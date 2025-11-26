"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";

function RuleNode({ data }: NodeProps) {
  const action = (data.action as string) || "allow";

  return (
    <div className={`px-4 py-2 ${action}`}>
      <Handle type="target" position={Position.Top} />
      <div className="font-semibold text-xs">{data.label}</div>
      {data.details && (
        <div className="text-xs opacity-80 mt-1">{data.details as string}</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default memo(RuleNode);
