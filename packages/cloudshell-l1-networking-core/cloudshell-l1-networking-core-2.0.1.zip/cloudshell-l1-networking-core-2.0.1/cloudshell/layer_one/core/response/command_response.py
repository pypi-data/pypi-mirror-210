from datetime import datetime

from cloudshell.layer_one.core.request.command_request import CommandRequest


class CommandResponse:
    def __init__(self, command_request: CommandRequest):
        """Command response."""
        self.command_request = command_request

        # Response attributes
        self.success = False
        self.error = None
        self.log = None
        self.timestamp = datetime.now().strftime("%d.%m.%Y %H:%M:%S")
        self.response_info = None

    def __str__(self):
        return (
            f"Command: {self.command_request.command_name}, "
            f"{self.command_request.command_id}, "
            f"{self.command_request.command_params}"
        )

    def __repr__(self):
        return self.__str__()
