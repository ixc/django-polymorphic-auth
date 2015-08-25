import six
from .base import BaseChildModelPlugin, PluginMount


class PolymorphicAuthChildModelPlugin(six.with_metaclass(
        PluginMount, BaseChildModelPlugin)):
    """
    Mount point for ``Polymorphic Auth`` child model plugins.
    """

    @classmethod
    def get_plugin_for_model(cls, model):
        for plugin in cls.plugins:
            if plugin.model == model:
                return plugin

    @classmethod
    def unregister(cls, model):
        """
        Remove all existing plugins for a particular model
        """
        try:
            plugin = cls.get_plugin_for_model(model)
            cls.plugins.remove(plugin)
        except ValueError:
            pass
