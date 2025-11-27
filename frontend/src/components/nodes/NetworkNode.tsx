"use client";

import { memo } from "react";
import { Handle, Position } from "@xyflow/react";

interface NetworkNodeProps {
  data: {
    label: string;
  };
}

function NetworkNode({ data }: NetworkNodeProps) {
  return (
    <div className="px-4 py-2">
      <Handle type="target" position={Position.Top} />
      <div className="font-semibold">{data.label}</div>
      <Handle type="source" position={Position.Bottom} />
    </div>
  );
}

export default memo(NetworkNode);
