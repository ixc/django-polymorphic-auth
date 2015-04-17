from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import \
    EmailFieldMixin, User, UserManager, UsernameFieldMixin, \
    UsernameMethodsMixin


class AbstractUsernameUser(
        UsernameMethodsMixin, User, EmailFieldMixin, UsernameFieldMixin):
    """
    Abstract polymorphic child model with username login.
    """

    USERNAME_FIELD = 'username'
    REQUIRED_FIELDS = ['email', 'first_name', 'last_name']

    class Meta:
        abstract = True
        verbose_name = _('user with username login')
        verbose_name_plural = _('users with username login')


class UsernameUser(AbstractUsernameUser):
    objects = UserManager()
