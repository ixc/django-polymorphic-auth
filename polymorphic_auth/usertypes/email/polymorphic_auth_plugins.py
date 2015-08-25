from polymorphic_auth.plugins import PolymorphicAuthChildModelPlugin
from .models import EmailUser
from .admin import EmailUserAdmin


class EmailUserAuthPlugin(PolymorphicAuthChildModelPlugin):
    model = EmailUser
    model_admin = EmailUserAdmin
