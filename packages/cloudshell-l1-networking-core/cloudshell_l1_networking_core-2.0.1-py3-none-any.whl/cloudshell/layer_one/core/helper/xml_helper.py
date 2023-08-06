import re
from xml.etree import ElementTree


class XMLHelper:
    @staticmethod
    def build_node_from_string(xml_str: str) -> ElementTree.Element:
        """Node for template."""
        parser = ElementTree.XMLParser(encoding="unicode")
        node = ElementTree.fromstring(xml_str, parser=parser)
        return node

    @staticmethod
    def read_template(template_path: str) -> str:
        """Read template from file."""
        with open(template_path) as f:
            return f.read()

    @staticmethod
    def get_node_namespace(node: ElementTree.Element) -> str:
        """Node namespace."""
        m = re.match(r"{.*}", node.tag)
        return m.group(0) if m else ""
