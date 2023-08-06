from abc import ABC, abstractmethod


class DriverCommandsInterface(ABC):
    @abstractmethod
    def login(self, address, username, password):
        """Driver command Login.

        :param address:
        :param username:
        :param password:
        :return:
        """
        pass

    @abstractmethod
    def get_resource_description(self, address):
        """Driver command GetResourceDescription.

        :param address:
        :return:
        """
        pass

    @abstractmethod
    def map_bidi(self, src_port, dst_port):
        """Driver command MapBidi.

        :param src_port:
        :param dst_port:
        :return:
        """
        pass

    @abstractmethod
    def map_uni(self, src_port, dst_ports):
        """Driver command MapUni.

        :param src_port:
        :param dst_ports:
        :return:
        """
        pass

    @abstractmethod
    def map_clear_to(self, src_port, dst_ports):
        """Driver command MapClearTo.

        :param src_port:
        :param dst_ports:
        :return:
        """
        pass

    @abstractmethod
    def map_clear(self, ports):
        """Driver command MapClear.

        :param ports:
        :return:
        """
        pass

    @abstractmethod
    def get_attribute_value(self, address, attribute_name):
        """Driver command GetAttributeValue.

        :param address:
        :param attribute_name:
        :return:
        """
        pass

    @abstractmethod
    def set_attribute_value(self, address, attribute_name, attribute_value):
        """Driver command SetAttributeValue.

        :param address:
        :param attribute_name:
        :param attribute_value:
        :return:
        """
        pass

    @abstractmethod
    def get_state_id(self):
        """Driver command GetStateId.

        :return:
        """
        pass

    @abstractmethod
    def set_state_id(self, state_id):
        """Driver command SetStateId.

        :param state_id:
        :return:
        """
        pass

    @abstractmethod
    def map_tap(self, src_port, dst_ports):
        """Driver command MapTap.

        :param src_port:
        :param dst_ports:
        :return:
        """
        pass

    @abstractmethod
    def set_speed_manual(self, src_port, dst_port, speed, duplex):
        """Set connection speed.

        Is not used for the new standard
        :param src_port:
        :param dst_port:
        :param speed:
        :param duplex:
        :return:
        """
        pass
