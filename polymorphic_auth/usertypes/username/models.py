import re

from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import UserManager, UsernameFieldMixin
from polymorphic_auth.usertypes.email.abstract import AbstractEmailUser


class AbstractUsernameUser(AbstractEmailUser, UsernameFieldMixin):

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        abstract = True

    @classmethod
    def create_initial(cls, **kwargs):
        """
        Derive username from name.
        """
        name = kwargs.get('name', '')
        username = re.sub(r'[^a-z]+', '', name.lower())
        kwargs.setdefault(cls.USERNAME_FIELD, username)
        return super(AbstractUsernameUser, cls).create_initial(**kwargs)


class UsernameUser(AbstractUsernameUser):

    objects = UserManager()

    class Meta:
        verbose_name = _('user with username login')
        verbose_name_plural = _('users with username login')
