from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import UserManager
from polymorphic_auth.usertypes.email.abstract import AbstractEmailUser


class EmailUser(AbstractEmailUser):

    objects = UserManager()

    class Meta:
        verbose_name = _('user with email login')
        verbose_name_plural = _('users with email login')
