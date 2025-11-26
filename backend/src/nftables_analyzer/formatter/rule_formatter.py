"""Rich formatting for CLI output."""

from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.text import Text

from nftables_analyzer.models import EvaluationResult, Rule


class RuleFormatter:
    """Formats rules and results using Rich."""

    def __init__(self, console: Console | None = None) -> None:
        """Initialize formatter with optional console."""
        self.console = console or Console()

    def format_rules(self, rules: list[Rule], title: str = "Rules") -> None:
        """Display rules in a table."""
        table = Table(title=title, show_header=True, header_style="bold magenta")
        table.add_column("Line", style="dim", width=6)
        table.add_column("Chain", style="cyan")
        table.add_column("Source", style="green")
        table.add_column("Destination", style="green")
        table.add_column("Protocol", style="yellow")
        table.add_column("Sport", style="blue")
        table.add_column("Dport", style="blue")
        table.add_column("Action", style="bold")

        for rule in rules:
            action_style = "green" if rule.action == "accept" else "red"
            table.add_row(
                str(rule.line_number),
                rule.chain,
                rule.source or "-",
                rule.destination or "-",
                rule.protocol or "-",
                rule.sport or "-",
                rule.dport or "-",
                Text(rule.action.upper(), style=action_style),
            )

        self.console.print(table)

    def format_result(self, result: EvaluationResult) -> None:
        """Display evaluation result with rich formatting."""
        # Verdict panel
        verdict_color = {
            "ALLOW": "green",
            "BLOCK": "red",
            "NO_MATCH": "yellow",
            "CONFLICT": "red bold",
        }.get(result.verdict, "white")

        verdict_panel = Panel(
            Text(result.verdict, style=verdict_color, justify="center"),
            title="Verdict",
            border_style=verdict_color,
        )
        self.console.print(verdict_panel)

        # Explanation
        self.console.print(f"\n[bold]Explanation:[/bold] {result.explanation}\n")

        # Matched rules
        if result.matched_rules:
            self.console.print(f"[bold]Matched Rules ({len(result.matched_rules)}):[/bold]")
            self.format_rules(result.matched_rules, "")

        # Conflicts
        if result.conflicts:
            self.console.print(f"\n[bold red]Conflicts Found ({len(result.conflicts)}):[/bold red]")
            for conflict in result.conflicts:
                self.console.print(f"  - {conflict}")

        # Trace
        if result.trace:
            self.console.print("\n[bold]Evaluation Trace:[/bold]")
            for step in result.trace:
                self.console.print(f"  [dim]{step}[/dim]")

    def format_redundant_rules(self, redundant: list[tuple[Rule, Rule]]) -> None:
        """Display redundant rules."""
        if not redundant:
            self.console.print("[green]No redundant rules found![/green]")
            return

        self.console.print(f"\n[bold yellow]Redundant Rules Found ({len(redundant)}):[/bold yellow]\n")

        for general, specific in redundant:
            self.console.print(
                f"[yellow]Rule {general.line_number} shadows rule {specific.line_number}:[/yellow]"
            )
            self.console.print(f"  General:  {general}")
            self.console.print(f"  Specific: {specific}\n")

    def format_error(self, error: str) -> None:
        """Display error message."""
        self.console.print(Panel(error, title="Error", border_style="red"))

    def format_info(self, message: str) -> None:
        """Display info message."""
        self.console.print(f"[cyan]{message}[/cyan]")
