from django.contrib import auth
from django.test.utils import override_settings

from polymorphic_auth import appsettings


def patch_get_user_model():
    """
    Get the polymorphic `DEFAULT_CHILD_MODEL` instead of the `AUTH_USER_MODEL`.
    """
    auth.get_user_model = override_settings(
        AUTH_USER_MODEL=appsettings.DEFAULT_CHILD_MODEL)(auth.get_user_model)
