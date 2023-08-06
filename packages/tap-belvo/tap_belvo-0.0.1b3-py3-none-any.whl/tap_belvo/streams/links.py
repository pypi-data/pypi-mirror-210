"""Stream type classes for tap-belvo."""

from __future__ import annotations

from tap_belvo.client import BelvoStream


class Links(BelvoStream):
    """Links stream."""

    name = "links_links"
    path = "/api/links"
    primary_keys = ["id"]
    replication_key = "created_at"
    openapi_ref = "Link"

    def get_child_context(
        self,
        record: dict,
        context: dict | None,  # noqa: ARG002
    ) -> dict:
        """Return the child context.

        Args:
            record: The record to get the child context for.
            context: The parent context.

        Returns:
            The child context.
        """
        return {"link_id": record["id"]}


class Institutions(BelvoStream):
    """Institutions stream."""

    name = "links_institutions"
    path = "/api/institutions"
    primary_keys = ["id"]
    replication_key = None
    openapi_ref = "Institution"
