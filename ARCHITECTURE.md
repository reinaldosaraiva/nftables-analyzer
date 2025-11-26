# NFTables Analyzer - Fullstack Architecture

## Overview

Extend the existing nftables-analyzer CLI tool with a web interface featuring graphical visualization of firewall rules using React Flow.

---

## 1. DECISIONS

### Type: FULLSTACK
- **Backend**: FastAPI (reuse existing CLI services)
- **Frontend**: Next.js 15 App Router + React Flow
- **Graph Library**: @xyflow/react (React Flow v12)
- **Styling**: Tailwind CSS + shadcn/ui components
- **State Management**: React Query (TanStack Query) for server state

### Rationale
- FastAPI integrates seamlessly with existing Pydantic models
- Next.js 15 App Router provides optimal performance with Server Components
- React Flow is the industry standard for node-based visualizations
- CLI continues working independently (separation of concerns)

---

## 2. PROJECT STRUCTURE

```
nftables-analyzer/
├── backend/
│   ├── src/nftables_analyzer/
│   │   ├── api/                    # NEW - FastAPI layer
│   │   │   ├── __init__.py
│   │   │   ├── main.py             # FastAPI app entry
│   │   │   ├── deps.py             # Dependencies
│   │   │   └── routes/
│   │   │       ├── __init__.py
│   │   │       ├── rules.py        # Rules endpoints
│   │   │       ├── query.py        # Query endpoints
│   │   │       └── health.py       # Health check
│   │   ├── services/               # NEW - Business logic layer
│   │   │   ├── __init__.py
│   │   │   ├── rule_service.py     # Orchestrates parser + evaluator
│   │   │   └── graph_service.py    # Transforms rules to graph data
│   │   ├── schemas/                # NEW - API schemas
│   │   │   ├── __init__.py
│   │   │   ├── requests.py         # Request DTOs
│   │   │   └── responses.py        # Response DTOs (graph nodes/edges)
│   │   ├── parser/                 # EXISTING
│   │   ├── evaluator/              # EXISTING
│   │   ├── interpreter/            # EXISTING
│   │   ├── formatter/              # EXISTING
│   │   ├── models/                 # EXISTING
│   │   └── cli.py                  # EXISTING (unchanged)
│   ├── tests/
│   │   ├── api/                    # NEW - API tests
│   │   │   ├── test_rules_api.py
│   │   │   └── test_query_api.py
│   │   └── [existing tests]
│   └── pyproject.toml              # Add fastapi, uvicorn
│
├── frontend/
│   ├── src/
│   │   ├── app/
│   │   │   ├── layout.tsx
│   │   │   ├── page.tsx            # Main dashboard
│   │   │   └── api/                # API routes (if needed)
│   │   ├── components/
│   │   │   ├── ui/                 # shadcn components
│   │   │   ├── rules/
│   │   │   │   ├── RuleUploader.tsx
│   │   │   │   ├── RuleGraph.tsx
│   │   │   │   └── RuleTable.tsx
│   │   │   ├── query/
│   │   │   │   ├── QueryForm.tsx
│   │   │   │   └── ResultPanel.tsx
│   │   │   └── shared/
│   │   │       ├── RedundancyWarnings.tsx
│   │   │       └── TraceViewer.tsx
│   │   ├── lib/
│   │   │   ├── api-client.ts       # Fetch wrapper
│   │   │   ├── graph-utils.ts      # Node/edge transformations
│   │   │   └── types.ts            # TypeScript types
│   │   └── hooks/
│   │       ├── useRules.ts
│   │       └── useQuery.ts
│   ├── public/
│   ├── tailwind.config.ts
│   ├── next.config.ts
│   └── package.json
│
├── docker-compose.yml              # Dev environment
├── Makefile                        # Commands
└── README.md
```

---

## 3. API ENDPOINTS (FastAPI)

### Base URL: `/api/v1`

```python
# POST /api/v1/rules/parse
# Parse rules from file upload or text paste
class ParseRulesRequest(BaseModel):
    content: str
    format: Literal["json", "text", "auto"] = "auto"

class ParseRulesResponse(BaseModel):
    rules: list[Rule]
    graph: GraphData  # Nodes and edges for visualization
    warnings: list[str]

# POST /api/v1/rules/query
# Evaluate traffic query
class QueryRequest(BaseModel):
    rules: list[Rule]  # Or rule_id if persisted
    query: Query | str  # Structured or natural language

class QueryResponse(BaseModel):
    result: EvaluationResult
    highlighted_nodes: list[str]  # Node IDs to highlight
    highlighted_edges: list[str]  # Edge IDs to highlight

# GET /api/v1/rules/redundant
# Check for redundant rules
class RedundancyRequest(BaseModel):
    rules: list[Rule]

class RedundancyResponse(BaseModel):
    redundant_pairs: list[tuple[int, int]]  # Line numbers
    warnings: list[RedundancyWarning]

# GET /api/v1/health
# Health check
class HealthResponse(BaseModel):
    status: str = "healthy"
    version: str
```

