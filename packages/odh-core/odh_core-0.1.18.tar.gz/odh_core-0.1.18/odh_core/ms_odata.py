import logging
from urllib.parse import urlsplit, urlunsplit
from datetime import datetime, timezone
from jose import jwt
import aiohttp
import asyncio

log = logging.getLogger(__name__)
log.addHandler(logging.NullHandler())


class MicrosoftException(Exception):
    """General Microsoft Exception, Transport error, server error, etc."""

    pass


class GraphError(Exception):
    """Exception to catch Microsoft Graph API errors, user code did something wrong"""

    pass


def relative_url(url: str) -> str:
    """Convert absolute url to relative url"""
    return urlunsplit(urlsplit(url)._replace(scheme="", netloc=""))


class ms_odata:
    def __init__(
        self,
        CLIENT_ID: str,
        TENANT_ID: str,
        CLIENT_SECRET: str,
        scope: str = "https://graph.microsoft.com/.default",
        b2c=False,
        base_url="https://graph.microsoft.com/",
    ) -> None:
        self.CLIENT_ID = CLIENT_ID
        self.TENANT_ID = TENANT_ID
        self.CLIENT_SECRET = CLIENT_SECRET
        self.scope = scope
        self.b2c = b2c
        self.token = {}
        self.session = aiohttp.ClientSession(base_url=base_url, trust_env=True)

    async def get_token(self):
        """Get the token from Microsoft Graph"""

        # TENANT_ID can be guid or domain name (e.g. contoso.onmicrosoft.com)
        url = f"https://login.microsoftonline.com/{self.TENANT_ID}/oauth2/v2.0/token"

        # Set the headers
        headers = {"Content-Type": "application/x-www-form-urlencoded"}

        # Set the payload

        payload = {
            "grant_type": "client_credentials",
            "client_id": self.CLIENT_ID,
            "client_secret": self.CLIENT_SECRET,
            # msgraph only needs this scope for now
            "scope": self.scope,
        }

        # Make the request to get the token
        # TODO: remove the session
        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, data=payload) as resp:
                token_json = await resp.json()
                if not resp.ok:
                    raise MicrosoftException(
                        f"Request to {url} failed with {resp.status}"
                    )
                # decode jwt token to AzureADToken
                tokendecoded = jwt.get_unverified_claims(token_json["access_token"])

                self.token["access_token"] = token_json["access_token"]
                self.token["expires_on"] = datetime.fromtimestamp(
                    tokendecoded["exp"], tz=timezone.utc
                )
                self.token["not_before"] = datetime.fromtimestamp(
                    tokendecoded["nbf"], tz=timezone.utc
                )
                self.token["resource"] = tokendecoded["aud"]

                log.info(
                    f'Claimed new token, expires on {self.token["expires_on"]},'
                    f" for {self.TENANT_ID}"
                )

    async def update_token_header(self):
        # TODO: merge this in to get_token
        await self.get_token()
        # create a session with required headers and retry policy

        # save the access token in settings object?

        self.session.headers.update(
            {
                "Authorization": f'Bearer {self.token["access_token"]}',
                "Content-Type": "application/json",
                "Accept": "application/json",
            }
        )

    async def get_one(
        self,
        resource: str,
        filter: str = None,
        # add support to have str och obj as input
        # have default select based on what resource it is
        expand: str = None,
        select: str = None,
        deltaLink: str = None,
        nextLink: str = None,
        endpoint: str = "v1.0",
    ):
        """Function to do Odata querys against Microsfts Graph API
        to use delta queries call a /delta resource. @odata.deltaLink will be
        returned as part of the response and has to be set un subsequent calls.
        If the initial query retuns nextLink, the link will be followed and complete
        data returned

        """
        request_retry = 0
        while request_retry < 5:
            url = None
            try:
                # deltalink and nextlink are absolute url and can't base_url
                # per odata spec domain can't be changed
                if deltaLink:
                    url = relative_url(deltaLink)
                elif nextLink:
                    url = relative_url(nextLink)
                else:
                    url = f"/{endpoint}/{resource}"
                    parameters = []
                    if filter:
                        parameters.append(f"$filter={filter}")
                    if select:
                        parameters.append(f"$select={select}")
                    if expand:
                        parameters.append(f"$expand={expand}")
                    if parameters:
                        url = f"{url}?{'&'.join(parameters)}"
                # make the request
                async with self.session.get(url) as resp:
                    # if we get 200, return the data
                    if resp.status == 200:
                        return await resp.json()
                    # if we get 401, refresh the token and retry
                    elif resp.status == 401:
                        # refresh the token
                        await self.update_token_header()
                        request_retry += 1
                    # if we get 404, return empty
                    elif resp.status == 404:
                        return {}
                    # if we get 429, wait and retry
                    elif resp.status == 429:
                        delay = float(resp.headers["retry-after"])
                        log.info(
                            f"Request to {url} failed with 429, retrying in {delay} seconds"
                        )
                        await asyncio.sleep(delay)
                        request_retry += 1
                    # if we get 503, wait and retry
                    elif resp.status == 503:
                        delay = 5
                        log.info(
                            f"Request to {url} failed with 503, retrying in {delay} seconds"
                        )
                        await asyncio.sleep(delay)
                        request_retry += 1
                    # if we get anything else, log it and return empty
                    else:
                        log.error(
                            f"Request to {url} failed with {resp.status} {resp.reason}"
                        )
                        return {}
            except aiohttp.ClientError as e:
                log.error(f"Request to {url} failed with {e}")
                return {}

    async def get_all(
        self,
        resource: str,
        filter: str = None,
        expand: str = None,
        select: str = None,
        endpoint: str = "v1.0",
        deltaLink: str = None,
    ):
        nextLink = None
        # get the odata
        odata_records = []
        while True:
            graphdata = await self.get_one(
                resource=resource,
                select=select,
                filter=filter,
                expand=expand,
                nextLink=nextLink,
                deltaLink=deltaLink,
                endpoint=endpoint,
            )
            # if we get an empty response, return
            if not graphdata:
                return odata_records
            # if we get a single response return it
            if graphdata.get("value") is None:
                return graphdata
            # if we get several responses, add the values to the list
            for value in graphdata["value"]:
                odata_records.append(value)
            # if we get an empty response, return
            if "@odata.nextLink" in graphdata:
                nextLink = graphdata["@odata.nextLink"]
            elif "@odata.deltaLink" in graphdata:
                deltaLink = graphdata["@odata.deltaLink"]
                return odata_records, deltaLink
            else:
                return odata_records, None

    # # not working yet
    # async def get(
    #     self,
    #     resource: str,
    #     filter: str = None,
    #     expand: str = None,
    #     select: str = None,
    #     endpoint: str = "v1.0",
    #     deltaLink: str = None,
    # ):
    #     raise NotImplementedError
    #     nextLink = None
    #     # # get the odata
    #     # odata_records = []
    #     while True:
    #         graphdata = await self.get_one(
    #             resource=resource,
    #             select=select,
    #             filter=filter,
    #             expand=expand,
    #             deltaLink=deltaLink,
    #             endpoint=endpoint,
    #         )
    #         # if we get an empty response, stop
    #         if not graphdata:
    #             raise StopAsyncIteration
    #             # return odata_records
    #         # if we get a single response return it
    #         if graphdata.get("value") is None:
    #             yield graphdata
    #         # if we get several responses, add the values to the list
    #         for value in graphdata["value"]:
    #             yield value
    #             # odata_records.append(value)

    #         # if we get a nextLink, follow it
    #         if "@odata.nextLink" in graphdata:
    #             nextLink = graphdata["@odata.nextLink"]

    #         elif "@odata.deltaLink" in graphdata:
    #             deltaLink = graphdata["@odata.deltaLink"]
    #             # yield records
    #             breakpoint()
    #         #     return odata_records, deltaLink
    #         # else:
    #         #     return odata_records, None

    async def post(
        self,
        resource: str,
        data: dict,
        endpoint: str = "v1.0",
    ):
        """Handles retry logic and token refresh for microsoft graph post request

        Post data to the graph using the odata protocol

        https://learn.microsoft.com/en-us/graph/errors

        """
        request_retry = 0
        while request_retry < 5:
            # make the request
            url = f"/{endpoint}/{resource}"
            async with self.session.post(url=url, data=data) as resp:
                if resp.status == 204:
                    resp_json = {}
                    return resp_json
                # if we get 200, return the data
                if resp.status >= 200 and resp.status < 300:
                    resp_json = await resp.json()
                    if not resp.ok:
                        log.error(f'graph error: {resp_json["error"]["message"]}')
                        log.debug(resp_json)
                    return resp_json
                # if we get 401, refresh the token and retry
                elif resp.status == 401:
                    # refresh the token
                    await self.update_token_header()
                    request_retry += 1

                # if we get 400, raise an error, something is wrong get user code to handle it
                elif resp.status == 400:
                    resp_json = await resp.json()
                    raise GraphError(resp_json["error"]["message"])

                # if we get 429, wait and retry
                elif resp.status == 429:
                    delay = float(resp.headers["retry-after"])
                    log.info(
                        f"Request to {url} failed with 429, retrying in {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    request_retry += 1
                # if we get 503, wait and retry
                elif resp.status == 503:
                    delay = float(resp.headers["retry-after"])
                    log.info(
                        f"Request to {url} failed with 503, retrying in {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    request_retry += 1
                # if we get anything else, log it and return empty
                else:
                    resp_json = await resp.json()
                    log.debug(resp_json)
                    log.error(
                        f"Request to {url} failed with {resp.status} {resp.reason}"
                    )
                    return {}

    async def delete(
        self,
        resource: str,
        endpoint: str = "v1.0",
    ):
        """Handles retry logic and token refresh for microsoft graph post request

        Delete data from the graph using the odata protocol

        https://learn.microsoft.com/en-us/graph/errors

        """
        request_retry = 0
        while request_retry < 5:
            # make the request
            url = f"/{endpoint}/{resource}"
            async with self.session.delete(url=url) as resp:
                if resp.status == 204:
                    resp_json = {}
                    return resp_json
                # if we get 200, return the data
                if resp.status >= 200 and resp.status < 300:
                    resp_json = await resp.json()
                    if not resp.ok:
                        log.error(f'graph error: {resp_json["error"]["message"]}')
                        log.debug(resp_json)
                    return resp_json
                # if we get 401, refresh the token and retry
                elif resp.status == 401:
                    # refresh the token
                    await self.update_token_header()
                    request_retry += 1

                # if we get 400, raise an error, something is wrong get user code to handle it
                elif resp.status == 400:
                    resp_json = await resp.json()
                    raise GraphError(resp_json["error"]["message"])

                # if we get 429, wait and retry
                elif resp.status == 429:
                    delay = float(resp.headers["retry-after"])
                    log.info(
                        f"Request to {url} failed with 429, retrying in {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    request_retry += 1
                # if we get 503, wait and retry
                elif resp.status == 503:
                    delay = float(resp.headers["retry-after"])
                    log.info(
                        f"Request to {url} failed with 503, retrying in {delay} seconds"
                    )
                    await asyncio.sleep(delay)
                    request_retry += 1
                # if we get anything else, log it and return empty
                else:
                    resp_json = await resp.json()
                    log.debug(resp_json)
                    log.error(
                        f"Request to {url} failed with {resp.status} {resp.reason}"
                    )
                    return {}
