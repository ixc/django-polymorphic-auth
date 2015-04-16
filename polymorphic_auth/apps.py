from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate


def create_users(sender, **kwargs):
    """
    Creates a user account for each name and email in the ``ADMINS`` and
    ``MANAGERS`` settings.
    """
    User = get_user_model()
    for name, email in settings.ADMINS:
        User.create_initial(
            name=name, email=email, is_staff=True, is_superuser=True)
    for name, email in settings.MANAGERS:
        User.create_initial(
            name=name, email=email, is_staff=True)


class AppConfig(AppConfig):
    """
    Connect ``post_migrate`` signal.
    """
    name = 'polymorphic_auth'

    def ready(self):
        post_migrate.connect(create_users, sender=self)
