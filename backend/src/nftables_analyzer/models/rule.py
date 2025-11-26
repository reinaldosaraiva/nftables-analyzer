"""Rule, Chain, and Table models."""

from typing import Literal

from pydantic import BaseModel, Field


class Rule(BaseModel):
    """Represents a single nftables rule."""

    action: Literal["accept", "drop", "reject", "jump", "return"]
    chain: str
    table: str = "filter"
    source: str | None = None
    destination: str | None = None
    sport: str | None = None
    dport: str | None = None
    protocol: Literal["tcp", "udp", "icmp", "any"] | None = None
    line_number: int
    raw: str | None = Field(default=None, description="Original rule text")

    def __str__(self) -> str:
        """Human-readable representation."""
        parts = [f"{self.table}/{self.chain}"]
        if self.source:
            parts.append(f"src={self.source}")
        if self.destination:
            parts.append(f"dst={self.destination}")
        if self.protocol:
            parts.append(f"proto={self.protocol}")
        if self.sport:
            parts.append(f"sport={self.sport}")
        if self.dport:
            parts.append(f"dport={self.dport}")
        parts.append(f"→ {self.action}")
        return " ".join(parts)


class Chain(BaseModel):
    """Represents a chain containing multiple rules."""

    name: str
    table: str = "filter"
    policy: Literal["accept", "drop"] = "accept"
    rules: list[Rule] = Field(default_factory=list)

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the chain."""
        self.rules.append(rule)


class Table(BaseModel):
    """Represents a table containing multiple chains."""

    name: str = "filter"
    chains: dict[str, Chain] = Field(default_factory=dict)

    def add_chain(self, chain: Chain) -> None:
        """Add a chain to the table."""
        self.chains[chain.name] = chain

    def get_chain(self, name: str) -> Chain | None:
        """Get a chain by name."""
        return self.chains.get(name)
