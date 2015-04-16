from polymorphic_auth.models import \
    EmailFieldMixin, NameFieldsMixin, NameMethodsMixin, User


# This lives here instead of in the `models` module because `UsernameUser` is
# a subclass, and we don't want `email` migrations to be a dependency of for
# `username` migrations.
class AbstractEmailUser(
        NameMethodsMixin, User, EmailFieldMixin, NameFieldsMixin):

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        abstract = True
