import six
from .base import BaseChildModelPlugin, PluginMount


class PolymorphicAuthChildModelPlugin(six.with_metaclass(
        PluginMount, BaseChildModelPlugin)):
    """
    Mount point for ``Polymorphic Auth`` child model plugins.
    """
    pass
