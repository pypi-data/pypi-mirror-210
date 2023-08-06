import os
import re


class XMLLogger:
    """Simple logger used for xml."""

    PASSWORD_DISPLAY = "Password>*******</"

    def __init__(self, path: str):
        try:
            os.makedirs(os.path.dirname(path))
        except Exception:
            pass
        self._descriptor = open(path, "w+")

    def __del__(self):
        self._descriptor.close()

    def _write_data(self, data: str):
        self._descriptor.write(data + "\r\n")
        self._descriptor.flush()

    def info(self, data: str):
        self._write_data(self._prepare_output(data))

    def _prepare_output(self, data: str) -> str:
        return re.sub(r"Password>.*?</", self.PASSWORD_DISPLAY, data)
