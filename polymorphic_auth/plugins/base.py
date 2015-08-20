import inspect
from django.apps import apps
from django.contrib.contenttypes.models import ContentType


# METACLASSES #################################################################

# When used as a metaclass for a mount point, each plugin subclass will
# register itself with the mount point. Attributes and methods defined on a
# metaclass will become class methods on each mount point subclass.

# To iterate plugin classes, access the `plugins` attribute on the mount point.
# To iterate plugin instances, call the `get_plugins()` method on the mount
# point. Any arguments will be passed through to each plugin.


class PluginMount(type):
    """
    Marty Alchin's Simple Plugin Framework.

    See: http://martyalchin.com/2008/jan/10/simple-plugin-framework/
    """

    def __init__(cls, name, bases, attrs):
        if not hasattr(cls, 'plugins'):
            # This branch only executes when processing the mount point itself.
            # So, since this is a new plugin type, not an implementation, this
            # class shouldn't be registered as a plugin. Instead, it sets up a
            # list where plugins can be registered later.
            cls.plugins = []
        else:
            # This must be a plugin implementation, which should be registered.
            # Simply appending it to the list is all that's needed to keep
            # track of it later.
            cls.plugins.append(cls)

    def get_plugins(cls, *args, **kwargs):
        """
        Return a list of plugin instances and pass through arguments.
        """
        return [plugin(*args, **kwargs) for plugin in cls.plugins]


# BASE PLUGIN MOUNT POINTS ####################################################

# When used as base classes along with a plugin mount metaclass, the resulting
# mount point inherit these attributes and methods.


class BaseChildModelPlugin(object):
    """
    Subclass with a ``PluginMount`` metaclass to create a new plugin mount
    point for polymorphic child models.
    """

    model = None
    model_admin = None

    @staticmethod
    def resolve_class(cl):
        if inspect.isclass(cl):
            # already a class
            return cl
        try:
            # try [appname].[modelname] format first
            return apps.get_model(cl)
        except (AttributeError, LookupError, ValueError):
            # try full path to module
            d = cl.rfind(".")
            classname = cl[d+1:len(cl)]
            m = __import__(cl[0:d], globals(), locals(), [classname])
            return getattr(m, classname)

    @property
    def content_type(self):
        """
        Return the ``ContentType`` for the model.
        """
        return ContentType.objects.get_for_model(self.model_class())

    @property
    def verbose_name(self):
        """
        Returns the title for the plugin, by default it reads the
        ``verbose_name`` of the model.
        """
        return self.model_class()._meta.verbose_name

    @classmethod
    def model_class(cls):
        """
        Resolve ``model`` attribute into a class type (if not already).
        """
        return cls.resolve_class(cls.model)

    @classmethod
    def model_admin_class(cls):
        """
        Resolve ``model_admin`` attribute into a class type (if not already).
        """
        return cls.resolve_class(cls.model_admin)

    @classmethod
    def unregister(cls, model):
        """
        Remove all existing plugins for a particular model
        """
        model = cls.resolve_class(model)
        new_plugins = []
        for plugin in cls.plugins:
            if plugin.model_class() != model:
                new_plugins.append(plugin)

        cls.plugins = new_plugins
