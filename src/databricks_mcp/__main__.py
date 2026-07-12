"""Command-line entry point."""

from __future__ import annotations

import logging

from databricks_mcp.config import Settings
from databricks_mcp.server import create_server

logger = logging.getLogger(__name__)


def main() -> None:
    """Start DatabricksMCP using validated environment configuration."""
    settings = Settings.from_env()
    logging.basicConfig(
        level=settings.log_level,
        format="%(asctime)s %(levelname)s %(name)s %(message)s",
    )
    server = create_server(settings)
    try:
        server.run(transport=settings.transport)
    except KeyboardInterrupt:
        logger.info("DatabricksMCP stopped")


if __name__ == "__main__":  # pragma: no cover
    main()
