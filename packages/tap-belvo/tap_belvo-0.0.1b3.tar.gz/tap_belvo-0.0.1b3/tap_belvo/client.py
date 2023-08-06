"""REST client handling, including BelvoStream base class."""

from __future__ import annotations

from abc import ABCMeta, abstractmethod
from typing import TYPE_CHECKING, Any
from urllib.parse import ParseResult, parse_qsl

from requests_cache import install_cache
from singer_sdk import RESTStream
from singer_sdk._singerlib import resolve_schema_references
from singer_sdk.authenticators import BasicAuthenticator
from singer_sdk.helpers._typing import is_date_or_datetime_type
from singer_sdk.pagination import BaseHATEOASPaginator

from tap_belvo.openapi import load_openapi

if TYPE_CHECKING:
    from requests import Response


PAGE_SIZE = 1000

install_cache("tap_belvo_cache", backend="sqlite", expire_after=3600)


class BelvoPaginator(BaseHATEOASPaginator):
    """Belvo API paginator class."""

    def get_next_url(self, response: Response) -> str | None:
        """Get the next URL from the response.

        Args:
            response: The response object.

        Returns:
            The next URL.
        """
        return response.json().get("next")


class BelvoStream(RESTStream, metaclass=ABCMeta):
    """Belvo stream class."""

    records_jsonpath = "$.results[*]"  # Or override `parse_response`.

    @property
    def url_base(self) -> str:
        """Return the URL base property.

        Returns:
            str: The URL base.
        """
        return self.config["base_url"]

    @property
    def authenticator(self) -> BasicAuthenticator:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        username = self.config["secret_id"]
        password = self.config["password"]

        return BasicAuthenticator.create_for_stream(
            self,
            username=username,
            password=password,
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        headers = {}
        headers["User-Agent"] = f"{self.tap_name}/{self._tap.plugin_version}"
        return headers

    def get_new_paginator(self) -> BelvoPaginator:
        """Get a new paginator instance.

        Returns:
            A new paginator instance.
        """
        return BelvoPaginator()

    def get_url_params(
        self,
        context: dict | None,
        next_page_token: ParseResult | None,
    ) -> dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        params: dict[str, Any] = {
            "page": 1,
            "page_size": PAGE_SIZE,
        }

        if next_page_token:
            params.update(parse_qsl(next_page_token.query))

        if self.replication_key:
            start_date = self.get_starting_timestamp(context)
            if start_date:
                params[f"{self.replication_key}__gte"] = start_date.date()

        return params

    @property
    def is_timestamp_replication_key(self) -> bool:
        """Check is replication key is a timestamp.

        Developers can override to `True` in order to force this value, although this
        should not be required in most use cases since the type can generally be
        accurately detected from the JSON Schema.

        Returns:
            True if the stream uses a timestamp-based replication key.
        """
        if not self.replication_key:
            return False
        type_dict = self.schema.get("properties", {}).get(self.replication_key)
        return is_date_or_datetime_type(type_dict)

    def _resolve_openapi_ref(self) -> dict[str, Any]:
        schema = {"$ref": f"#/components/schemas/{self.openapi_ref}"}
        openapi = load_openapi()
        schema["components"] = openapi["components"]
        return resolve_schema_references(schema)

    @property
    def schema(self) -> dict[str, Any]:
        """Return the schema for this stream.

        Returns:
            The schema for this stream.
        """
        return self._resolve_openapi_ref()

    @property
    @abstractmethod
    def openapi_ref(self) -> str:
        """Return the OpenAPI component name for this stream.

        Returns:
            The OpenAPI reference for this stream.
        """
        ...
