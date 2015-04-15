from django.utils.translation import ugettext_lazy as _
from django_polymorphic_auth.models import UsernameFieldMixin
from django_polymorphic_auth.usertypes.email.abstract import AbstractEmailUser


class AbstractUsernameUser(AbstractEmailUser, UsernameFieldMixin):

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        abstract = True


class UsernameUser(AbstractUsernameUser):
    class Meta:
        verbose_name = _('user with username login')
        verbose_name_plural = _('users with username login')
