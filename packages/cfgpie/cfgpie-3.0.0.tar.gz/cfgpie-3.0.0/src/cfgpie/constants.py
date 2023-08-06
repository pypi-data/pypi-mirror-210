# -*- coding: UTF-8 -*-

from os.path import dirname, realpath, join
from sys import modules
from types import ModuleType
from weakref import WeakValueDictionary

__all__ = [
    "NAME",
    "INSTANCES",
    "RLOCKS",
    "ROOT",
    "CONFIG",
]

# default instance name:
NAME: str = "cfgpie"

# config parser instances container:
INSTANCES: WeakValueDictionary = WeakValueDictionary()

# recursive thread locks container:
RLOCKS: WeakValueDictionary = WeakValueDictionary()

# main python module:
MODULE: ModuleType = modules.get("__main__")

# root directory:
ROOT: str = dirname(realpath(MODULE.__file__))

# config default file path:
CONFIG: str = join(ROOT, "config", "config.ini")
