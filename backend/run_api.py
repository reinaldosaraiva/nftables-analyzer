#!/usr/bin/env python3
"""Development server launcher for nftables-analyzer API."""

import uvicorn

if __name__ == "__main__":
    uvicorn.run(
        "nftables_analyzer.api.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info",
    )
