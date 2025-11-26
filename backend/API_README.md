# nftables-analyzer API

FastAPI REST API for analyzing nftables firewall rules and evaluating traffic queries.

## Installation

Install dependencies with uv:

```bash
cd backend
uv sync
```

Or with pip:

```bash
pip install -e .
```

## Running the API

### Development server (with auto-reload):

```bash
python run_api.py
```

Or using uvicorn directly:

```bash
uvicorn nftables_analyzer.api.main:app --reload --host 0.0.0.0 --port 8000
```

### Production server:

```bash
uvicorn nftables_analyzer.api.main:app --host 0.0.0.0 --port 8000 --workers 4
```

The API will be available at: `http://localhost:8000`

API documentation: `http://localhost:8000/docs`

## API Endpoints

### Health Check

**GET** `/api/v1/health`

Returns API health status.

**Response:**
```json
{
  "status": "healthy",
  "service": "nftables-analyzer"
}
```

---

### Parse Rules

**POST** `/api/v1/rules/parse`

Parse nftables rules from text or JSON format and return rules with graph visualization data.

**Request Body:**
```json
{
  "content": "ip saddr 192.168.1.0/24 tcp dport 22 accept\nip saddr 10.0.0.0/8 drop",
  "format": "text"
}
```

**Response:**
```json
{
  "rules": [
    {
      "action": "accept",
      "chain": "input",
      "table": "filter",
      "source": "192.168.1.0/24",
      "destination": null,
      "sport": null,
      "dport": "22",
      "protocol": "tcp",
      "line_number": 1,
      "raw": "ip saddr 192.168.1.0/24 tcp dport 22 accept"
    }
  ],
  "graph": {
    "nodes": [
      {
        "id": "src-192.168.1.0-24",
        "type": "network",
        "data": {"label": "192.168.1.0/24", "type": "source"},
        "position": {"x": 0, "y": 0}
      },
      {
        "id": "rule-1",
        "type": "rule",
        "data": {"label": "Rule 1", "action": "accept", "chain": "input"},
        "position": {"x": 300, "y": 0}
      }
    ],
    "edges": [
      {
        "id": "e-src-192.168.1.0-24-rule-1",
        "source": "src-192.168.1.0-24",
        "target": "rule-1",
        "animated": false
      }
    ]
  },
  "count": 2
}
```

---

### Evaluate Query

**POST** `/api/v1/rules/query`

Evaluate a traffic query against firewall rules.

**Request Body (Natural Language):**
```json
{
  "rules_content": "ip saddr 192.168.1.0/24 tcp dport 22 accept",
  "rules_format": "text",
  "query_text": "from 192.168.1.100 to 10.0.0.5 port 22 tcp"
}
```

**Request Body (Structured):**
```json
{
  "rules_content": "ip saddr 192.168.1.0/24 tcp dport 22 accept",
  "rules_format": "text",
  "src_ip": "192.168.1.100",
  "dst_ip": "10.0.0.5",
  "dst_port": 22,
  "protocol": "tcp",
  "direction": "in"
}
```

**Response:**
```json
{
  "verdict": "ALLOW",
  "explanation": "Traffic allowed by rule 1",
  "matched_rules": [
    {
      "action": "accept",
      "chain": "input",
      "table": "filter",
      "source": "192.168.1.0/24",
      "dport": "22",
      "protocol": "tcp",
      "line_number": 1
    }
  ],
  "conflicts": [],
  "trace": [
    "Evaluating query: from 192.168.1.100 to 10.0.0.5:22 proto=tcp (in)",
    "Total rules to check: 1",
    "Relevant rules for chain 'input': 1",
    "Rule 1 matches: accept (src=192.168.1.0/24, dport=22)"
  ],
  "graph": {
    "nodes": [...],
    "edges": [...]
  }
}
```

Possible verdicts:
- `ALLOW` - Traffic is allowed
- `BLOCK` - Traffic is blocked
- `NO_MATCH` - No matching rules (default policy applies)
- `CONFLICT` - Multiple rules with conflicting actions

---

### Check Redundancy

**GET** `/api/v1/rules/redundant?rules_content=...&rules_format=text`

Find redundant rules (rules that shadow other rules).

**Query Parameters:**
- `rules_content` - Rules text or JSON
- `rules_format` - "text" or "json" (default: "text")

**Response:**
```json
{
  "redundant_count": 1,
  "redundant_pairs": [
    {
      "shadowing_rule": {
        "action": "accept",
        "source": "192.168.1.0/24",
        "line_number": 1
      },
      "shadowed_rule": {
        "action": "accept",
        "source": "192.168.1.100",
        "line_number": 5
      },
      "reason": "Rule 1 shadows rule 5"
    }
  ]
}
```

---

## Graph Visualization Format

The API returns graph data in React Flow format with:

**Node Types:**
- `network` - Source/destination IP addresses or networks
- `rule` - Firewall rules
- `port` - Destination ports

**Edge Properties:**
- `animated: true` - When rule is matched by a query
- `style.stroke` - Green (#10b981) for accept, Red (#ef4444) for drop/reject

**Matched Rules Highlighting:**
- Matched rule nodes have yellow/red background based on action
- Edges connected to matched rules are animated

---

## Example Usage with curl

### Parse rules:
```bash
curl -X POST http://localhost:8000/api/v1/rules/parse \
  -H "Content-Type: application/json" \
  -d '{
    "content": "ip saddr 192.168.1.0/24 tcp dport 22 accept\nip saddr 10.0.0.0/8 drop",
    "format": "text"
  }'
```

### Evaluate query:
```bash
curl -X POST http://localhost:8000/api/v1/rules/query \
  -H "Content-Type: application/json" \
  -d '{
    "rules_content": "ip saddr 192.168.1.0/24 tcp dport 22 accept",
    "query_text": "from 192.168.1.100 to 10.0.0.5 port 22 tcp"
  }'
```

### Health check:
```bash
curl http://localhost:8000/api/v1/health
```

---

## CORS Configuration

The API allows CORS from:
- `http://localhost:3000` (Next.js default)
- `http://localhost:5173` (Vite default)

To add more origins, edit `src/nftables_analyzer/api/main.py`:

```python
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://your-frontend:port"],
    ...
)
```

---

## CLI Tool Still Works!

The original CLI tool is unchanged and works independently:

```bash
# Parse and analyze rules
nftables-analyzer parse examples/rules.txt

# Evaluate query
nftables-analyzer query examples/rules.txt "from 192.168.1.10 to port 80"

# Check redundancy
nftables-analyzer redundant examples/rules.txt
```

---

## Architecture

```
src/nftables_analyzer/
├── api/
│   ├── main.py              # FastAPI app
│   ├── schemas.py           # Request/response DTOs
│   ├── routes/
│   │   ├── health.py        # Health endpoint
│   │   └── rules.py         # Rules endpoints
│   └── services/
│       └── graph_service.py # Graph conversion
├── parser/                  # Reused services
├── evaluator/
├── interpreter/
└── models/
```

The API layer is thin and reuses all existing business logic from the CLI tool.

---

## Testing

Run tests:

```bash
pytest tests/
```

With coverage:

```bash
pytest --cov=src/nftables_analyzer --cov-report=html
```

---

## Dependencies

- **FastAPI** - Modern async web framework
- **Uvicorn** - ASGI server
- **Pydantic** - Data validation (already used)
- **Python-multipart** - Form data support

Existing services reused:
- RuleParser
- RuleEvaluator
- QueryInterpreter
- IPMatcher
- All Pydantic models
