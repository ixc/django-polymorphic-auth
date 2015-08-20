"""
App configuration for ``polymorphic_auth.email`` app.
"""

# Register signal handlers, but avoid interacting with the database.
# See: https://docs.djangoproject.com/en/1.8/ref/applications/#django.apps.AppConfig.ready

from django.apps import AppConfig
from django.utils.module_loading import autodiscover_modules


class AppConfig(AppConfig):
    name = 'polymorphic_auth.usertypes.email'
    label = 'polymorphic_auth_email'

    def ready(self):
        autodiscover_modules('plugin')
