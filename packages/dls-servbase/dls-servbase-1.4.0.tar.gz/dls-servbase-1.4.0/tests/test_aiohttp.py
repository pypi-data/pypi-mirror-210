import asyncio
import concurrent.futures
import functools
import logging
import multiprocessing
from urllib.parse import urlparse

import aiohttp
import aiohttp.web
import aiohttp.web_runner
import pytest

# Utilities.
from dls_utilpack.describe import describe

logger = logging.getLogger(__name__)


class TestAiohttp:
    """
    Test the aiohttp package directly, just to make sure it operations like we think it does.

    Does not import from any of the dls_servbase packages.

    Start a process for a server, and one for a client, and let them talk.

    """

    # ----------------------------------------------------------------------------------------
    def test_internet_sockest(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """ """

        multiprocessing.current_process().name = "main"

        failure_message = None

        try:
            # Run main in asyncio event loop.
            asyncio.run(
                self._main_coroutine(
                    constants,
                    "http://*:22132",
                    "http://localhost:22132",
                    output_directory,
                )
            )

        except Exception as exception:
            logger.exception("unexpected exception during the test", exc_info=exception)
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)

    # ----------------------------------------------------------------------------------------
    def test_unix_pipes(
        self,
        constants,
        logging_setup,
        output_directory,
    ):
        """ """

        multiprocessing.current_process().name = "main"

        failure_message = None

        try:
            # Run main in asyncio event loop.
            asyncio.run(
                self._main_coroutine(
                    constants,
                    f"{output_directory}/unix_socket",
                    f"{output_directory}/unix_socket",
                    output_directory,
                )
            )

        except Exception as exception:
            logger.exception("unexpected exception during the test", exc_info=exception)
            failure_message = str(exception)

        if failure_message is not None:
            pytest.fail(failure_message)

    # ----------------------------------------------------------------------------------------
    async def _main_coroutine(
        self, constants, server_endpoint, client_endpoint, output_directory
    ):
        """ """

        loop = asyncio.get_running_loop()

        self.__server_endpoint = server_endpoint
        self.__client_endpoint = client_endpoint

        with concurrent.futures.ProcessPoolExecutor() as pool:
            # Start a server and client in separate processes.
            server_executor = loop.run_in_executor(
                pool,
                functools.partial(self._server_process, constants, output_directory),
            )

            # Let the server process get truly started.
            # TODO: Remove sleep waiting for server process to start in test_31_aiohttp.
            await asyncio.sleep(0.5)
            client_executor = loop.run_in_executor(
                pool,
                functools.partial(self._client_process, constants, output_directory),
            )

            client_result = await client_executor
            logger.info(describe("client_result", client_result))

            server_result = await server_executor
            logger.info(describe("server_result", server_result))

    # ----------------------------------------------------------------------------------------
    def _server_process(
        self,
        constants,
        output_directory,
    ):
        """ """
        multiprocessing.current_process().name = "_server"

        try:
            logger.info("in _server_process")
            # raise RuntimeError("deliberate exception in _server_process")
            server_task = self._server_coroutine(constants, output_directory)
            server_task_result = asyncio.run(server_task)
            return server_task_result

        except Exception as exception:
            logger.exception("error in server process", exc_info=exception)
            return exception

    # ----------------------------------------------------------------------------------------
    async def _server_coroutine(
        self,
        constants,
        output_directory,
    ):
        """ """

        self._shutdown_event = asyncio.Event()

        try:
            logger.info("in _server_coroutine")
            web_app = aiohttp.web.Application()
            web_app.add_routes(
                [
                    aiohttp.web.get("/hello", self._handle_hello),
                    aiohttp.web.get("/shutdown", self._handle_shutdown),
                ]
            )

            self._runner = aiohttp.web.AppRunner(web_app)
            await self._runner.setup()

            if self.__server_endpoint.startswith("http"):
                parts = urlparse(self.__server_endpoint)
                site = aiohttp.web.TCPSite(self._runner, parts.hostname, parts.port)
            else:
                site = aiohttp.web.UnixSite(self._runner, self.__server_endpoint)
            await site.start()

            logger.info("awaiting shutdown event")
            await self._shutdown_event.wait()

            return None

        except Exception as exception:
            logger.exception("error in server coroutine", exc_info=exception)
            return exception

    # ----------------------------------------------------------------------------------------
    async def _handle_hello(self, request):
        try:
            logger.info("handling hello")
            # raise RuntimeError("deliberate exception in _handle_hello")
            response = aiohttp.web.Response(text="Hello, world")
            return response
        except Exception as exception:
            return self._componse_exception(exception)

    # ----------------------------------------------------------------------------------------
    async def _handle_shutdown(self, request):
        try:
            logger.info("handling shutdown")
            response = aiohttp.web.Response(status=200, text="ok")
            logger.info("setting shutdown event")
            self._shutdown_event.set()
            return response
        except Exception as exception:
            return self._componse_exception(exception)

    # ----------------------------------------------------------------------------------------
    def _componse_exception(self, exception):
        logger.exception("error ", exc_info=exception)
        return aiohttp.web.Response(status=500, body=str(exception).encode())

    # ----------------------------------------------------------------------------------------
    def _client_process(
        self,
        constants,
        output_directory,
    ):
        """ """
        multiprocessing.current_process().name = "_client"

        try:
            logger.info("in _client_process")

            # raise RuntimeError("deliberate exception in _client_process")
            client_task = self._client_coroutine(constants, output_directory)
            client_task_result = asyncio.run(client_task)
            return client_task_result

        except Exception as exception:
            logger.exception("error in client process", exc_info=exception)
            return exception

    # ----------------------------------------------------------------------------------------
    async def _client_coroutine(
        self,
        constants,
        output_directory,
    ):
        """ """

        try:
            logger.info("in _client_coroutine")
            # raise RuntimeError("deliberate exception in _client_coroutine")

            if self.__client_endpoint.startswith("http"):
                connector = None
                netloc = self.__client_endpoint
            else:
                connector = aiohttp.UnixConnector(path=self.__client_endpoint)
                netloc = "http://unixconnector"

            logger.info(f"client netloc is {netloc}")

            async with aiohttp.ClientSession(connector=connector) as session:
                try:
                    async with session.get(f"{netloc}/hello") as hello_response:
                        pass
                except Exception:
                    logger.exception("error in client call")

                async with session.get(f"{netloc}/shutdown"):
                    pass
                return hello_response.status
                # print(await resp.text())

        except Exception as exception:
            logger.exception("error in client coroutine", exc_info=exception)
            return exception
