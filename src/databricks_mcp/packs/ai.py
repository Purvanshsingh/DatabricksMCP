"""AI read pack: Model Serving endpoints, Vector Search, and Genie spaces (read-only)."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "ai"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_serving_endpoints",
            NAME,
            RiskClass.READ,
            "List Model Serving endpoints, bounded to the configured page size.",
        )
    )
    def list_serving_endpoints(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_serving_endpoints(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_serving_endpoint",
            NAME,
            RiskClass.READ,
            "Get the configuration and state of one Model Serving endpoint by name.",
        )
    )
    def get_serving_endpoint(name: str) -> dict[str, Any]:
        return registrar.service.get_serving_endpoint(name)

    @registrar.tool(
        ToolSpec(
            "list_vector_search_endpoints",
            NAME,
            RiskClass.READ,
            "List Vector Search endpoints, bounded to the configured page size.",
        )
    )
    def list_vector_search_endpoints(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_vector_search_endpoints(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_vector_search_endpoint",
            NAME,
            RiskClass.READ,
            "Get one Vector Search endpoint by name.",
        )
    )
    def get_vector_search_endpoint(endpoint_name: str) -> dict[str, Any]:
        return registrar.service.get_vector_search_endpoint(endpoint_name)

    @registrar.tool(
        ToolSpec(
            "list_vector_search_indexes",
            NAME,
            RiskClass.READ,
            "List Vector Search indexes on an endpoint, bounded to the page size.",
        )
    )
    def list_vector_search_indexes(
        endpoint_name: str, limit: int = default_limit
    ) -> list[dict[str, Any]]:
        return registrar.service.list_vector_search_indexes(
            endpoint_name=endpoint_name, limit=limit_of(limit)
        )

    @registrar.tool(
        ToolSpec(
            "get_vector_search_index",
            NAME,
            RiskClass.READ,
            "Get one Vector Search index by its full name.",
        )
    )
    def get_vector_search_index(index_name: str) -> dict[str, Any]:
        return registrar.service.get_vector_search_index(index_name)

    @registrar.tool(
        ToolSpec(
            "list_genie_spaces", NAME, RiskClass.READ, "List Genie spaces available to the caller."
        )
    )
    def list_genie_spaces() -> dict[str, Any]:
        return registrar.service.list_genie_spaces()

    @registrar.tool(ToolSpec("get_genie_space", NAME, RiskClass.READ, "Get one Genie space by id."))
    def get_genie_space(space_id: str) -> dict[str, Any]:
        return registrar.service.get_genie_space(space_id)
