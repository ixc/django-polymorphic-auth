from django.contrib.auth.models import \
    AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils import six, timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from polymorphic import PolymorphicModel, PolymorphicManager


# MIXINS ######################################################################


class EmailFieldMixin(models.Model):
    """
    Add a unique email field.
    """

    email = models.EmailField(
        _('email address'), help_text=_('Required. Unique.'), unique=True,
        error_messages={
            'unique': _('A user with that email address already exists.'),
        })

    class Meta:
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Sends an email to this User.
        """
        send_mail(subject, message, from_email, [self.email], **kwargs)


class NameFieldsMixin(models.Model):
    """
    Add first and last name fields.
    """

    first_name = models.CharField(
        _('first name'), help_text=_('Required.'), max_length=255)
    last_name = models.CharField(
        _('last name'), help_text=_('Required.'), max_length=255)

    class Meta:
        abstract = True

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


class NameMethodsMixin(object):
    """
    This is a separate mixin derived from ``object``, so it can safely be
    included before ``User`` in the base classes list. If we add these methods
    to ``NameFieldsMixin`` and include it before ``User``, we get::

        AttributeError: 'NoneType' object has no attribute 'name'

    """

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        "Returns the short name for the user."
        return self.first_name


class UsernameFieldMixin(models.Model):
    """
    Add a unique username field.
    """

    username = models.CharField(
        _('username'), max_length=255, unique=True,
        help_text=_('Required. Unique. Must contain only letters, digits and '
                    '@.+-_ characters.'),
        validators=[
            validators.RegexValidator(
                r'^[\w.@+-]+$', _('This field is invalid.'), 'invalid'),
        ],
        error_messages={
            'unique': _('A user with that username already exists.'),
        })

    class Meta:
        abstract = True


# MANAGERS ####################################################################


class UserManager(PolymorphicManager, BaseUserManager):
    """
    Manager for ``AbstractUser`` models.
    """

    use_in_migrations = True

    def _create_user(self, password, is_staff, is_superuser, **extra_fields):
        """
        Creates a User with the given password, staff and superuser status, and
        extra fields.
        """
        user = self.model(
            is_staff=is_staff, is_active=True, is_superuser=is_superuser,
            **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password=None, **extra_fields):
        return self._create_user(
            password, is_staff=False, is_superuser=False, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        return self._create_user(
            password, is_staff=True, is_superuser=True, **extra_fields)


# ABSTRACT MODELS #############################################################


@python_2_unicode_compatible
class AbstractUser(PolymorphicModel, AbstractBaseUser, PermissionsMixin):
    """
    Abstract polymorphic user model, with the minimum required fields. Includes
    support for Django's ``Group`` and ``Permission`` models, but has no
    username, email, or name fields.
    """

    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into the admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether the user account is active. Disable '
                    'this instead of deleting the account.'))
    created = models.DateTimeField(
        _('created'), default=timezone.now, editable=False)

    objects = UserManager()

    USERNAME_FIELD = 'id'

    class Meta:
        abstract = True
        verbose_name = _('user')
        verbose_name_plural = _('users')

    def __str__(self):
        return six.text_type(self.get_username())


# CONCRETE MODELS #############################################################


class User(AbstractUser):
    pass
