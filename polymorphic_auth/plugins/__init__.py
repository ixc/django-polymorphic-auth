import six
from .base import BaseChildModelPlugin, PluginMount


class PolymorphicAuthChildModelPlugin(six.with_metaclass(
        PluginMount, BaseChildModelPlugin)):
    """
    Mount point for ``Polymorphic Auth`` child model plugins.
    """

    @classmethod
    def register(cls, plugin_path):
        """
        Ensure plugin at given path is registered
        """
        pass

    @classmethod
    def unregister(cls, model):
        """
        Remove all existing plugins for a particular model
        """
        new_plugins = []
        for plugin in cls.plugins:
            # FIXME: Ensure 'model' field has been resolved to a class type
            # before comparison.
            if plugin.model != model:
                new_plugins.append(plugin)

        cls.plugins = new_plugins
