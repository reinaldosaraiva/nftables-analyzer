"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";

interface RuleNodeProps {
  data: {
    label: string;
    action?: string;
    details?: string;
  };
}

function RuleNode({ data }: RuleNodeProps) {
  const action = data.action || "allow";

  return (
    <div className={`px-4 py-2 ${action}`}>
      <Handle type="target" position={Position.Top} />
      <div className="font-semibold text-xs">{data.label}</div>
      {data.details && (
        <div className="text-xs opacity-80 mt-1">{data.details}</div>
      )}
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default memo(RuleNode);
