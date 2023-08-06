from __future__ import annotations


class CommandRequest:
    def __init__(self, command_name: str, command_id, command_params: dict):
        """Command request entity."""
        self.command_name = command_name
        self.command_id = command_id
        self.command_params = command_params

    def __str__(self):
        return f"Command: {self.command_name}, {self.command_id}, {self.command_params}"

    def __repr__(self):
        return self.__str__()
