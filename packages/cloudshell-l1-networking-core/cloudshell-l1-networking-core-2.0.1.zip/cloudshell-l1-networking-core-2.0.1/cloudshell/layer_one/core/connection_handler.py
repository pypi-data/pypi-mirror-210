from __future__ import annotations

import logging
import re
import socket
import traceback
from threading import Thread

from cloudshell.layer_one.core.command_executor import CommandExecutor
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.request.requests_parser import RequestsParser
from cloudshell.layer_one.core.response.command_responses_builder import (
    CommandResponsesBuilder,
)

logger = get_l1_logger(name=__name__)


class ConnectionClosedException(Exception):
    pass


class ConnectionHandler(Thread):
    """Handle connections."""

    REQUEST_END = rb"</Commands>"
    END_COMMAND = "\r\n"
    READ_TIMEOUT = 30

    def __init__(
        self,
        connection_socket: socket.socket,
        command_executor: CommandExecutor,
        xml_logger: logging.Logger,
        buffer_size: int = 2048,
    ):
        """Initialize class."""
        super().__init__()
        self._connection_socket = connection_socket
        self._xml_logger = xml_logger
        self._command_executor = command_executor
        self._buffer_size = buffer_size

    def run(self):
        """Start handling new connection."""
        while True:
            try:
                command_requests = self._read_request_commands()
                responses = self._command_executor.execute_commands(command_requests)
                self._send_response(
                    CommandResponsesBuilder.to_string(
                        CommandResponsesBuilder.build_xml_result(responses)
                    )
                )
            except ConnectionClosedException:
                self._connection_socket.close()
                logger.debug("Connection closed by remote host")
                break
            except socket.timeout:
                self._connection_socket.close()
                logger.debug("Connection closed by timeout")
                break
            except Exception as ex:
                self._send_response(
                    CommandResponsesBuilder.to_string(
                        CommandResponsesBuilder.build_xml_error(0, str(ex))
                    )
                )
                tb = traceback.format_exc()
                logger.error(tb, exc_info=True)
                self._connection_socket.close()
                break

    def _read_socket(self) -> str:
        """Read data from socket."""
        self._connection_socket.settimeout(self.READ_TIMEOUT)
        data = b""
        while True:
            input_buffer = self._connection_socket.recv(self._buffer_size)
            if not input_buffer:
                raise ConnectionClosedException()
            else:
                # removed input_buffer.strip(), fixes
                # https://github.com/QualiSystems/cloudshell-L1-networking-core/issues/25
                data += input_buffer
                if re.search(self.REQUEST_END, data):
                    break

        return data.decode()

    def _read_request_commands(self) -> list:
        """Read data and create requests."""
        request_string = self._read_socket()
        self._xml_logger.info(request_string.replace("\r", "") + "\n\n")
        requests = RequestsParser.parse_request_commands(request_string)
        logger.debug(requests)
        return requests

    def _send_response(self, response_string: str):
        """Send response."""
        data = response_string + self.END_COMMAND + self.END_COMMAND
        self._connection_socket.send(data.encode())
        self._xml_logger.info(response_string)
