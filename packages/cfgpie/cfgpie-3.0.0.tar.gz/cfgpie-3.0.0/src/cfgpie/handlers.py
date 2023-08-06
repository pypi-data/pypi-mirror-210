# -*- coding: UTF-8 -*-

from __future__ import annotations

from ast import literal_eval
from configparser import ConfigParser, BasicInterpolation, ExtendedInterpolation
from decimal import Decimal
from os.path import isfile, exists, realpath
from sys import argv
from threading import RLock
from typing import Any, Type, Dict, Union, List, Tuple, Iterator

from .constants import NAME, INSTANCES, RLOCKS, ROOT
from .exceptions import ArgParseError
from .utils import folder, file, ensure_folder, as_dict

__all__ = [
    "BasicInterpolation",
    "ExtendedInterpolation",
    "CfgParser",
]


DEFAULTS: dict = {
    "directory": ROOT,
}

CONVERTERS: dict = {
    "decimal": Decimal,
    "list": literal_eval,
    "tuple": literal_eval,
    "set": literal_eval,
    "dict": literal_eval,
    "path": realpath,
    "folder": folder,
    "file": file,
}


class ArgsParser(object):

    @staticmethod
    def _check_argv(args: Union[str, List[str], Tuple[str]]) -> Union[List[str], Tuple[str]]:
        if args is None:
            return argv[1:]
        elif isinstance(args, str):
            return [arg.strip() for arg in args.split(" ")]
        elif not isinstance(args, (list, tuple)):
            raise TypeError(
                f"cmd-line params must be of type 'str', 'list[str]' or "
                f"'tuple[str]' not '{type(args).__name__}'!"
            )
        return args

    @staticmethod
    def _update_params(params: dict, section: str, option: str, value: str):
        if section not in params:
            params.update({section: {option: value}})
        else:
            params.get(section).update({option: value})

    def _parse_argv(self, args: Iterator[str]) -> dict:
        temp = dict()
        for arg in args:
            if arg.startswith("--"):
                stripped = arg.strip("-")
                try:
                    section, option = stripped.split("-")
                except ValueError:
                    raise ArgParseError(f"Inconsistency in cmd-line parameters '{arg}'!")
                else:
                    try:
                        value = next(args)
                    except StopIteration:
                        raise ArgParseError(f"Missing value for parameter '{arg}'")
                    else:
                        if value.startswith("--") is False:
                            self._update_params(temp, section.upper(), option, value)
                        else:
                            raise ArgParseError(f"Incorrect value '{value}' for parameter '{arg}'!")
            else:
                raise ArgParseError(f"Inconsistency in cmd-line parameters '{arg}'!")
        return temp


class Singleton(object):

    def __init__(self, parser: Type[CfgParser]):
        self._parser = parser

    def __call__(self, name: str = NAME, **kwargs):
        self._parser._check_name(name)
        if name not in INSTANCES:
            instance = self._parser(name, **kwargs)
            INSTANCES.update({name: instance})
        return INSTANCES.get(name)


@Singleton
class CfgParser(ConfigParser, ArgsParser):
    """
    ConfigParser that:

        - sets `DEFAULT` section with `directory` pointing at root folder of the project;
        - implements interpolation using :class:`ExtendedInterpolation()`;
        - brings extra converters for: `decimal`, `list`, `tuple`, `set`, `dict`, `path`, `folder` and `file`.
    """

    @staticmethod
    def _dispatch_rlock(name: str = NAME) -> RLock:
        if name not in RLOCKS:
            instance: RLock = RLock()
            RLOCKS.update({name: instance})
        return RLOCKS.get(name)

    @staticmethod
    def _check_name(value: str) -> str:
        if not isinstance(value, str):
            raise TypeError(
                f"CfgParser 'name' attribute must be of "
                f"type 'str' not '{type(value).__name__}'!"
            )
        if len(value) == 0:
            raise ValueError(
                f"CfgParser 'name' attribute must be a "
                f"string object with a length greater than '0'!"
            )
        return value

    def __init__(self, name: str = NAME, **kwargs):
        self._name = name

        defaults: dict = DEFAULTS.copy()
        if "defaults" in kwargs:
            defaults.update(kwargs.pop("defaults"))
        kwargs.update(defaults=defaults)

        if "interpolation" not in kwargs:
            kwargs.update(interpolation=ExtendedInterpolation())

        converters: dict = CONVERTERS.copy()
        if "converters" in kwargs:
            converters.update(kwargs.pop("converters"))
        kwargs.update(converters=converters)

        super(ConfigParser, self).__init__(**kwargs)

    @property
    def name(self) -> str:
        return self._name

    def open(self, file_path: str, encoding: str = "UTF-8", fallback: dict = None):
        """
        Read from configuration `file_path`. If `file_path` does not exist and
        `fallback` is provided the latter will be used and a new configuration
        file will be written.
        """
        file_path: str = realpath(file_path)
        thread_lock: RLock = self._dispatch_rlock(file_path)
        with thread_lock:
            if exists(file_path) and isfile(file_path):
                self.read(file_path, encoding=encoding)
            elif fallback is not None:
                self.read_dict(dictionary=fallback, source="<backup>")
                self.save(file_path, encoding)

    def save(self, file_path: str, encoding: str = "UTF-8"):
        """Save the configuration to `file_path`."""
        thread_lock = self._dispatch_rlock(file_path)
        with thread_lock:
            ensure_folder(file_path)
            with open(file_path, "w", encoding=encoding) as handle:
                self.write(handle)

    def read_argv(self, args: Union[str, List[str], Tuple[str]] = None):
        """Parse `args` (cmd-line arguments) and update the configuration."""
        self._thread_lock(self._name).acquire()
        try:
            args = self._check_argv(args)
        except (TypeError, ValueError):
            raise
        else:
            if len(args) > 0:
                self.read_dict(
                    dictionary=self._parse_argv(iter(args)),
                    source="<argv>"
                )
        finally:
            self._thread_lock(self._name).release()

    def parse(self, args: Union[str, List[str], Tuple[str]] = None):
        """
        Parse `args` (cmd-line arguments) and update the configuration.
        Don't use this one! Use `read_argv()` instead.
        """
        self.read_argv(args)

    def set_defaults(self, mapping: Union[Dict[str, Any], List[Tuple[str, Any]]] = None, **kwargs):
        """Update `DEFAULT` section with `mapping` & `kwargs`."""
        with self._thread_lock(self._name):
            params: dict = as_dict(mapping, **kwargs)

            if len(params) > 0:
                self._read_defaults(params)

    def _thread_lock(self, name: str = NAME) -> RLock:
        if not hasattr(self, "_rlock"):
            self._rlock: RLock = self._dispatch_rlock(name)
        return self._rlock
