"""OPNsense diagnostics module."""

import pkgutil
import sys
import importlib
import inspect
import enum
from pyopnsenseapi.modules import Modules
from .const import DIAGNOSTICS


class Diagnostics():
    """Diagnostics module."""

    is_module = True

    def _controller_discovery(self, base):
        """Discovers all controllers under this module."""
        pkgutil.iter_modules()
        controllers = pkgutil.walk_packages(
            sys.modules[self.__class__.__module__].__path__,
            onerror=None
        )

        for controller in controllers:
            mod = importlib.import_module(base + controller.name)
            classes = inspect.getmembers(mod, predicate=inspect.isclass)
            for class_l in classes:
                if (issubclass(class_l[1], object) and
                    not issubclass(class_l[1], enum.Enum)):
                    if class_l[1].is_controller:
                        setattr(self, controller.name, class_l[1](self._client))
                        break

    def __init__(self, client, base) -> None:
        self._client = client
        self._controller_discovery(base)
