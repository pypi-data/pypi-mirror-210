import os
import socket
import sys
import threading
import time
from abc import ABC

from cloudshell.layer_one.core.connection_handler import ConnectionHandler
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.helper.runtime_configuration import RuntimeConfiguration

logger = get_l1_logger(name=__name__)


class DriverListener(ABC):
    """Listen for new connection."""

    BACKLOG = 10
    SERVER_HOST = "0.0.0.0"
    SERVER_PORT = 1024
    SOCKET_TIMEOUT = 900

    def __init__(self, command_executor, xml_logger):
        self._command_executor = command_executor
        self._xml_logger = xml_logger
        self._is_running = False

        self._debug_mode = RuntimeConfiguration().read_key("DEBUG_ENABLED", False)

    def _initialize_socket(self, host: str, port: str):
        """Initialize socket, and start listening."""
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        logger.debug("New socket created")
        try:
            server_socket.bind((host, int(port)))
            server_socket.settimeout(self.SOCKET_TIMEOUT)
            server_socket.listen(self.BACKLOG)
        except Exception as ex:
            # log will be  here
            logger.error(str(ex))
            raise
        logger.debug(f"Listen address {host}:{port}")
        self._is_running = True
        return server_socket

    def set_running(self, is_running):
        self._is_running = is_running

    def _wait_for_debugger_attach(self):
        pid = str(os.getpid())

        while not sys.gettrace():
            logger.info(
                f"Waiting for a debugger to attach to this python driver process. "
                f"(PID #{pid})"
            )
            time.sleep(2)

        logger.info(f"Debugger attached. (PID #{pid})")

    def start_listening(self, host=None, port=None):
        """Initialize socket and start listening."""
        host = host if host else self.SERVER_HOST
        port = port if port else self.SERVER_PORT
        print(f"Listen address {host}:{port}")  # noqa: T201
        server_socket = self._initialize_socket(host, port)
        while self._is_running:
            try:
                connection, connection_data = server_socket.accept()
            except socket.timeout:
                map(  # noqa: C417
                    lambda th: isinstance(th, ConnectionHandler) and th.join(),
                    threading.enumerate(),
                )
                logger.debug("Terminating by idle timeout")
                break
            logger.debug(
                f"New connection from {connection_data[0]}:{connection_data[1]}"
            )
            if connection is not None:
                request_handler = ConnectionHandler(
                    connection,
                    self._command_executor,
                    self._xml_logger,
                )
                if self._debug_mode:
                    self._wait_for_debugger_attach()
                    try:
                        request_handler.run()
                    except Exception as err:
                        logger.debug(f"ConnectionHandler Error: {str(err)}")
                else:
                    request_handler.start()
                    logger.debug(f"Threads count: {threading.activeCount()}")
