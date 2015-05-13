from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import EmailFieldMixin, User, UserManager


class AbstractEmailUser(User, EmailFieldMixin):
    """
    Abstract polymorphic child model with email login.
    """

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        abstract = True
        verbose_name = _('user with email login')
        verbose_name_plural = _('users with email login')

    @property
    def username(self):
        return getattr(self, self.USERNAME_FIELD)


class EmailUser(AbstractEmailUser):
    objects = UserManager()
