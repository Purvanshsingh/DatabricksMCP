# syntax=docker/dockerfile:1
FROM python:3.12-slim AS builder

ENV PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1

WORKDIR /build
COPY pyproject.toml README.md LICENSE ./
COPY src ./src
RUN python -m pip wheel --wheel-dir /wheels .

FROM python:3.12-slim AS runtime

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATABRICKS_MCP_TRANSPORT=streamable-http \
    DATABRICKS_MCP_HOST=0.0.0.0 \
    DATABRICKS_MCP_PORT=8000

RUN groupadd --system databricks-mcp \
    && useradd --system --gid databricks-mcp --create-home databricks-mcp

COPY --from=builder /wheels /wheels
RUN python -m pip install --no-cache-dir /wheels/* \
    && rm -rf /wheels

USER databricks-mcp
EXPOSE 8000
ENTRYPOINT ["databricks-mcp"]