---

## 4. GRAPH DATA MODEL

```python
# backend/src/nftables_analyzer/schemas/responses.py

class GraphNode(BaseModel):
    """Node for React Flow visualization."""
    id: str
    type: Literal["ip", "network", "port", "rule", "action"]
    data: dict  # label, ip, cidr, port, action, etc.
    position: dict  # x, y coordinates

class GraphEdge(BaseModel):
    """Edge for React Flow visualization."""
    id: str
    source: str
    target: str
    type: Literal["allowed", "blocked", "matched"]
    animated: bool = False
    data: dict  # rule_line, protocol, etc.

class GraphData(BaseModel):
    """Complete graph for visualization."""
    nodes: list[GraphNode]
    edges: list[GraphEdge]
```

### Graph Layout Strategy

```
[Source IPs/Networks] --> [Rules] --> [Destination IPs/Networks]
       (green)           (gray)            (blue)

Example:
  [192.168.1.0/24] --tcp:80--> [Rule 1: ACCEPT] --> [10.0.0.0/8]
  [10.0.0.1]       --any-----> [Rule 2: DROP]   --> [any]
```

---

## 5. FRONTEND COMPONENTS

### RuleUploader.tsx
```typescript
interface RuleUploaderProps {
  onRulesParsed: (data: ParseRulesResponse) => void;
}
// - File dropzone (JSON/text)
// - Textarea for pasting
// - Format detection
```

### RuleGraph.tsx
```typescript
interface RuleGraphProps {
  graph: GraphData;
  highlightedNodes?: string[];
  highlightedEdges?: string[];
  onNodeClick?: (nodeId: string) => void;
}
// - React Flow canvas
// - Custom node types (IP, Network, Rule, Action)
// - Edge labels (protocol, port)
// - Zoom/pan controls
// - Minimap
```

### QueryForm.tsx
```typescript
interface QueryFormProps {
  onSubmit: (query: Query) => void;
}
// - Source IP input
// - Destination IP input
// - Port inputs (src/dst)
// - Protocol dropdown
// - Direction select
// - Natural language textarea (alternative)
```

### ResultPanel.tsx
```typescript
interface ResultPanelProps {
  result: EvaluationResult | null;
}
// - Verdict badge (ALLOW/BLOCK/NO_MATCH/CONFLICT)
// - Explanation text
// - Matched rules list
// - Expandable trace viewer
```

### RedundancyWarnings.tsx
```typescript
interface RedundancyWarningsProps {
  warnings: RedundancyWarning[];
  onWarningClick?: (lineNumbers: [number, number]) => void;
}
// - Warning cards
// - Click to highlight in graph
```

---

## 6. SERVICE LAYER

### GraphService (NEW)
```python
# backend/src/nftables_analyzer/services/graph_service.py

class GraphService:
    """Transforms rules into graph visualization data."""

    @staticmethod
    def rules_to_graph(rules: list[Rule]) -> GraphData:
        """Convert rules to nodes and edges."""
        # 1. Extract unique IPs/networks
        # 2. Create nodes for each
        # 3. Create rule nodes
        # 4. Create edges based on rule criteria
        # 5. Calculate layout positions
        pass

    @staticmethod
    def highlight_matched(
        graph: GraphData,
        matched_rules: list[Rule]
    ) -> tuple[list[str], list[str]]:
        """Return node/edge IDs to highlight."""
        pass
```

### RuleService (NEW)
```python
# backend/src/nftables_analyzer/services/rule_service.py

class RuleService:
    """Orchestrates rule parsing, evaluation, and graph generation."""

    def __init__(self) -> None:
        self.graph_service = GraphService()

    def parse_and_graph(self, content: str, format: str) -> ParseRulesResponse:
        """Parse rules and generate graph data."""
        rules = RuleParser.parse_text(content) if format == "text" else RuleParser.parse_json(content)
        graph = self.graph_service.rules_to_graph(rules)
        return ParseRulesResponse(rules=rules, graph=graph, warnings=[])

    def evaluate_query(
        self,
        rules: list[Rule],
        query: Query
    ) -> QueryResponse:
        """Evaluate query and return result with highlights."""
        evaluator = RuleEvaluator(rules)
        result = evaluator.evaluate(query)

        # Generate graph and highlights
        graph = self.graph_service.rules_to_graph(rules)
        nodes, edges = self.graph_service.highlight_matched(graph, result.matched_rules)

        return QueryResponse(
            result=result,
            highlighted_nodes=nodes,
            highlighted_edges=edges,
        )
```

