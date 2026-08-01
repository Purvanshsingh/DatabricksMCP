"""Compute read pack: clusters, cluster events, policies, and node/version metadata."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from databricks_mcp.policy import RiskClass
from databricks_mcp.registry import ToolSpec

if TYPE_CHECKING:
    from databricks_mcp.registry import Registrar

NAME = "compute"


def register(registrar: Registrar) -> None:
    default_limit = registrar.settings.default_page_size
    limit_of = registrar.checked_limit

    @registrar.tool(
        ToolSpec(
            "list_clusters",
            NAME,
            RiskClass.READ,
            "List all-purpose and job clusters, bounded to the configured page size.",
        )
    )
    def list_clusters(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_clusters(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "get_cluster",
            NAME,
            RiskClass.READ,
            "Get the configuration and state of one cluster by id.",
        )
    )
    def get_cluster(cluster_id: str) -> dict[str, Any]:
        return registrar.service.get_cluster(cluster_id)

    @registrar.tool(
        ToolSpec(
            "list_cluster_events",
            NAME,
            RiskClass.READ,
            "List lifecycle events for one cluster, bounded to the page size.",
        )
    )
    def list_cluster_events(cluster_id: str, limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_cluster_events(cluster_id=cluster_id, limit=limit_of(limit))

    @registrar.tool(
        ToolSpec(
            "list_cluster_policies",
            NAME,
            RiskClass.READ,
            "List cluster policies, bounded to the configured page size.",
        )
    )
    def list_cluster_policies(limit: int = default_limit) -> list[dict[str, Any]]:
        return registrar.service.list_cluster_policies(limit=limit_of(limit))

    @registrar.tool(
        ToolSpec("get_cluster_policy", NAME, RiskClass.READ, "Get one cluster policy by id.")
    )
    def get_cluster_policy(policy_id: str) -> dict[str, Any]:
        return registrar.service.get_cluster_policy(policy_id)

    @registrar.tool(
        ToolSpec(
            "list_node_types",
            NAME,
            RiskClass.READ,
            "List available compute node types for the workspace.",
        )
    )
    def list_node_types() -> dict[str, Any]:
        return registrar.service.list_node_types()

    @registrar.tool(
        ToolSpec(
            "list_spark_versions",
            NAME,
            RiskClass.READ,
            "List available Databricks Runtime (Spark) versions.",
        )
    )
    def list_spark_versions() -> dict[str, Any]:
        return registrar.service.list_spark_versions()
