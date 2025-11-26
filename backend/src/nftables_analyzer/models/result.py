"""Evaluation result models."""

from typing import Literal

from pydantic import BaseModel, Field

from nftables_analyzer.models.rule import Rule


class Conflict(BaseModel):
    """Represents a conflict between rules."""

    rule1: Rule
    rule2: Rule
    reason: str

    def __str__(self) -> str:
        """Human-readable representation."""
        return (
            f"Conflict: {self.rule1.chain} line {self.rule1.line_number} "
            f"vs line {self.rule2.line_number} - {self.reason}"
        )


class EvaluationResult(BaseModel):
    """Result of evaluating a query against rules."""

    verdict: Literal["ALLOW", "BLOCK", "NO_MATCH", "CONFLICT"]
    matched_rules: list[Rule] = Field(default_factory=list)
    conflicts: list[Conflict] = Field(default_factory=list)
    explanation: str
    trace: list[str] = Field(default_factory=list, description="Step-by-step trace")

    def add_trace(self, step: str) -> None:
        """Add a step to the trace."""
        self.trace.append(step)

    def add_conflict(self, rule1: Rule, rule2: Rule, reason: str) -> None:
        """Add a conflict."""
        self.conflicts.append(Conflict(rule1=rule1, rule2=rule2, reason=reason))