---

## 7. DEPENDENCIES

### Backend (add to pyproject.toml)
```toml
[project.optional-dependencies]
api = [
    "fastapi>=0.109.0",
    "uvicorn[standard]>=0.27.0",
    "python-multipart>=0.0.6",  # File uploads
]
```

### Frontend (package.json)
```json
{
  "dependencies": {
    "next": "15.0.0",
    "react": "^18.3.0",
    "react-dom": "^18.3.0",
    "@xyflow/react": "^12.0.0",
    "@tanstack/react-query": "^5.0.0",
    "tailwindcss": "^3.4.0",
    "class-variance-authority": "^0.7.0",
    "clsx": "^2.1.0",
    "lucide-react": "^0.400.0"
  },
  "devDependencies": {
    "typescript": "^5.5.0",
    "@types/react": "^18.3.0",
    "@types/node": "^20.0.0"
  }
}
```

---

## 8. NEXT_INPUT for Developer

### Backend Tasks:
1. Create `/api/main.py` with FastAPI app (import existing services)
2. Create routes: `rules.py`, `query.py`, `health.py`
3. Create `GraphService` to transform rules to React Flow format
4. Create `RuleService` to orchestrate existing components
5. Add API schemas in `/schemas/`
6. Add CORS middleware for frontend
7. Keep CLI working (don't modify `cli.py`)

### Frontend Tasks:
1. Initialize Next.js 15 with App Router
2. Install React Flow (`@xyflow/react`)
3. Create custom node components (IP, Network, Rule, Action)
4. Create `RuleUploader` with file drop + paste
5. Create `QueryForm` with structured + NL inputs
6. Create `ResultPanel` with verdict display
7. Create `RedundancyWarnings` panel
8. Implement API client with TanStack Query

### Integration:
- Backend runs on port 8000
- Frontend runs on port 3000
- CORS configured for localhost
- Docker Compose for local development

---

## 9. GRAPH VISUALIZATION SPEC

### Node Types:
| Type | Shape | Color | Data |
|------|-------|-------|------|
| `ip` | Circle | Gray | Single IP address |
| `network` | Rounded Rect | Blue | CIDR notation |
| `rule` | Diamond | Green/Red | Rule action + line# |
| `port` | Small circle | Yellow | Port number |
| `any` | Dashed circle | Light gray | Wildcard |

### Edge Types:
| Type | Style | Animated |
|------|-------|----------|
| `allowed` | Solid green | No |
| `blocked` | Solid red | No |
| `matched` | Thick + glow | Yes |

### Layout:
```
Column 1: Sources (left)
Column 2: Rules (center)
Column 3: Destinations (right)

Vertical spacing: 100px per node
Horizontal spacing: 300px between columns
```

---

## 10. FILE ARTIFACTS TO CREATE

### Backend:
- `/backend/src/nftables_analyzer/api/__init__.py`
- `/backend/src/nftables_analyzer/api/main.py`
- `/backend/src/nftables_analyzer/api/deps.py`
- `/backend/src/nftables_analyzer/api/routes/__init__.py`
- `/backend/src/nftables_analyzer/api/routes/rules.py`
- `/backend/src/nftables_analyzer/api/routes/query.py`
- `/backend/src/nftables_analyzer/api/routes/health.py`
- `/backend/src/nftables_analyzer/services/__init__.py`
- `/backend/src/nftables_analyzer/services/rule_service.py`
- `/backend/src/nftables_analyzer/services/graph_service.py`
- `/backend/src/nftables_analyzer/schemas/__init__.py`
- `/backend/src/nftables_analyzer/schemas/requests.py`
- `/backend/src/nftables_analyzer/schemas/responses.py`

### Frontend:
- `/frontend/package.json`
- `/frontend/next.config.ts`
- `/frontend/tailwind.config.ts`
- `/frontend/tsconfig.json`
- `/frontend/src/app/layout.tsx`
- `/frontend/src/app/page.tsx`
- `/frontend/src/components/rules/RuleUploader.tsx`
- `/frontend/src/components/rules/RuleGraph.tsx`
- `/frontend/src/components/query/QueryForm.tsx`
- `/frontend/src/components/query/ResultPanel.tsx`
- `/frontend/src/components/shared/RedundancyWarnings.tsx`
- `/frontend/src/lib/api-client.ts`
- `/frontend/src/lib/types.ts`
- `/frontend/src/hooks/useRules.ts`

### Root:
- `/docker-compose.yml`
- `/Makefile`
