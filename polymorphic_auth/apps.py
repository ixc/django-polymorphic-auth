from django.apps import AppConfig
from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models.signals import post_migrate
from django.utils.module_loading import autodiscover_modules


def create_users(sender, **kwargs):
    """
    Creates a user account for each name and email in the ``ADMINS`` and
    ``MANAGERS`` settings, skipping duplicates.
    """
    User = get_user_model()
    seen = set()

    def create(name, email, fields):
        # Use an incrementing integer as the username for user models with "id"
        # as the username field.
        if User.USERNAME_FIELD == 'id':
            seen.add((name, email))
            fields.update(id=len(seen))
        User.try_create(**fields)

    # Admins.
    for name, email in settings.ADMINS:
        fields = dict(name=name, email=email, is_staff=True, is_superuser=True)
        create(name, email, fields)

    # Managers.
    for name, email in settings.MANAGERS:
        fields = dict(name=name, email=email, is_staff=True)
        create(name, email, fields)


class AppConfig(AppConfig):
    """
    Connect ``post_migrate`` signal.
    """
    name = 'polymorphic_auth'

    def ready(self):
        post_migrate.connect(create_users, sender=self)
        autodiscover_modules('polymorphic_auth_plugins')
