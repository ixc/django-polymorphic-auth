from django.conf import settings

POLYMORPHIC_AUTH = getattr(settings, 'POLYMORPHIC_AUTH', {})

# Get the default polymorphic child model. Django's `AUTH_USER_MODEL` setting
# should always be set to the polymorphic parent model.
DEFAULT_CHILD_MODEL = POLYMORPHIC_AUTH.get(
    'DEFAULT_CHILD_MODEL', settings.AUTH_USER_MODEL)
