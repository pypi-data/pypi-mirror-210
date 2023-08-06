"""Simple plugin loader"""
#  Copyright (c) 2023. ISTMO Center S.A.  All Rights Reserved
#

import importlib


class PluginInterface:
    @staticmethod
    def initialise() -> None:
        """Initialise the plugin"""


def import_module(name: str) -> PluginInterface:
    return importlib.import_module(name)


def load_plugins(plugins: list[str]) -> None:
    """Load the plugins list"""
    for plugin_name in plugins:
        plugin = import_module(plugin_name)
        plugin.initialise()
