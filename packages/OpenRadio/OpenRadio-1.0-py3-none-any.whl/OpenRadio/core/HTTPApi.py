from .const import *
from .Exceptions import *
import http.server as http
from http import HTTPStatus
import http.server as httpd

import urllib.parse as urlparser
import json

from threading import Thread

import logging

LOGGER = logging.getLogger(__name__)
LOGGER.setLevel(LOG_LEVEL)
LOGGER.addHandler(LOG_HANDLER)

NOT_FOUND = {
    "response_code": HTTPStatus.NOT_FOUND,
    "content_type": "application/json",
    "response": {"error": "The Requested Path was not found."},
}
UNKNOWN_REQUEST = {
    "response_code": HTTPStatus.NOT_FOUND,
    "content_type": "application/json",
    "response": {"error": "Not a valid request."},
}


NOT_DECODEABLE_MSG = {"error": "Response data not in str,bytes or dict format."}

FACTORY_SETTINGS = {"ip": "0.0.0.0", "port": 8081}


class HTTPApi:
    def __init__(self, core):
        self.core = core

        http_handler = Handler
        http_handler.set_core(Handler, self.core)

        server_stat = self._start_server(http_handler)

        if not server_stat:
            LOGGER.warning(
                "Error while starting http server. Falling back to factory settings."
            )
            self.restore_server_settings()
            server_stat = self._start_server(http_handler)

        if not server_stat:
            raise HTTPApiNotStarting(f"""Server not staring with factory defaults. Is the port ({self.get_config_entry("ip")}:{self.get_config_entry("port")}) unused?""")



        LOGGER.info(
            f"""Server is available at : {self.get_config_entry("ip")}:{self.get_config_entry("port")}."""
        )
        thread = Thread(target=self.server.serve_forever, name="HTTPApi")

        self.thread = thread

        thread.start()

    def _start_server(self,http_handler):
        try:
            server = httpd.HTTPServer(
                (self.get_config_entry("ip"), self.get_config_entry("port")),
                http_handler,
            )

        except:
            return False

        self.server = server

        return True

    def get_config_entry(self, entry):
        config = self.core.Settings.get_config("core.httpapi")

        if config == {}:
            LOGGER.info(f"Empty config. Falling back to factory settings.")
            self.restore_server_settings()
            return FACTORY_SETTINGS.get(entry, False)

        if entry not in config.keys():
            LOGGER.warning(
                f"Entry not found in settings. Falling back to factory settings."
            )
            return FACTORY_SETTINGS.get(entry, False)

        return config[entry]

    def restore_server_settings(self):
        self.core.Settings.save_config("core.httpapi", FACTORY_SETTINGS)

    def on_quit(self):
        self.server.shutdown()
        self.thread.join()


class Handler(httpd.BaseHTTPRequestHandler):
    def _answer_request(self, response):
        response_data = response["response"]
        response_type = type(response_data)

        response_code = response["response_code"]

        response_content = response["content_type"]

        if response_type != bytes and response_type != str and response_type != dict:
            LOGGER.error("Unable to send data to client. Not bytes,str or dict.")
            response_data = NOT_DECODEABLE_MSG

            response_code = HTTPStatus.INTERNAL_SERVER_ERROR
            response_content = "application/json"

        if response_type == str:
            response_data = response_data.encode("utf-8")
        elif response_type == dict:
            try:
                response_data = json.dumps(response_data).encode("utf-8")
            except TypeError:
                LOGGER.error("Got unserializable dict.")
                response_data = json.dumps(NOT_DECODEABLE_MSG).encode("utf-8")
                response_code = HTTPStatus.INTERNAL_SERVER_ERROR
                response_content = "application/json"

        self.send_response(response_code)
        self.send_header("Content-Type", response["content_type"])
        self.end_headers()

        self.wfile.write(response_data)

    def _parse_request(self, post_data=None):
        decoded_url = urlparser.unquote(self.path)
        split_url = decoded_url.split("/")

        rootpath = split_url[1]

        if rootpath == "":
            self._answer_request(UNKNOWN_REQUEST)
            return

        http_modules = self.core.ModuleHandler.get_modules_by_tags(["USES_HTTP"])

        if rootpath not in http_modules:
            self._answer_request(NOT_FOUND)
            return

        module = self.core.ModuleHandler.get_module_by_domain(http_modules[rootpath])

        module_sub_path = split_url

        module_sub_path.pop(0)
        module_sub_path.pop(0)
        if "" in module_sub_path:
            module_sub_path.remove("")

        module_response = module.on_http(
            path=module_sub_path, data=post_data, handler=self
        )
        self._answer_request(module_response)

    def set_core(self, core):
        self.core = core

    def do_GET(self):
        self._parse_request()

    def do_POST(self):
        length = int(self.headers["Content-Length"])
        data = self.rfile.read(length)
        self._parse_request(post_data=data)
