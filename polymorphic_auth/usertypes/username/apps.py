"""
App configuration for ``polymorphic_auth.username`` app.
"""

# Register signal handlers, but avoid interacting with the database.
# See: https://docs.djangoproject.com/en/1.8/ref/applications/#django.apps.AppConfig.ready

from django.apps import AppConfig


class AppConfig(AppConfig):
    name = '.'.join(__name__.split('.')[:-1])  # Name of package where `apps` module is located
    label = 'polymorphic_auth_username'
