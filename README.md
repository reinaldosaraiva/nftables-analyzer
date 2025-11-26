# NFTables Analyzer

[![CI Pipeline](https://github.com/reinaldosaraiva/nftables-analyzer/actions/workflows/ci.yml/badge.svg)](https://github.com/reinaldosaraiva/nftables-analyzer/actions/workflows/ci.yml)
[![Security Pipeline](https://github.com/reinaldosaraiva/nftables-analyzer/actions/workflows/security.yml/badge.svg)](https://github.com/reinaldosaraiva/nftables-analyzer/actions/workflows/security.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

> **Visualize, analyze, and query nftables firewall rules with an interactive graph interface.**

<p align="center">
  <img src="docs/screenshot.png" alt="NFTables Analyzer Screenshot" width="800">
</p>

## Overview

NFTables Analyzer helps network administrators and security engineers understand complex firewall configurations by:

- **Visualizing** firewall rules as an interactive network graph
- **Querying** traffic flows to instantly see which rules allow or block traffic
- **Detecting** redundant, shadowed, or conflicting rules
- **Understanding** rule precedence with step-by-step evaluation traces

## Features

| Feature | Description |
|---------|-------------|
| **Visual Graph** | Interactive React Flow visualization of firewall rules |
| **Natural Language Queries** | Ask "can 192.168.1.10 reach port 22?" in plain English |
| **CIDR Matching** | Full support for IP ranges (e.g., 192.168.0.0/24) |
| **Rule Analysis** | Detect redundant rules and potential conflicts |
| **Dual Interface** | Web UI for visualization + CLI for automation |
| **API First** | RESTful API for integration with other tools |

## Quick Start

### Option 1: Docker (Recommended)

```bash
# Clone the repository
git clone https://github.com/reinaldosaraiva/nftables-analyzer.git
cd nftables-analyzer

# Start with Docker Compose
docker-compose up -d

# Open in browser
open http://localhost:3000
```

### Option 2: Local Development

```bash
# Clone the repository
git clone https://github.com/reinaldosaraiva/nftables-analyzer.git
cd nftables-analyzer

# Install dependencies
make install

# Start backend (terminal 1)
make local-backend

# Start frontend (terminal 2)
make local-frontend

# Open in browser
open http://localhost:3000
```

### Option 3: CLI Only

```bash
cd backend
uv sync
uv run nftables-analyzer --help
```

## Usage

### Web Interface

1. **Upload Rules**: Paste your nftables rules or upload a file
2. **Visualize**: See rules as an interactive graph
3. **Query**: Test traffic flows and see which rules match

### Example Rules

```
ip saddr 192.168.1.0/24 tcp dport 22 accept
ip saddr 10.0.0.0/8 tcp dport 443 accept
ip saddr 0.0.0.0/0 tcp dport 80 accept
ip daddr 192.168.1.100 tcp dport 3306 drop
```

### CLI Commands

```bash
# Evaluate a traffic query
nftables-analyzer query rules.txt "from 192.168.1.10 to port 22 tcp"

# List all rules
nftables-analyzer list-rules rules.txt

# Check for redundant rules
nftables-analyzer check-redundant rules.txt

# Get query syntax help
nftables-analyzer query-help
```

### API Endpoints

| Endpoint | Method | Description |
|----------|--------|-------------|
| `/api/v1/rules/parse` | POST | Parse rules and get graph data |
| `/api/v1/rules/query` | POST | Evaluate traffic query |
| `/api/v1/rules/redundant` | GET | Find redundant rules |
| `/api/v1/health` | GET | Health check |

**Example API Call:**

```bash
curl -X POST http://localhost:8000/api/v1/rules/parse \
  -H "Content-Type: application/json" \
  -d '{"content": "ip saddr 192.168.1.0/24 tcp dport 22 accept", "format": "text"}'
```

## Architecture

```
nftables-analyzer/
├── backend/                    # Python FastAPI + CLI
│   ├── src/nftables_analyzer/
│   │   ├── api/               # REST API (FastAPI)
│   │   ├── cli.py             # CLI (Typer + Rich)
│   │   ├── parser/            # Rule parsing
│   │   ├── evaluator/         # Traffic evaluation
│   │   └── interpreter/       # Natural language processing
│   └── tests/                 # 60+ pytest tests
│
├── frontend/                   # Next.js 15 + React Flow
│   ├── src/
│   │   ├── app/               # Next.js App Router
│   │   ├── components/        # React components
│   │   └── lib/               # API client + types
│   └── package.json
│
├── .github/workflows/          # CI/CD + Security
│   ├── ci.yml                 # Lint, Test, Build
│   ├── security.yml           # SAST, SCA, Container scans
│   └── release.yml            # Docker + GitHub Release
│
├── docker-compose.yml          # Production setup
├── docker-compose.dev.yml      # Development setup
└── Makefile                    # Unified commands
```

## Tech Stack

### Backend
- **Python 3.11+** with type hints
- **FastAPI** for REST API
- **Typer + Rich** for CLI
- **Pydantic** for validation
- **UV** for package management

### Frontend
- **Next.js 15** with App Router
- **React Flow** (@xyflow/react) for graph visualization
- **TypeScript** strict mode
- **Tailwind CSS** for styling

### DevOps
- **Docker** multi-stage builds
- **GitHub Actions** CI/CD
- **Security scanning**: Bandit, Semgrep, Trivy, CodeQL, Gitleaks

## Development

### Prerequisites

- Python 3.11+
- Node.js 20+
- UV (`pip install uv`)
- Docker (optional)

### Commands

```bash
make help              # Show all commands

# Docker
make dev               # Start all services in Docker
make build             # Build production images

# Local
make install           # Install all dependencies
make local-backend     # Start backend (port 8000)
make local-frontend    # Start frontend (port 3000)

# Quality
make test              # Run all tests
make lint              # Run linters
make clean             # Clean up
```

### Running Tests

```bash
# Backend tests
cd backend && uv run pytest -v --cov

# Frontend build check
cd frontend && npm run build
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

### GitFlow

- `main` - Production releases
- `develop` - Development integration
- `feature/*` - New features
- `release/*` - Release preparation
- `hotfix/*` - Urgent fixes

## Security

This project follows DevSecOps practices with automated security scanning:

- **SAST**: Bandit (Python), Semgrep (multi-language)
- **SCA**: pip-audit, npm audit
- **Container**: Trivy vulnerability scanning
- **Secrets**: Gitleaks detection
- **Code Analysis**: GitHub CodeQL

Report security vulnerabilities via [GitHub Security Advisories](https://github.com/reinaldosaraiva/nftables-analyzer/security/advisories).

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Acknowledgments

- [nftables](https://netfilter.org/projects/nftables/) - The Linux kernel firewall
- [React Flow](https://reactflow.dev/) - Graph visualization library
- [FastAPI](https://fastapi.tiangolo.com/) - Modern Python web framework

---

<p align="center">
  Made with ❤️ by <a href="https://github.com/reinaldosaraiva">reinaldosaraiva</a>
</p>
