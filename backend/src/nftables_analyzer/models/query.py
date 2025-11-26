"""Query model for packet matching."""

from typing import Literal

from pydantic import BaseModel, Field, field_validator


class Query(BaseModel):
    """Represents a packet query for rule evaluation."""

    src_ip: str | None = Field(default=None, description="Source IP address")
    dst_ip: str | None = Field(default=None, description="Destination IP address")
    src_port: int | None = Field(default=None, ge=1, le=65535, description="Source port")
    dst_port: int | None = Field(default=None, ge=1, le=65535, description="Destination port")
    protocol: str | None = Field(default=None, description="Protocol (tcp, udp, icmp)")
    direction: Literal["in", "out", "forward"] = Field(
        default="in", description="Traffic direction"
    )

    @field_validator("protocol")
    @classmethod
    def validate_protocol(cls, v: str | None) -> str | None:
        """Validate and normalize protocol."""
        if v is None:
            return None
        v = v.lower()
        if v not in ["tcp", "udp", "icmp", "any"]:
            raise ValueError(f"Invalid protocol: {v}")
        return v

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = []
        if self.src_ip:
            parts.append(f"from {self.src_ip}")
            if self.src_port:
                parts.append(f":{self.src_port}")
        if self.dst_ip:
            parts.append(f"to {self.dst_ip}")
            if self.dst_port:
                parts.append(f":{self.dst_port}")
        if self.protocol:
            parts.append(f"proto={self.protocol}")
        parts.append(f"({self.direction})")
        return " ".join(parts)
