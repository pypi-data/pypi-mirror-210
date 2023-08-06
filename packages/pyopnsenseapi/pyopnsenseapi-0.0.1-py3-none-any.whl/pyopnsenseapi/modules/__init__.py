"""pyopnsenseapi add-on modules"""

import pkgutil
import sys
import importlib
import inspect

class Modules(object):
    """Functional modules."""

    def _module_discovery(self, base):
        """Discovers all modules on the system and starts init routines."""
        pkgutil.iter_modules()
        controllers = pkgutil.walk_packages(
            sys.modules[self.__class__.__module__].__path__,
            onerror=None
        )

        for controller in controllers:
            if controller.ispkg:
                mod = importlib.import_module(base + controller.name)
                classes = inspect.getmembers(mod, predicate=inspect.isclass)
                for class_l in classes:
                    if class_l[1].is_module:
                        setattr(self, controller.name,
                                class_l[1](self._client, base + controller.name + '.'))
                        break

    def __init__(self, client) -> None:
        self._client = client
        self._module_discovery('pyopnsenseapi.modules.')
