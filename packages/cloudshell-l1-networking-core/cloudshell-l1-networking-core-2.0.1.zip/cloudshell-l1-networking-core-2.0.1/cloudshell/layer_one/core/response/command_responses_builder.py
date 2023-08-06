from __future__ import annotations

import os
from xml.etree import ElementTree

from cloudshell.layer_one.core.helper.xml_helper import XMLHelper
from cloudshell.layer_one.core.response.command_response import CommandResponse

ElementTree.register_namespace(
    "", "http://schemas.qualisystems.com/ResourceManagement/DriverCommandResult.xsd"
)


def full_path(relative_path: str) -> str:
    return os.path.join(os.path.dirname(__file__), relative_path)


class CommandResponsesBuilder:
    RESPONSES_TEMPLATE = XMLHelper.read_template(
        full_path("templates/responses_template.xml")
    )
    COMMAND_RESPONSE_TEMPLATE = XMLHelper.read_template(
        full_path("templates/command_response_template.xml")
    )
    ERROR_RESPONSE = XMLHelper.read_template(full_path("templates/error_response.xml"))

    @staticmethod
    def _build_command_response_node(
        command_response: CommandResponse,
    ) -> ElementTree.Element:
        """Build command response node."""
        command_response_node = XMLHelper.build_node_from_string(
            CommandResponsesBuilder.COMMAND_RESPONSE_TEMPLATE
        )
        command_response_node.set(
            "CommandName", command_response.command_request.command_name
        )
        command_response_node.set(
            "CommandId", command_response.command_request.command_id
        )
        command_response_node.set("Success", str(command_response.success).lower())

        timestamp_node = command_response_node.find("Timestamp")
        timestamp_node.text = command_response.timestamp

        if command_response.error is not None:
            command_response_node.find("Error").text = command_response.error

        if command_response.log is not None:
            command_response_node.find("Log").text = command_response.log

        if command_response.response_info is not None:
            command_response_node.append(
                command_response.response_info.build_xml_node()
            )
        else:
            command_response_node.append(ElementTree.Element("ResponseInfo"))
        return command_response_node

    @staticmethod
    def build_xml_result(responses: list[CommandResponse]) -> ElementTree.Element:
        """Build responses for list of responses objects."""
        responses_node = XMLHelper.build_node_from_string(
            CommandResponsesBuilder.RESPONSES_TEMPLATE
        )
        tree = ElementTree.ElementTree(responses_node)
        for command_response in responses:
            responses_node.append(
                CommandResponsesBuilder._build_command_response_node(command_response)
            )
        return tree.getroot()

    @staticmethod
    def to_string(root: ElementTree.Element) -> str:
        """Generate string for xml node."""
        return ElementTree.tostring(root, encoding="unicode", method="xml").replace(
            "\n", "\r\n"
        )

    @staticmethod
    def build_xml_error(error_code, log_message):
        """Build error response."""
        command_response_node = XMLHelper.build_node_from_string(
            CommandResponsesBuilder.ERROR_RESPONSE
        )
        tree = ElementTree.ElementTree(command_response_node)
        namespace = XMLHelper.get_node_namespace(command_response_node)
        command_response_node.find(f"{namespace}ErrorCode").text = str(error_code)
        command_response_node.find(f"{namespace}Log").text = str(log_message)
        return tree.getroot()
