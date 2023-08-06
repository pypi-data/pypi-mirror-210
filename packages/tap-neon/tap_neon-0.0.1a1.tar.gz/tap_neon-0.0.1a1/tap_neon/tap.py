"""Neon Serverless Postgres tap class."""

from __future__ import annotations

from typing import TYPE_CHECKING

import requests
from singer_sdk import Stream, Tap
from singer_sdk import typing as th
from singer_sdk._singerlib import resolve_schema_references

from tap_neon import streams

if TYPE_CHECKING:
    from singer_sdk.streams import RESTStream

OPENAPI_URL = "https://dfv3qgd2ykmrx.cloudfront.net/api_spec/release/v2.json"
STREAMS: list[type[streams.NeonStream]] = [
    streams.Operations,
    streams.Projects,
    streams.Branches,
    streams.Endpoints,
    streams.Roles,
    streams.Databases,
]


class TapNeon(Tap):
    """Singer tap for Neon Serverless Postgres."""

    name = "tap-neon"

    config_jsonschema = th.PropertiesList(
        th.Property(
            "api_key",
            th.StringType,
            required=True,
            description="API Key for Neon Serverless Postgres",
        ),
        th.Property(
            "start_date",
            th.DateTimeType,
            description="Earliest datetime to get data from",
        ),
    ).to_dict()

    def get_openapi_schema(self) -> dict:
        """Retrieve Swagger/OpenAPI schema for this API.

        Returns:
            OpenAPI schema.
        """
        return requests.get(OPENAPI_URL, timeout=5).json()

    def discover_streams(self) -> list[Stream]:
        """Return a list of discovered streams.

        Returns:
            A list of Neon Serverless Postgres streams.
        """
        streams: list[RESTStream] = []
        openapi_schema = self.get_openapi_schema()

        for stream_type in STREAMS:
            schema = {"$ref": f"#/components/schemas/{stream_type.swagger_ref}"}
            schema["components"] = openapi_schema["components"]
            resolved_schema = resolve_schema_references(schema)
            streams.append(stream_type(tap=self, schema=resolved_schema))

        return sorted(streams, key=lambda x: x.name)
