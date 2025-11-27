"""Rule, Chain, Table, and Set models."""

from typing import Literal

from pydantic import BaseModel, Field


class Rule(BaseModel):
    """Represents a single nftables rule."""

    action: Literal["accept", "drop", "reject", "jump", "return", "counter", "log"]
    chain: str
    table: str = "filter"
    family: str = "inet"
    source: str | None = None
    destination: str | None = None
    sport: str | None = None
    dport: str | None = None
    protocol: Literal["tcp", "udp", "icmp", "icmpv6", "ah", "esp", "any"] | None = None
    line_number: int
    raw: str | None = Field(default=None, description="Original rule text")
    sets_referenced: list[str] = Field(default_factory=list, description="Sets used in this rule")
    iif: str | None = Field(default=None, description="Input interface")
    oif: str | None = Field(default=None, description="Output interface")

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


class SetDefinition(BaseModel):
    """Represents an nftables set definition."""

    name: str
    table: str
    family: str = "inet"
    type: str = Field(description="Set type: ipv4_addr, inet_service, iface_index, etc.")
    flags: list[str] = Field(default_factory=list, description="Set flags: interval, timeout, etc.")
    elements: list[str] = Field(default_factory=list, description="Set elements/values")
    line_number: int = 0


class Chain(BaseModel):
    """Represents a chain containing multiple rules."""

    name: str
    table: str = "filter"
    family: str = "inet"
    type: str | None = Field(default=None, description="Chain type: filter, nat, route")
    hook: str | None = Field(default=None, description="Hook: input, output, forward, prerouting, postrouting")
    priority: str | None = Field(default=None, description="Chain priority")
    policy: Literal["accept", "drop"] = "accept"
    rules: list[Rule] = Field(default_factory=list)
    line_number: int = 0

    def add_rule(self, rule: Rule) -> None:
        """Add a rule to the chain."""
        self.rules.append(rule)

    @property
    def rule_count(self) -> int:
        """Return number of rules in chain."""
        return len(self.rules)


class Table(BaseModel):
    """Represents a table containing multiple chains."""

    name: str = "filter"
    family: str = "inet"
    chains: dict[str, Chain] = Field(default_factory=dict)
    sets: dict[str, SetDefinition] = Field(default_factory=dict)
    line_number: int = 0

    def add_chain(self, chain: Chain) -> None:
        """Add a chain to the table."""
        self.chains[chain.name] = chain

    def get_chain(self, name: str) -> Chain | None:
        """Get a chain by name."""
        return self.chains.get(name)

    def add_set(self, set_def: SetDefinition) -> None:
        """Add a set to the table."""
        self.sets[set_def.name] = set_def

    @property
    def chain_count(self) -> int:
        """Return number of chains in table."""
        return len(self.chains)

    @property
    def set_count(self) -> int:
        """Return number of sets in table."""
        return len(self.sets)

    @property
    def rule_count(self) -> int:
        """Return total rules across all chains."""
        return sum(c.rule_count for c in self.chains.values())
