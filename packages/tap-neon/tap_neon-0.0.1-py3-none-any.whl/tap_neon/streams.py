"""Stream type classes for tap-neon."""

from __future__ import annotations

from tap_neon.client import NeonStream


class Projects(NeonStream):
    """Projects stream."""

    name = "projects"
    path = "/projects"
    primary_keys = ["id"]
    replication_key = None
    swagger_ref = "Project"
    records_jsonpath = "$.projects[*]"

    def get_child_context(
        self,
        record: dict,
        context: dict | None,  # noqa: ARG002
    ) -> dict:
        """Return the child context for this record.

        Args:
            record: The record to get the child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"project_id": record["id"]}


class Operations(NeonStream):
    """Operations stream."""

    name = "operations"
    path = "/projects/{project_id}/operations"
    primary_keys = ["id"]
    replication_key = None
    swagger_ref = "Operation"
    records_jsonpath = "$.operations[*]"
    next_page_token_jsonpath = "$.pagination.cursor"  # noqa: S105
    parent_stream_type = Projects


class Branches(NeonStream):
    """Branches stream."""

    name = "branches"
    path = "/projects/{project_id}/branches"
    primary_keys = ["id"]
    replication_key = None
    swagger_ref = "Branch"
    records_jsonpath = "$.branches[*]"
    parent_stream_type = Projects

    def get_child_context(
        self,
        record: dict,
        context: dict | None,  # noqa: ARG002
    ) -> dict:
        """Add branch_id to context.

        Args:
            record: A record dict.
            context: A context dict.

        Returns:
            The updated context dict.
        """
        return {
            "project_id": record["project_id"],
            "branch_id": record["id"],
        }


class Databases(NeonStream):
    """Databases stream."""

    name = "databases"
    path = "/projects/{project_id}/branches/{branch_id}/databases"
    primary_keys = ["id"]
    replication_key = None
    swagger_ref = "Database"
    records_jsonpath = "$.databases[*]"
    parent_stream_type = Branches


class Roles(NeonStream):
    """Roles stream."""

    name = "roles"
    path = "/projects/{project_id}/branches/{branch_id}/roles"
    primary_keys = ["name"]
    replication_key = None
    swagger_ref = "Role"
    records_jsonpath = "$.roles[*]"
    parent_stream_type = Branches


class Endpoints(NeonStream):
    """Endpoints stream."""

    name = "endpoint"
    path = "/projects/{project_id}/endpoints"
    primary_keys = ["id"]
    replication_key = None
    swagger_ref = "Endpoint"
    records_jsonpath = "$.endpoints[*]"
    parent_stream_type = Projects
