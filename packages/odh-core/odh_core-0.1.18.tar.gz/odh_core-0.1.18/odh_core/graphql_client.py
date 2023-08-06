from gql import Client as gql_client
from gql.transport.aiohttp import AIOHTTPTransport
from graphql import DocumentNode
import logging

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


# # Tracelog for aiohttp
# # from: https://stackoverflow.com/a/64954315
# async def on_request_end(session, context, params):
#     trace_log = logging.getLogger("aiohttp.client")
#     trace_log.debug(
#         f"Request: {params.method} {params.url} "
#         f"Response: status:{params.response.status} {await params.response.text()}"
#     )

# trace_config = aiohttp.TraceConfig()
# trace_config.on_request_end.append(on_request_end)

# session = (
#     aiohttp.ClientSession(
#         base_url="https://graph.microsoft.com/",
#         headers=settings.jsonheaders,
#         trust_env=True,
#         # log all requests made by the session
#         trace_configs=[trace_config],
#     ),
# )


class GraphQLClient:
    """GraphQL client with session management

    .. todo::
        - Add support for trace logging

    """

    def __init__(
        self, url: str, headers: dict = None, ssl: bool = True, timeout: int = 10
    ):
        """Initialize GraphQL client

        Args:
            url (str): GraphQL server URL
            headers (dict, optional): HTTP headers to send with each request
            ssl (bool, optional): Verify SSL certificate
            timeout (int, optional): Timeout in seconds

        """
        self._client = gql_client(
            transport=AIOHTTPTransport(
                url=url,
                headers=headers,
                ssl=ssl,
                timeout=timeout,
            ),
            fetch_schema_from_transport=True,
        )
        self._session = None

    async def connect_async(self):
        self._session = await self._client.connect_async(reconnecting=True)
        log.info(f"Connected to GraphQL server: {self._client.transport.url}")

    async def close_async(self):
        await self._client.close_async()
        log.info(f"Connection closed to GraphQL server: {self._client.transport.url}")

    async def execute_async(self, query: DocumentNode, variable_values=None):
        """Execute a GraphQL query"""
        if not isinstance(query, DocumentNode):
            raise TypeError("query must be a gql object")

        if variable_values is None:
            result = await self._session.execute(query)
        else:
            result = await self._session.execute(query, variable_values)
        return result
