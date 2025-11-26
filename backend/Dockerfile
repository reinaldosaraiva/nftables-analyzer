# Multi-stage Dockerfile for FastAPI backend

# Development stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm AS development

WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./

# Install dependencies (dev + runtime)
RUN uv pip install --system --no-cache -e ".[dev]"

# Copy source code
COPY src/ ./src/

EXPOSE 8000

CMD ["uvicorn", "nftables_analyzer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]

# Builder stage
FROM ghcr.io/astral-sh/uv:python3.11-bookworm-slim AS builder

WORKDIR /app

# Copy dependency files
COPY pyproject.toml README.md ./
COPY src/ ./src/

# Install dependencies and build
RUN uv pip install --system --no-cache .

# Production runtime stage
FROM python:3.11-slim-bookworm

WORKDIR /app

# Copy installed packages from builder
COPY --from=builder /usr/local/lib/python3.11/site-packages /usr/local/lib/python3.11/site-packages
COPY --from=builder /app/src /app/src

# Create non-root user
RUN useradd -m -u 1000 appuser && \
    chown -R appuser:appuser /app

USER appuser

EXPOSE 8000

CMD ["uvicorn", "nftables_analyzer.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
