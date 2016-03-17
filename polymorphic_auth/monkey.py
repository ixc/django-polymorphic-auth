from django.apps import apps as django_apps
from django.contrib import auth
from django.core.exceptions import ImproperlyConfigured

from polymorphic_auth import appsettings


def _get_user_model():
    """
    Returns the User model that is active in this project.
    """
    try:
        return django_apps.get_model(appsettings.DEFAULT_CHILD_MODEL)
    except ValueError:
        raise ImproperlyConfigured(
            "DEFAULT_CHILD_MODEL must be of the form 'app_label.model_name'")
    except LookupError:
        raise ImproperlyConfigured(
            "DEFAULT_CHILD_MODEL refers to model '%s' that has not been "
            "installed" % appsettings.DEFAULT_CHILD_MODEL
        )


def patch_get_user_model():
    """
    Get the polymorphic `DEFAULT_CHILD_MODEL` instead of the `AUTH_USER_MODEL`.
    """
    auth.get_user_model = _get_user_model
