from polymorphic_auth.plugins import PolymorphicAuthChildModelPlugin
from .models import UsernameUser
from .admin import UsernameUserAdmin


class UsernameUserAuthPlugin(PolymorphicAuthChildModelPlugin):
    model = UsernameUser
    model_admin = UsernameUserAdmin
