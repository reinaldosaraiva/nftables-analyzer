"use client";

import { memo } from "react";
import { Handle, Position, type NodeProps } from "@xyflow/react";

function NetworkNode({ data }: NodeProps) {
  return (
    <div className="px-4 py-2">
      <Handle type="target" position={Position.Top} />
      <div className="font-semibold">{data.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default memo(NetworkNode);
