"""FastAPI application entry point."""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from nftables_analyzer.api.routes import health, rules

app = FastAPI(
    title="nftables-analyzer API",
    description="API for analyzing nftables rules and evaluating traffic queries",
    version="0.1.0",
)

# CORS configuration for frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Register routes
app.include_router(health.router, prefix="/api/v1", tags=["health"])
app.include_router(rules.router, prefix="/api/v1/rules", tags=["rules"])


@app.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {
        "message": "nftables-analyzer API",
        "version": "0.1.0",
        "docs": "/docs",
    }
