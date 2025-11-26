# nftables-analyzer

A CLI tool for analyzing nftables rules and evaluating traffic queries using natural language.

## Features

- Parse nftables rules from JSON or text format
- Evaluate traffic queries using natural language
- CIDR notation support for IP matching
- Port range matching
- Rich CLI output with tables and colors
- Find redundant and conflicting rules
- Step-by-step evaluation trace

## Installation

```bash
# Using uv (recommended)
uv pip install -e .

# Using pip
pip install -e .
```

## Usage

### Evaluate a Traffic Query

```bash
nftables-analyzer query rules.json "from 192.168.1.10 to 10.0.0.5 port 80 tcp"
nftables-analyzer query rules.txt "incoming traffic from 192.168.0.0/24 to port 443"
```

### List All Rules

```bash
nftables-analyzer list-rules rules.json
nftables-analyzer list-rules rules.txt --chain input
```

### Check for Redundant Rules

```bash
nftables-analyzer check-redundant rules.json
```

### Query Syntax Help

```bash
nftables-analyzer query-help
```

## Natural Language Query Examples

- `"from 192.168.1.10 to 10.0.0.5 port 80 tcp"`
- `"incoming traffic from 192.168.0.0/24 to port 443"`
- `"outgoing tcp to 8.8.8.8 port 53"`
- `"from 172.16.0.1 source port 12345 to 192.168.1.1 port 22"`

## Development

```bash
# Install dev dependencies
uv pip install -e ".[dev]"

# Run tests
pytest

# Run linter
ruff check .

# Run type checker
mypy src/
```

## Architecture

```
nftables-analyzer/
├── src/nftables_analyzer/
│   ├── cli.py              # Typer CLI application
│   ├── models/             # Pydantic models
│   ├── parser/             # Rule parsing (JSON/text)
│   ├── evaluator/          # Rule evaluation logic
│   ├── interpreter/        # Natural language parsing
│   └── formatter/          # Rich output formatting
└── tests/                  # Pytest test suite
```
