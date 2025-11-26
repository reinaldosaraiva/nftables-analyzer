"""CLI application using Typer."""

from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

from nftables_analyzer.evaluator import RuleEvaluator
from nftables_analyzer.formatter import RuleFormatter
from nftables_analyzer.interpreter import QueryInterpreter
from nftables_analyzer.models import Query
from nftables_analyzer.parser import RuleParser

app = typer.Typer(
    name="nftables-analyzer",
    help="Analyze nftables rules and evaluate traffic queries",
    add_completion=False,
)

console = Console()
formatter = RuleFormatter(console)


@app.command()
def query(
    rules_file: Path = typer.Argument(
        ..., help="Path to nftables rules file (JSON or text)", exists=True
    ),
    query_text: str = typer.Argument(..., help="Natural language query"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Show detailed trace"),
) -> None:
    """Evaluate a traffic query against nftables rules.

    Examples:
        nftables-analyzer query rules.json "from 192.168.1.10 to 10.0.0.5 port 80 tcp"
        nftables-analyzer query rules.txt "incoming traffic from 192.168.0.0/24 to port 443"
    """
    try:
        # Parse rules
        formatter.format_info(f"Loading rules from: {rules_file}")
        rules = RuleParser.parse_file(rules_file)
        formatter.format_info(f"Loaded {len(rules)} rules\n")

        # Parse query
        parsed_query = QueryInterpreter.parse(query_text)
        formatter.format_info(f"Query: {parsed_query}\n")

        # Evaluate
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate(parsed_query)

        # Display result
        formatter.format_result(result)

    except Exception as e:
        formatter.format_error(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def list_rules(
    rules_file: Path = typer.Argument(
        ..., help="Path to nftables rules file (JSON or text)", exists=True
    ),
    chain: Optional[str] = typer.Option(None, "--chain", "-c", help="Filter by chain name"),
) -> None:
    """List all rules from a file.

    Examples:
        nftables-analyzer list-rules rules.json
        nftables-analyzer list-rules rules.txt --chain input
    """
    try:
        # Parse rules
        formatter.format_info(f"Loading rules from: {rules_file}\n")
        rules = RuleParser.parse_file(rules_file)

        # Filter by chain if specified
        if chain:
            rules = [r for r in rules if r.chain.lower() == chain.lower()]
            formatter.format_rules(rules, f"Rules in chain: {chain}")
        else:
            formatter.format_rules(rules, "All Rules")

    except Exception as e:
        formatter.format_error(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def check_redundant(
    rules_file: Path = typer.Argument(
        ..., help="Path to nftables rules file (JSON or text)", exists=True
    ),
) -> None:
    """Find redundant rules (rules that shadow other rules).

    Examples:
        nftables-analyzer check-redundant rules.json
    """
    try:
        # Parse rules
        formatter.format_info(f"Loading rules from: {rules_file}\n")
        rules = RuleParser.parse_file(rules_file)
        formatter.format_info(f"Analyzing {len(rules)} rules for redundancy...\n")

        # Find redundant rules
        evaluator = RuleEvaluator(rules)
        redundant = evaluator.find_redundant_rules()

        # Display results
        formatter.format_redundant_rules(redundant)

    except Exception as e:
        formatter.format_error(f"Error: {e}")
        raise typer.Exit(code=1)


@app.command()
def query_help() -> None:
    """Show help for natural language query syntax."""
    help_text = QueryInterpreter.help_text()
    console.print(help_text)


def main() -> None:
    """Entry point for CLI."""
    app()


if __name__ == "__main__":
    main()
