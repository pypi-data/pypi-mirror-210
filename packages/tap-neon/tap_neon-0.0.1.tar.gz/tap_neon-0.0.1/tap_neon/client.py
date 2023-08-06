"""REST client handling, including NeonStream base class."""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

from singer_sdk import RESTStream
from singer_sdk.authenticators import BearerTokenAuthenticator
from singer_sdk.helpers.jsonpath import extract_jsonpath
from singer_sdk.pagination import JSONPathPaginator

if TYPE_CHECKING:
    from requests import Response


class NeonCursorPaginator(JSONPathPaginator):
    """Cursor paginator for Neon API."""

    def has_more(self, response: Response) -> bool:
        """Return True if there are more pages to paginate.

        Args:
            response: The most recent response from the API.

        Returns:
            True if there are more pages to paginate.
        """
        cursor = next(extract_jsonpath(self._jsonpath, response.json()), None)
        if cursor == self.current_value and self.count > 1:
            return False
        return True


class NeonStream(RESTStream):
    """Neon Serverless Postgres stream class."""

    url_base = "https://console.neon.tech/api/v2"
    next_page_token_jsonpath = "$.next_page"  # noqa: S105

    swagger_ref: str

    @property
    def authenticator(self) -> BearerTokenAuthenticator:
        """Get an authenticator object.

        Returns:
            The authenticator instance for this REST stream.
        """
        token: str = self.config["api_key"]
        return BearerTokenAuthenticator.create_for_stream(
            self,
            token=token,
        )

    @property
    def http_headers(self) -> dict:
        """Return the http headers needed.

        Returns:
            A dictionary of HTTP headers.
        """
        return {
            "User-Agent": f"{self.tap_name}/{self._tap.plugin_version}",
            "Content-Type": "application/json",
        }

    def get_url_params(
        self,
        context: dict | None,  # noqa: ARG002
        next_page_token: Any | None,
    ) -> dict[str, Any]:
        """Get URL query parameters.

        Args:
            context: Stream sync context.
            next_page_token: Next offset.

        Returns:
            Mapping of URL query parameters.
        """
        params: dict = {}

        if self.next_page_token_jsonpath:
            params["limit"] = 100
            if next_page_token:
                params["cursor"] = next_page_token
        return params

    def get_new_paginator(self) -> NeonCursorPaginator:
        """Get a new paginator instance.

        Returns:
            A new paginator instance.
        """
        return NeonCursorPaginator(jsonpath=self.next_page_token_jsonpath)
