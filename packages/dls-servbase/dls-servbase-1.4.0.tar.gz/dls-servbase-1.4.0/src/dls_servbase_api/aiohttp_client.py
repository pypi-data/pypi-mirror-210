import asyncio
import copy
import json
import logging
import socket
import time
from urllib.parse import urlparse

import aiohttp

# Utilities.
from dls_utilpack.callsign import callsign
from dls_utilpack.describe import describe
from dls_utilpack.explain import explain, explain2
from dls_utilpack.import_class import import_classname_from_modulename

# Exceptions.
from dls_servbase_api.exceptions import (
    ClientConnectorError as DlsServbaseClientConnectorError,
)

logger = logging.getLogger(__name__)


# ------------------------------------------------------------------------------------------
class AiohttpClient:
    """
    Object representing a client to an aiohttp server.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, aiohttp_specification):
        self.__aiohttp_specification = copy.deepcopy(aiohttp_specification)

        if "client" not in self.__aiohttp_specification:
            self.__aiohttp_specification["client"] = "http://%s:%s" % (
                self.__aiohttp_specification.get("client_host", "unconfigured"),
                self.__aiohttp_specification.get("port", "unconfigured"),
            )

        self.__endpoint = self.__aiohttp_specification["client"]
        self._client_session = None

        # Set log level default to avoid unwanted messages.
        logging.getLogger("aiohttp").setLevel(
            aiohttp_specification.get("log_level", "WARNING")
        )

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return self.__aiohttp_specification["client"]

    # ----------------------------------------------------------------------------------------
    async def __is_client_connection_possible(self):
        """"""

        if self.__endpoint.startswith("http"):
            parts = urlparse(self.__endpoint)
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            result = sock.connect_ex((parts.hostname, parts.port))
            sock.close()
            # logger.debug(
            #     f"sock.connect_ex(({parts.hostname}, {parts.port})) result is {result}"
            # )
            return result == 0
        else:
            # TODO: Do proper check if client connection possible for unix pipe.
            await asyncio.sleep(0.100)
            return True

    # ----------------------------------------------------------------------------------------
    async def _establish_client_session(self):
        """"""

        if self._client_session is None:
            if self.__endpoint.startswith("http"):
                connector = None
                self.__client_netloc = self.__endpoint
            else:
                parts = urlparse(self.__endpoint)
                connector = aiohttp.UnixConnector(path=parts.path)
                self.__client_netloc = "http://unixconnector"

            self._client_session = aiohttp.ClientSession(connector=connector)

    # ----------------------------------------------------------------------------------------
    async def client_get_info(self):
        """"""
        await self._establish_client_session()

        async with self._client_session.get("/get_info") as response:
            return await response.json()

    # ----------------------------------------------------------------------------------------
    async def client_protocolj(self, request_object, cookies=None):
        """"""
        await self._establish_client_session()

        # logger.info(describe("request_object", request_object))

        try:
            async with self._client_session.post(
                f"{self.__client_netloc}/protocolj",
                json=request_object,
                cookies=cookies,
            ) as response:
                if response.status == 200:
                    response_json = await response.json()
                    if cookies is not None:
                        if response_json is None:
                            response_json = {}
                        response_json["__cookies"] = response.cookies
                    return response_json
                else:
                    text = await response.text()

                    exception_class = RuntimeError
                    exception_message = "server responded with status %d: %s" % (
                        response.status,
                        text,
                    )

                    try:
                        response_dict = json.loads(text)

                        if "exception" in response_dict:
                            qualname = response_dict["exception"].get("qualname")
                            exception_message = response_dict["exception"].get(
                                "message", "no message"
                            )
                            try:
                                modulename = ".".join(qualname.split(".")[:-1])
                                classname = qualname.split(".")[-1]
                                exception_class = import_classname_from_modulename(
                                    classname, modulename
                                )
                            except Exception:
                                exception_class = RuntimeError
                                exception_message = f"{qualname}: {exception_message}"
                    except Exception:
                        pass

                    raise exception_class(exception_message)
        except aiohttp.ClientConnectorError as exception:
            raise DlsServbaseClientConnectorError(
                explain(exception, f"connecting to {callsign(self)}")
            )

    # ----------------------------------------------------------------------------------------
    def _set_auth_headers(self, headers):
        """
        Put the proper authorization in the headers.
        """

        # Already authorization there?
        if "Authorization" in headers:
            return

        config = self.__aiohttp_specification.get("authorization")
        if config is None:
            return

        type = config.get("type")
        if type != "http_basic":
            raise RuntimeError(
                f'{callsign(self)} cannot understand configured authorization type "{type}"'
            )

        username = config.get("username")
        if username is None:
            raise RuntimeError(
                f"{callsign(self)} configured authorization does not contain username"
            )
        password = config.get("password")
        if password is None:
            raise RuntimeError(
                f"{callsign(self)} caonfigured authorization does not contain password"
            )

        auth = aiohttp.BasicAuth(username, password)

        headers["Authorization"] = auth.encode()

    # ----------------------------------------------------------------------------------------
    async def client_get_json(self, url, **kwargs):
        """"""
        await self._establish_client_session()

        if not url.startswith("/"):
            url = "/" + url
        url = f"{self.__client_netloc}{url}"

        headers = kwargs.get("headers", {})
        headers = copy.deepcopy(headers)
        headers["Accept"] = "application/json"

        # Put the proper authorization in the headers.
        self._set_auth_headers(headers)

        kwargs["headers"] = headers

        # logger.debug(describe(f"{callsign(self)} kwargs", kwargs))

        async with self._client_session.get(url, **kwargs) as response:

            if response.status != 200:
                content = await response.text()
                raise RuntimeError(
                    f"{url} error {response.status}: {response.reason}\n{content}"
                )

            content = await response.json()

            return content

    # ----------------------------------------------------------------------------------------
    async def client_get_csv(self, url, **kwargs):
        """"""
        await self._establish_client_session()

        if not url.startswith("/"):
            url = "/" + url
        url = f"{self.__client_netloc}{url}"

        headers = kwargs.get("headers", {})
        headers = copy.deepcopy(headers)
        headers["Accept"] = "text/csv"
        kwargs["headers"] = headers
        logger.debug(describe("kwargs", kwargs))

        async with self._client_session.get(url, **kwargs) as response:
            logger.info(f"response.url {response.url}")

            if response.status != 200:
                content = await response.text()
                raise RuntimeError(
                    f"{url} error {response.status}: {response.reason}\n{content}"
                )

            content = await response.text()

            return content

    # ----------------------------------------------------------------------------------------
    async def client_get_file(self, url):
        """"""
        await self._establish_client_session()

        if not url.startswith("/"):
            url = "/" + url
        url = f"{self.__client_netloc}{url}"

        async with self._client_session.get(url) as response:

            if response.status != 200:
                raise RuntimeError(f"{url} error {response.status}: {response.reason}")

            if response.headers["Content-Type"] in (
                "text/plain"
                "text/html"
                "text/css"
                "application/javascript"
                "application/json"
            ):

                # Read body and decode into text.
                content = await response.text("utf-8")
            else:
                content = await response.read()

            return content

    # ----------------------------------------------------------------------------------------
    async def client_report_health(self):
        """"""
        await self._establish_client_session()

        try:
            response = await self.client_get_json("report_health")
        except Exception as exception:
            logger.error(
                explain2(exception, "[BADHEALTH] contacting server"), exc_info=exception
            )
            response = {"exception": str(exception)}

        return response

    # ----------------------------------------------------------------------------------------
    async def client_shutdown(self):
        """"""

        if not await self.__is_client_connection_possible():
            await self.close_client_session()
            return {"message": "no previous instance to shutdown"}

        await self._establish_client_session()

        time_zero = time.time()
        try:
            # TODO: Check response from shutdown, whatever it might be.
            await self._client_session.get(f"{self.__client_netloc}/shutdown")

            logger.debug(
                f"[DISSHU] client has requested {callsign(self)} server shutdown"
            )

            max_seconds = 5.0
            nap_seconds = 0.050
            timeout_time = time.time() + max_seconds

            while True:
                # Quit looping when server has closed its end of the socket.
                is_client_connection_possible = (
                    await self.__is_client_connection_possible()
                )
                if not is_client_connection_possible:
                    break

                # Too much time has passed while waiting for server to shut down?
                if time.time() > timeout_time:
                    raise RuntimeError(
                        f"remote server did not shut down within {max_seconds} seconds"
                    )

                logger.debug(
                    f"[DISSHU] waiting for {callsign(self)} server shutdown, napping {nap_seconds}"
                )

                # Small sleep after sending shutdown command lets the server really shut down.
                # TODO: Detect when server shutdown is complete.
                await asyncio.sleep(nap_seconds)
        finally:
            await self.close_client_session()

        return {
            # Let caller know that another process had existed.
            "had_existed": True,
            "message": "previous instance shutdown after %0.3f seconds"
            % (time.time() - time_zero),
        }

    # ----------------------------------------------------------------------------------------
    async def open_client_session(self):
        """"""

        await self._establish_client_session()

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""

        if self._client_session is not None:
            # logger.debug("closing client session")

            await self._client_session.close()
            self._client_session = None
