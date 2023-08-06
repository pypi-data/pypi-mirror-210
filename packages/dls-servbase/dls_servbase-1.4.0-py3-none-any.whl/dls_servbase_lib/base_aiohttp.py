import asyncio
import copy
import json
import logging
import multiprocessing
import os
import socket
import threading
import time
import uuid
from urllib.parse import urlparse

import aiohttp
import aiohttp.web
import aiohttp.web_runner
from dls_logformatter.functions import list_exception_causes
from dls_mainiac_lib.mainiac import Mainiac
from dls_multiconf_lib.multiconfs import multiconfs_get_default, multiconfs_has_default
from dls_utilpack.callsign import callsign
from dls_utilpack.explain import explain
from dls_utilpack.global_signals import global_sigint
from dls_utilpack.modify_process_title import modify_process_title
from dls_utilpack.qualname import qualname
from dls_utilpack.search_file import SearchFileNotFound, search_file

from dls_servbase_api.aiohttp_client import AiohttpClient  # noqa: I001
from dls_servbase_api.constants import Keywords  # noqa: I001
from dls_servbase_lib.cookies.cookies import Cookies

logger = logging.getLogger(__name__)


class Opaque:
    def __init__(self):
        self.cookies = Cookies(name="http request cookies")
        pass


# ------------------------------------------------------------------------------------------
class BaseAiohttp:
    """
    Object representing a a process which receives requests from aiohttp.
    """

    # ----------------------------------------------------------------------------------------
    def __init__(self, aiohttp_specification, calling_file=None):
        self.__aiohttp_specification = copy.deepcopy(aiohttp_specification)

        # Make sure there is a search_paths in the spedcification.
        search_paths = self.__aiohttp_specification.get("search_paths")
        if search_paths is None:
            self.__aiohttp_specification["search_paths"] = []

        # Caller's filename is presented?
        if calling_file is not None:
            # Search in html in the caller's filename's parent.
            self.__aiohttp_specification["search_paths"].append(
                f"{os.path.dirname(calling_file)}/html"
            )

        if "server" not in self.__aiohttp_specification:
            self.__aiohttp_specification["server"] = "http://%s:%s" % (
                self.__aiohttp_specification.get("server_host", "unconfigured"),
                self.__aiohttp_specification.get("port", "unconfigured"),
            )

        self.__callsign_url = self.__aiohttp_specification.get("server")
        if self.__callsign_url is None:
            self.__callsign_url = "http://%s:%s" % (
                self.__aiohttp_specification.get("server_host", "unconfigured"),
                self.__aiohttp_specification.get("port", "unconfigured"),
            )

        self.__callsign_url = self.__callsign_url.replace("*", socket.gethostname())

        # Build a client which can talk to this server.
        self.__aiohttp_client = AiohttpClient(self.__aiohttp_specification)

        self.__process2 = None
        self.__up_event2 = multiprocessing.Event()
        self.__up_event3 = asyncio.Event()

        # In the case where we are started as a process, we will use an new event loop of our own.
        self.owned_event_loop2 = None

        self.__thread3 = None

        # Event set when shutdown requested by remote request.
        self._shutdown_event = asyncio.Event()

        self.__thread = None
        self.__app_runner = None

        # Set log level default to avoid unwanted messages.
        logging.getLogger("aiohttp").setLevel(
            aiohttp_specification.get("log_level", "WARNING")
        )

        # We provide cookie services to our deriving classes.
        if "cookie_specification" in self.__aiohttp_specification:
            self.__cookie_specification = self.__aiohttp_specification[
                "cookie_specification"
            ]
        else:
            self.__cookie_specification = None

        # Some things for the health report.
        self.__protocolj_count = 0
        self.__file_count = 0
        self.__filestore_count = 0
        self.__time_started = time.time()

    # ----------------------------------------------------------------------------------------
    def callsign(self):
        """"""
        return self.__callsign_url

    # ----------------------------------------------------------------------------------------
    async def start_process(self):
        """"""

        self.__process2 = multiprocessing.Process(
            target=self.prepare_to_activate_process,
        )
        self.__process2.start()
        logger.debug(f"[DISSHU] {callsign(self)} pid {self.__process2.pid} is started")
        # TODO: Make maximum wait time for start_process event to be configurable.
        timeout = 30.0
        naptime = 0.25
        time0 = time.time()
        while time.time() - time0 < timeout:
            if self.__up_event2.is_set():
                return
            if not self.__process2.is_alive():
                raise RuntimeError(
                    f"process for {callsign(self)} died without setting up_event"
                )
            await asyncio.sleep(naptime)

        raise RuntimeError(
            f"process for {callsign(self)} did not set up_event within timeout {timeout} seconds"
        )

    # ----------------------------------------------------------------------------------------
    async def is_process_started(self):
        """"""

        return self.__process2 is not None

    # ----------------------------------------------------------------------------------------
    async def is_process_alive(self):
        """"""

        if self.__process2 is None:
            raise RuntimeError(f"{callsign(self)} has no process defined for it")

        is_alive = self.__process2.is_alive()

        # state = "alive" if is_alive else "dead"

        # logger.debug(f"[DISSHU] {callsign(self)} pid {self.__process2.pid} is {state}")

        return is_alive

    # ----------------------------------------------------------------------------------------
    def prepare_to_activate_process(self):
        """"""

        try:
            if multiconfs_has_default():
                dls_servbase_multiconf = multiconfs_get_default()

                # ---------------------------------------------------------------------
                # Multiconf must provide logging settings.
                logging_settings = dls_servbase_multiconf.require("logging_settings")

                # Remove existing handlers which may have been inherited from a fork.
                handlers = list(logging.getLogger().handlers)
                for handler in handlers:
                    logging.getLogger().removeHandler(handler)

                # Make a dummy mainiac and use it to configure logging.
                # Some loggers need to connect to logging servers in the new process.
                mainiac = Mainiac(callsign(self))
                mainiac.configure_logging(logging_settings)

                # ---------------------------------------------------------------------
                # We need special method for mpqueue since it is a multiprocessing object.
                # logging_mpqueue = dls_servbase_multiconf.get_logging_mpqueue()
                # if logging_mpqueue is not None:
                #     # Remove existing handlers.
                #     handlers = list(logging.getLogger().handlers)
                #     for handler in handlers:
                #         logging.getLogger().removeHandler(handler)
                #     mpqueue_handler = logging.handlers.QueueHandler(logging_mpqueue)
                #     mpqueue_handler.setLevel(logging.DEBUG)
                #     # Let logging write custom formatted messages to stdout.
                #     # This will format the full stack trace in the current interpreter.
                #     # So the queue listener has no opportunity to prefer a format like "bare" or "short".
                #     # TODO: Improve logform formatting options when using mpqueue.
                #     mpqueue_handler.setFormatter(DlsLogformatter(type="long"))
                #     logging.getLogger().handlers = []
                #     logging.getLogger().addHandler(mpqueue_handler)
                # else:
                #     logger.debug("[MPQLOG] no mpqueue")
            else:
                logger.debug("[MPQLOG] no multiconf")

        except Exception as exception:
            logger.exception(
                callsign(
                    self,
                    explain(exception, "preparing to activate process"),
                ),
                exc_info=exception,
            )

        # Call abstract method provided by the overriding class.
        self.activate_process()

    # ----------------------------------------------------------------------------------------
    def activate_process_base(self):
        """"""

        try:
            # Change our title as it appears in "ps ax" and "top".
            modify_process_title(callsign(self))

            # Activate the signal handling.
            global_sigint.activate()

            self.owned_event_loop2 = asyncio.new_event_loop()
            asyncio.set_event_loop(self.owned_event_loop2)
            coro_future = self.activate_coro()
            self.owned_event_loop2.run_until_complete(coro_future)

            # Now we got a server running we can allow the parent process to continue.
            self.__up_event2.set()

            self.owned_event_loop2.run_forever()

        except Exception as exception:
            logger.exception("exception in process", exc_info=exception)

        logger.debug(f"[DISSHU] {callsign(self)} pid {os.getpid()} has quit")

    # ----------------------------------------------------------------------------------------
    async def start_thread(self):
        """"""

        loop = asyncio.get_event_loop()
        self.__thread3 = threading.Thread(target=self.activate_thread, args=(loop,))
        self.__thread3.start()
        await self.__up_event3.wait()

    # ----------------------------------------------------------------------------------------
    def activate_thread_base(self, loop):
        """
        This is called from each server's activate_thread() method.
        """

        try:
            # Activate the server.
            future = asyncio.run_coroutine_threadsafe(self.activate_coro(), loop)

            # Wait for the activation to complete.
            future.result()

            # Now we got a server running we can allow the caller to continue.
            loop.call_soon_threadsafe(self.__up_event3.set)

        except Exception as exception:
            logger.exception("exception in thread", exc_info=exception)

    # ----------------------------------------------------------------------------------------
    async def activate_coro_base(self, route_tuples=[]):
        """
        This is called from each server's activate_coro() method.
        """
        try:
            # Shut down any existing servers.
            result = await self.client_shutdown()

            if result.get("had_existed", False):
                logger.info(f"we have shut down an existing process {callsign(self)}")
            else:
                logger.debug(f"[AUTSHUT] {callsign(self)} {result['message']}")

            web_app = aiohttp.web.Application()

            # TODO: Make the route_tuples in base_aiohttp specific to each server in question.
            routes = [
                aiohttp.web.get("/shutdown", self._route_shutdown),
                aiohttp.web.get("/report_health", self._route_report_health),
                aiohttp.web.post("/protocolj", self._route_protocolj),
                aiohttp.web.get(
                    "/filestore/{filestore_path:.*}", self._route_get_filestore
                ),
                aiohttp.web.get("/{url:.*}", self._route_get_file),
            ]

            # Caller can give extra routes like this:
            # route_tuples = [("post", "submit", self._route_submit)]

            for route_tuple in route_tuples:
                if route_tuple[0] == "get":
                    routes.append(
                        aiohttp.web.get("/%s" % (route_tuple[1]), route_tuple[2])
                    )
                elif route_tuple[0] == "post":
                    routes.append(
                        aiohttp.web.post("/%s" % (route_tuple[1]), route_tuple[2])
                    )

            web_app.add_routes(routes)

            self.__app_runner = aiohttp.web.AppRunner(web_app)

            await self.__app_runner.setup()

            endpoint = self.__aiohttp_specification["server"]
            if endpoint.startswith("http"):
                parts = urlparse(endpoint)
                site = aiohttp.web.TCPSite(
                    self.__app_runner, parts.hostname, parts.port
                )
            else:
                parts = urlparse(endpoint)
                site = aiohttp.web.UnixSite(self.__app_runner, parts.path)

            await site.start()
        except Exception as exception:
            raise RuntimeError(
                explain(exception, f"exception starting {callsign(self)} site")
            )

    # ----------------------------------------------------------------------------------------
    async def base_direct_shutdown(self):
        """"""
        # If we were started via process, we will need to stop our own event loop.
        if self.owned_event_loop2 is not None:
            logger.debug(
                f"[DISSHU] directly shutting down {callsign(self)} owned event loop on pid {os.getpid()}"
            )

            try:
                self.owned_event_loop2.stop()

            except Exception as exception:
                raise RuntimeError(callsign(self, explain(exception, "shutting down")))

        elif self.__app_runner is not None:
            logger.debug(
                f"[DISSHU] directly shutting down {callsign(self)} by awaiting self.__app_runner.cleanup()"
            )
            await self.__app_runner.cleanup()

        # Set event which will cause server to shutdown.
        self._shutdown_event.set()

    # ----------------------------------------------------------------------------------------
    async def wait_for_shutdown(self):
        """"""
        try:
            await self._shutdown_event.wait()

        except Exception as exception:
            raise RuntimeError("exception while waiting for shutdown") from exception

    # ------------------------------------------------------------------------------------------
    # Handle request to get static file.
    async def _route_get_file(self, request):
        try:
            # Stuff for the health report.
            self.__file_count += 1

            # logger.info(f"request.path is {request.path}")

            # Filename from the url line.
            filename = request.path

            search_paths = self.__aiohttp_specification.get("search_paths", [])
            try:
                absolute = search_file(search_paths, filename)
            except SearchFileNotFound as exception:
                response = aiohttp.web.Response(
                    status=404, reason=str(exception), text=str(exception)
                )
                return response

            suffix = os.path.splitext(absolute)[1]

            if suffix == ".html":
                content_type = "text/html"
            elif suffix == ".css":
                content_type = "text/css"
            elif suffix == ".js":
                content_type = "application/javascript"
            elif suffix == ".json":
                content_type = "application/json"
            elif suffix == ".png":
                content_type = "image/png"
            elif suffix == ".jpg":
                content_type = "image/jpg"
            else:
                content_type = "application/octet-stream"

            headers = {"Content-Type": content_type}

            response = aiohttp.web.FileResponse(absolute, headers=headers)

            return response
        except Exception as exception:
            return self._compose_standard_exception(exception)

    # ------------------------------------------------------------------------------------------
    # Handle request to get file from filestore.
    async def _route_get_filestore(self, request):
        try:
            # Stuff for the health report.
            self.__filestore_count += 1

            absolute = "/" + request.match_info["filestore_path"].strip("/")

            suffix = os.path.splitext(absolute)[1]

            if suffix == ".html":
                content_type = "text/html; charset=utf-8"
            elif suffix == ".log":
                content_type = "text/plain; charset=utf-8"
            elif suffix == ".stdout":
                content_type = "text/plain; charset=utf-8"
            elif suffix == ".stderr":
                content_type = "text/plain; charset=utf-8"
            elif suffix == ".txt":
                content_type = "text/plain; charset=utf-8"
            elif suffix == ".css":
                content_type = "text/css; charset=utf-8"
            elif suffix == ".csv":
                content_type = "text/csv; charset=utf-8"
            elif suffix == ".yml" or suffix == ".yaml":
                content_type = "application/x-yaml"
            elif suffix == ".json":
                content_type = "application/json"
            elif suffix == ".png":
                content_type = "image/png"
            elif suffix == ".gif":
                content_type = "image/gif"
            elif suffix == ".jpg":
                content_type = "image/jpg"
            else:
                content_type = "application/octet-stream"

            headers = {"Content-Type": content_type}

            response = aiohttp.web.FileResponse(absolute, headers=headers)

            return response
        except Exception as exception:
            return self._compose_standard_exception(exception)

    # ------------------------------------------------------------------------------------------
    # Handle generic protocolj request.
    async def _route_protocolj(self, web_request):
        try:
            # Stuff for the health report.
            self.__protocolj_count += 1

            # Make an object to identify this transaction.
            opaque = Opaque()

            # Read the full body of the request and parse as json.
            content = await web_request.json()

            await self.register_cookies(
                opaque, web_request, content.get(Keywords.ENABLE_COOKIES, [])
            )

            # Dispatch the request to be handled per business logic.
            response_dict = await self.dispatch(content, opaque)

            # Make a response object.
            web_response = aiohttp.web.json_response(response_dict)

            # Flush all cookies.
            await self.flush_cookies(opaque, web_response)

            return web_response
        except Exception as exception:
            return self._compose_standard_exception(exception)

        finally:
            # Release all registered cookies to free their connections and other resources.
            await self.release_cookies(opaque)

    # ----------------------------------------------------------------------------------------
    async def register_cookies(self, opaque, web_request, cookie_names):
        """
        Register all the given named cookies received in the web request matching given names.
        """

        # Configuration does not provide a cookie specification?
        if self.__cookie_specification is None:
            # Just don't do cookies.
            # Other calls may fail, alerting the developer to the mis-configuration.
            return

        logger.debug(f"[COOKOFF] registering cookies {cookie_names}")

        # The caller gives the list of cookies that are interesting.
        for cookie_name in cookie_names:
            # We have a uuid for this cookie name already?
            if cookie_name in web_request.cookies:
                _uuid = web_request.cookies[cookie_name]
                logger.debug(
                    f"[COOKOFF] registering cookie {cookie_name} from existing uuid {_uuid}"
                )
                if _uuid == "" or _uuid == "None":
                    _uuid = None
            else:
                _uuid = None

            # There is no cookie by this name yet?
            if _uuid is None:
                _uuid = str(uuid.uuid4())
                logger.debug(
                    f"[COOKOFF] registering cookie {cookie_name} gets new uuid {_uuid}"
                )

            specification = copy.deepcopy(self.__cookie_specification)
            cookie = opaque.cookies.build_object(specification, predefined_uuid=_uuid)
            cookie.traits()["cookie_name"] = cookie_name

            opaque.cookies.add(cookie)

    # ----------------------------------------------------------------------------------------
    async def release_cookies(self, opaque):
        """
        Release all registered cookies to free their connections and other resources.
        """

        if self.__cookie_specification is None:
            return

        logger.debug("[RELCOOK] releasing cookies")

        for cookie in opaque.cookies.list():
            logger.debug("[RELCOOK] releasing cookie")
            await cookie.release()

    # ----------------------------------------------------------------------------------------
    async def flush_cookies(self, opaque, web_response):
        """
        Add all registered cookies to the response and save their persisted values.
        """

        if self.__cookie_specification is None:
            return

        # logger.debug("[COOKOFF] saving cookies to persist")

        for cookie in opaque.cookies.list():
            # Put the cookie into the web response.
            cookie_name = cookie.trait("cookie_name")
            web_response.set_cookie(cookie_name, cookie.uuid(), max_age=10000000)

            if cookie.is_dirty():
                # logger.debug(f"[COOKOFF] saving {cookie_name} to persist")
                # Store the cookie persistently.
                await cookie.save_to_persist()

    # ----------------------------------------------------------------------------------------
    def get_cookie_contents(self, opaque, cookie_name):
        """"""

        if self.__cookie_specification is None:
            raise RuntimeError("cookies have not been configured")

        cookie = opaque.cookies.find(cookie_name, trait_name="cookie_name")

        return cookie.get_contents()

    # ----------------------------------------------------------------------------------------
    async def get_cookie_content(
        self, opaque, cookie_name, keyword, default=None, xfrom=None
    ):
        """"""

        # No cookie specification in the configuration file?
        if self.__cookie_specification is None:
            raise RuntimeError("cookies have not been configured")

        # Find the cookie object corresponding to the cookie's name.
        cookie = opaque.cookies.find(cookie_name, trait_name="cookie_name")

        # Cookie has not been set yet?
        if not cookie.has_contents():
            # Get the cookie from the persistent storage.
            logger.debug(
                f"[COOKSEL] from {xfrom} loading cookie {id(cookie)} {cookie.uuid()} {cookie_name} from persist"
            )
            await cookie.load_from_persist()

        # Get the contents (dictionary) of the cookie.
        contents = cookie.get_contents()

        # Get the keyword from within the cookie contents dict.
        value = contents.get(keyword, default)

        return value

    # ----------------------------------------------------------------------------------------
    def set_cookie_content(self, opaque, cookie_name, keyword, value):
        """"""

        if self.__cookie_specification is None:
            raise RuntimeError("cookies have not been configured")

        cookie = opaque.cookies.find(cookie_name, trait_name="cookie_name")

        if cookie.has_contents():
            contents = cookie.get_contents()
        else:
            contents = {}
            cookie.set_contents(contents)
            cookie.set_dirty()

        if keyword not in contents or contents[keyword] != value:
            contents[keyword] = value
            cookie.set_dirty()

    # ----------------------------------------------------------------------------------------
    async def set_or_get_cookie_content(
        self, opaque, cookie_name, keyword, new_value, default
    ):

        if new_value == "undefined":
            new_value = None

        # Request does not contain the auto_update_enabled state in the ux?
        # This happens at the first request after a page load.
        if new_value is None:
            new_value = await self.get_cookie_content(
                opaque,
                cookie_name,
                keyword,
                default=default,
                xfrom="set_or_get_cookie_content",
            )

        self.set_cookie_content(
            opaque,
            cookie_name,
            keyword,
            new_value,
        )

        return new_value

    # ----------------------------------------------------------------------------------------
    async def dispatch(self, request_dict):
        """"""

        # Parent class must override this method.
        raise RuntimeError(f"no dispatching available by {callsign(self)} server")

    # ------------------------------------------------------------------------------------------
    async def _route_report_health(self, request):
        try:
            report = await self.report_health()

            # Make a response object.
            web_response = aiohttp.web.json_response(report)

            return web_response
        except Exception as exception:
            return self._compose_standard_exception(exception)

    # ------------------------------------------------------------------------------------------
    # Report server health.
    async def report_health(self):

        report_aiohttp = {}
        report_aiohttp["protocolj_count"] = self.__protocolj_count
        report_aiohttp["file_count"] = self.__file_count
        report_aiohttp["filestore_count"] = self.__filestore_count

        report = {}
        report["aiohttp"] = report_aiohttp
        report["time_alive"] = "%0.1f" % (time.time() - self.__time_started)
        report["request_count"] = (
            self.__protocolj_count + self.__file_count + self.__filestore_count
        )

        return report

    # ------------------------------------------------------------------------------------------
    # Handle request to exit the process.
    async def _route_shutdown(self, request):
        try:
            # Schedule a shutdown to happen after we finish this response.
            asyncio.create_task(self.direct_shutdown())

            response = aiohttp.web.Response(status=200, text="ok")

            return response
        except Exception as exception:
            return self._compose_standard_exception(exception)

    # ----------------------------------------------------------------------------------------
    def _compose_standard_exception(self, exception):
        logger.exception(
            f"{callsign(self)} exception while handling a request: {str(exception)}",
            exc_info=exception,
        )

        exception_causes = list_exception_causes(exception)
        body = {
            "exception": {
                "qualname": qualname(exception),
                "message": str(exception),
                "exception_causes": exception_causes,
            }
        }

        return aiohttp.web.Response(status=500, body=json.dumps(body, indent=4))

    # ----------------------------------------------------------------------------------------
    def client_url(self):
        """"""
        return self.__callsign_url

    # ----------------------------------------------------------------------------------------
    async def client_protocolj(self, request_object, cookies=None):
        """"""
        return await self.__aiohttp_client.client_protocolj(
            request_object, cookies=cookies
        )

    # ----------------------------------------------------------------------------------------
    async def client_get_json(self, url):
        """"""
        return await self.__aiohttp_client.client_get_json(url)

    # ----------------------------------------------------------------------------------------
    async def client_get_csv(self, url):
        """"""
        return await self.__aiohttp_client.client_get_csv(url)

    # ----------------------------------------------------------------------------------------
    async def client_get_file(self, url):
        """"""
        return await self.__aiohttp_client.client_get_file(url)

    # ----------------------------------------------------------------------------------------
    async def client_shutdown(self):
        """"""

        return await self.__aiohttp_client.client_shutdown()

    # ----------------------------------------------------------------------------------------
    async def close_client_session(self):
        """"""
        return await self.__aiohttp_client.close_client_session()

    # ----------------------------------------------------------------------------------------
    async def client_report_health(self):
        """"""
        return await self.__aiohttp_client.client_report_health()
