# -*- coding: UTF-8 -*-

__all__ = ["BaseConfigError", "ArgParseError"]


class BaseConfigError(Exception):
    """Base exception for all configuration errors."""


class ArgParseError(BaseConfigError):
    """Exception raised for cmd-line args parsing errors."""
