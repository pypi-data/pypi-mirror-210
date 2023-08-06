from __future__ import annotations

import logging


def get_l1_logger(name: str) -> logging.Logger:
    return logging.getLogger(f"cloudshell.l1.{name}")
