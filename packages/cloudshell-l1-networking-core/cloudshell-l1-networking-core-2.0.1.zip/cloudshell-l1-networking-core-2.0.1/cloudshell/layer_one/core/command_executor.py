from __future__ import annotations

from abc import abstractmethod

from cloudshell.layer_one.core.driver_commands_interface import DriverCommandsInterface
from cloudshell.layer_one.core.helper.logger import get_l1_logger
from cloudshell.layer_one.core.layer_one_driver_exception import LayerOneDriverException
from cloudshell.layer_one.core.request.command_request import CommandRequest
from cloudshell.layer_one.core.response.command_response import CommandResponse

logger = get_l1_logger(name=__name__)


class CommandResponseManager:
    """Generate and manage command response."""

    def __init__(self, command_request):
        self._command_response = CommandResponse(command_request)

    def __enter__(self):
        return self._command_response

    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_val:
            self._command_response.success = False
            self._command_response.error = exc_type.__name__
            self._command_response.log = str(exc_val)
            logger.exception("Command Execution Error")
        else:
            self._command_response.success = True
        return True


class CommandExecutor:
    """Execute driver commands."""

    def __init__(self, driver_instance):
        self._driver_instance = driver_instance
        self._state_id = None
        self._registered_commands = {
            "Login": self.login_executor,
            "GetResourceDescription": self.get_resource_description_executor,
            "MapBidi": self.map_bidi_executor,
            "MapUni": self.map_uni_executor,
            "MapClearTo": self.map_clear_to_executor,
            "MapClear": self.map_clear_executor,
            "GetStateId": self.get_state_id_executor,
            "SetStateId": self.set_state_id_executor,
            "GetAttributeValue": self.get_attribute_value_executor,
            "SetAttributeValue": self.set_attribute_value_executor,
            "MapTap": self.map_tap_executor,
            "SetSpeedManual": self.set_speed_manual_executor,
        }

    @abstractmethod
    def driver_instance(self) -> DriverCommandsInterface:
        """Create instance of the driver."""
        return self._driver_instance

    def execute_commands(self, command_requests: list[CommandRequest]) -> list:
        """Execute list of command requests."""
        driver = self.driver_instance()
        command_responses = []
        for command_request in command_requests:
            logger.info(f"Executing command {command_request.command_name}")
            if command_request.command_name in self._registered_commands:
                command = self._registered_commands[command_request.command_name]
                response = command(command_request, driver)
                command_responses.append(response)
            else:
                raise LayerOneDriverException(
                    "Incorrect command name, or command not registered",
                )

        return command_responses

    def login_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute Login command."""
        address = command_request.command_params.get("Address")[0]
        user = command_request.command_params.get("User")[0]
        password = command_request.command_params.get("Password")[0]

        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.login(
                address, user, password
            )
        return command_response

    def get_resource_description_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute GetResourceDescription command."""
        address = command_request.command_params.get("Address")[0]
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.get_resource_description(
                address
            )
        return command_response

    def map_bidi_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute MapBidi command."""
        port_a = command_request.command_params.get("MapPort_A")[0]
        port_b = command_request.command_params.get("MapPort_B")[0]
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.map_bidi(port_a, port_b)
        return command_response

    def map_uni_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute MapUni command."""
        src_port = command_request.command_params.get("SrcPort")[0]
        dst_ports = command_request.command_params.get("DstPort")
        with CommandResponseManager(command_request) as command_response:
            driver_instance.map_uni(src_port, dst_ports)
        return command_response

    def map_clear_to_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute MapClear command."""
        src_port = command_request.command_params.get("SrcPort")[0]
        dst_ports = command_request.command_params.get("DstPort")
        with CommandResponseManager(command_request) as command_response:
            driver_instance.map_clear_to(src_port, dst_ports)
        return command_response

    def map_clear_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute MapClear command."""
        ports = command_request.command_params.get("MapPort")
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.map_clear(ports)
        return command_response

    def get_state_id_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute GetStateId command."""
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.get_state_id()
        return command_response

    def set_state_id_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute SetStateId command."""
        state_id = command_request.command_params.get("StateId")[0]
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.set_state_id(state_id)
        return command_response

    def get_attribute_value_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute GetAttributeValue command."""
        address = command_request.command_params.get("Address")[0]
        attribute_name = command_request.command_params.get("Attribute")[0]
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.get_attribute_value(
                address, attribute_name
            )
        return command_response

    def set_attribute_value_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute SetAttributeValue command."""
        address = command_request.command_params.get("Address")[0]
        attribute_name = command_request.command_params.get("Attribute")[0]
        attribute_value = command_request.command_params.get("Value")[0]
        with CommandResponseManager(command_request) as command_response:
            command_response.response_info = driver_instance.set_attribute_value(
                address, attribute_name, attribute_value
            )
        return command_response

    def map_tap_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute MapTap command."""
        src_port = command_request.command_params.get("SrcPort")[0]
        dst_ports = command_request.command_params.get("DstPort")
        with CommandResponseManager(command_request) as command_response:
            driver_instance.map_tap(src_port, dst_ports)
        return command_response

    def set_speed_manual_executor(
        self, command_request: CommandRequest, driver_instance: DriverCommandsInterface
    ) -> CommandResponse:
        """Execute SetSpeedManual command."""
        src_port = command_request.command_params.get("SrcPort")[0]
        dst_ports = command_request.command_params.get("DstPort")[0]
        speed = command_request.command_params.get("Speed")[0]
        duplex = command_request.command_params.get("Duplex")[0]
        with CommandResponseManager(command_request) as command_response:
            driver_instance.set_speed_manual(src_port, dst_ports, speed, duplex)
        return command_response
