from django.utils.translation import ugettext_lazy as _
from django_polymorphic_auth.usertypes.email.abstract import AbstractEmailUser


class EmailUser(AbstractEmailUser):

    class Meta:
        verbose_name = _('user with email login')
        verbose_name_plural = _('users with email login')
