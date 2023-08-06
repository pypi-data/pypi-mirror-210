from __future__ import annotations

import os
import re
from typing import Any

from yaml import Loader, load


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super().__call__(*args, **kwargs)
        return cls._instances[cls]


class RuntimeConfiguration(metaclass=Singleton):
    """Runtime configuration helper."""

    KEY_SEPARATOR_LIST = [r"\.", r"\:", r"\/"]

    def __init__(self, config_path: str = None):
        self._key_separator_pattern = r"|".join(self.KEY_SEPARATOR_LIST)
        if not hasattr(self, "_configuration"):
            self._configuration = self._read_configuration(config_path)

    @property
    def configuration(self) -> dict:
        """Configuration property."""
        return self._configuration

    def _read_configuration(self, config_path: str) -> dict:
        """Read configuration from file if exists or use default."""
        if (
            config_path
            and os.path.isfile(config_path)
            and os.access(config_path, os.R_OK)
        ):
            with open(config_path) as config:
                return load(config, Loader=Loader)

    def read_key(self, complex_key: str, default_value: Any = None):
        """Value for complex key like CLI.PORTS."""
        value = self.configuration
        for key in re.split(self._key_separator_pattern, complex_key):
            if isinstance(value, dict):
                value = value.get(key)
            else:
                return default_value

        return value if value is not None else default_value
