from __future__ import annotations

from collections import defaultdict
from xml.etree.ElementTree import Element

from cloudshell.layer_one.core.helper.xml_helper import XMLHelper
from cloudshell.layer_one.core.request.command_request import CommandRequest


class RequestsParser:
    """Parse request data and build command requests."""

    @staticmethod
    def _build_command_instance(command_node: Element) -> CommandRequest:
        """Build command instance for command node."""
        command_name = command_node.get("CommandName")
        command_id = command_node.get("CommandId")
        command_params = defaultdict(list)
        namespace = XMLHelper.get_node_namespace(command_node)
        parameters_node = command_node.find(namespace + "Parameters")

        if parameters_node is not None:
            for param_node in parameters_node:
                key = param_node.tag.replace(namespace, "")
                command_params[key].append(param_node.text)

        return CommandRequest(command_name, command_id, command_params)

    @staticmethod
    def parse_request_commands(xml_request: str) -> list:
        """Parse xml request and create command instances."""
        commands = []
        request_node = XMLHelper.build_node_from_string(xml_request)
        for command_node in request_node:
            commands.append(RequestsParser._build_command_instance(command_node))
        return commands
