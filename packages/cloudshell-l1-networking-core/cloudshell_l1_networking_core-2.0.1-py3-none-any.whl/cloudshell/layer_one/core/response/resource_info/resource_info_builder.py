import os
from xml.etree.ElementTree import Element

from cloudshell.layer_one.core.helper.xml_helper import XMLHelper
from cloudshell.layer_one.core.response.resource_info.entities.base import (
    Attribute,
    ResourceInfo,
)


def full_path(relative_path: str) -> str:
    return os.path.join(os.path.dirname(__file__), relative_path)


class ResourceInfoBuilder:
    """Build resource info node."""

    RESOURCE_TEMPLATE = XMLHelper.read_template(
        full_path("templates/resource_template.xml")
    )
    ATTRIBUTE_TEMPLATE = XMLHelper.read_template(
        full_path("templates/resource_attribute_template.xml")
    )
    MAPPING_TEMPLATE = XMLHelper.read_template(
        full_path("templates/resource_incoming_map_template.xml")
    )

    @staticmethod
    def _build_resource_node(resource_info: ResourceInfo) -> Element:
        """Build resource xml node."""
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.RESOURCE_TEMPLATE)
        node.set("Name", resource_info.name)
        node.set("ResourceFamilyName", resource_info.family_name)
        node.set("ResourceModelName", resource_info.model_name)
        node.set("SerialNumber", resource_info.serial_number)
        node.set("Address", resource_info.address)
        attributes_node = node.find("ResourceAttributes")
        for attribute in resource_info.attributes:
            attribute_node = ResourceInfoBuilder._build_attribute_node(attribute)
            attributes_node.append(attribute_node)
        if resource_info.mapping:
            node.append(ResourceInfoBuilder._build_mapping_node(resource_info.mapping))
        return node

    @staticmethod
    def _build_attribute_node(attribute: Attribute) -> Element:
        """Build attribute node.

        :type attribute: cloudshell.layer_one.core.response.resource_info.entities.base.Attribute  # noqa: E501
        :return: Attribute node
        :rtype: xml.etree.ElementTree.Element
        """
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.ATTRIBUTE_TEMPLATE)
        node.set("Name", attribute.name)
        node.set("Type", attribute.type)
        node.set("Value", attribute.value)
        return node

    @staticmethod
    def _build_mapping_node(mapping_node: ResourceInfo) -> Element:
        """Build mapping node."""
        node = XMLHelper.build_node_from_string(ResourceInfoBuilder.MAPPING_TEMPLATE)
        child_incoming_node = node.find("IncomingMapping")
        child_incoming_node.text = mapping_node.address
        return node

    @staticmethod
    def _build_resource_child_nodes(node: Element, resource: ResourceInfo):
        """Build resource nodes for children recursively."""
        if len(resource.child_resources) > 0:
            child_resources_node = node.find("ChildResources")
            for child_resource in resource.child_resources.values():
                child_node = ResourceInfoBuilder._build_resource_node(child_resource)
                child_resources_node.append(child_node)
                ResourceInfoBuilder._build_resource_child_nodes(
                    child_node, child_resource
                )

    @staticmethod
    def build_resource_info_nodes(base_resource: ResourceInfo) -> Element:
        """Build tree of xml nodes for resource tree."""
        resource_node = ResourceInfoBuilder._build_resource_node(base_resource)
        ResourceInfoBuilder._build_resource_child_nodes(resource_node, base_resource)
        return resource_node
