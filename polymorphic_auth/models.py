from __future__ import print_function

import random
import re
import sys

from django import VERSION as django_version
from django.contrib.auth.models import \
    AbstractBaseUser, BaseUserManager, PermissionsMixin
from django.core import validators
from django.core.mail import send_mail
from django.db import models
from django.utils import six, timezone
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
try:
    # for django-polymorphic >= 0.8
    from polymorphic.models import PolymorphicModel, PolymorphicManager
except ImportError:
     # for django-polymorphic < 0.8
     from polymorphic import PolymorphicModel, PolymorphicManager


# FIELD MIXINS ################################################################


class AdminFieldsMixin(models.Model):
    """
    Add required fields for compatibility with the Django admin. The username
    field is used for both short and long form names. See:

    https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#custom-users-and-django-contrib-admin
    """

    is_staff = models.BooleanField(
        _('staff status'), default=False,
        help_text=_('Designates whether the user can log into the admin '
                    'site.'))
    is_active = models.BooleanField(
        _('active'), default=True,
        help_text=_('Designates whether the user account is active. Disable '
                    'this instead of deleting the account.'))

    class Meta:
        abstract = True

    def get_full_name(self):
        """
        Return the username field.
        """
        return six.text_type(self.get_username())

    get_short_name = get_full_name


class EmailFieldMixin(models.Model):
    """
    Add a unique email field.
    """

    email = models.EmailField(
        _('email address'), help_text=_('Required. Unique.'), max_length=254,
        unique=True,
        error_messages={
            'unique': _('A user with that email address already exists.'),
        })

    class Meta:
        abstract = True

    def email_user(self, subject, message, from_email=None, **kwargs):
        """
        Send an email to the user.
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


# METHOD MIXINS ###############################################################

# This is a separate mixin derived from `object`, so it can safely be included
# before `User` in polymorphic child models. If we add these methods to
# `NameFieldsMixin` and include it before `User`, we get:
#
#     AttributeError: 'NoneType' object has no attribute 'name'.


class NameMethodsMixin(object):
    """
    Add methods for ``NameFieldsMixin``.
    """

    @classmethod
    def try_create(cls, **kwargs):
        """
        Get first and last name from name.
        """
        name = kwargs.get('name', '').split()
        kwargs.setdefault('first_name', ' '.join(name[:1]))
        kwargs.setdefault('last_name', ' '.join(name[1:]))
        return super(NameMethodsMixin, cls).try_create(**kwargs)

    def get_full_name(self):
        """
        Returns the first_name plus the last_name, with a space in between.
        """
        full_name = '%s %s' % (self.first_name, self.last_name)
        return full_name.strip()

    def get_short_name(self):
        """
        Return the first name.
        """
        return self.first_name


class UsernameMethodsMixin(object):
    """
    Add methods for ``UsernameFieldMixin``.
    """

    @classmethod
    def try_create(cls, **kwargs):
        """
        Get username from name.
        """
        username = re.sub(r'[^a-z]+', '', kwargs.get('name', '').lower())
        kwargs.setdefault(cls.USERNAME_FIELD, username)
        return super(UsernameMethodsMixin, cls).try_create(**kwargs)


# MANAGERS ####################################################################


class UserManager(PolymorphicManager, BaseUserManager):
    """
    Manager for ``AbstractUser`` models. See:

    https://docs.djangoproject.com/en/1.8/topics/auth/customizing/#django.contrib.auth.models.CustomUserManager
    """

    def _create_user(self, password, **extra_fields):
        """
        Create a user account with a password.
        """
        user = self.model(**extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_user(self, password, **extra_fields):
        """
        Force ``is_staff`` and ``is_superuser`` fields to ``False``.
        """
        extra_fields.update(is_staff=False, is_superuser=False)
        return self._create_user(password, **extra_fields)

    def create_superuser(self, password, **extra_fields):
        """
        Force ``is_staff`` and ``is_superuser`` fields to ``True``.
        """
        extra_fields.update(is_staff=True, is_superuser=True)
        return self._create_user(password, **extra_fields)


# MODELS ######################################################################


@python_2_unicode_compatible
class AbstractUser(PolymorphicModel, AbstractBaseUser):
    """
    Abstract polymorphic parent model, with the bare minimum required fields.
    """

    created = models.DateTimeField(
        _('created'), default=timezone.now, editable=False)

    USERNAME_FIELD = 'id'

    class Meta:
        abstract = True
        verbose_name = _('user with ID login')
        verbose_name_plural = _('users with ID login')

    def __str__(self):
        return six.text_type(self.get_username())

    @classmethod
    def try_create(cls, _stdout=sys.stdout, **kwargs):
        """
        Creates a user account, if it does not already exist. Returns a 2-tuple
        containing the user and a ``created`` boolean.

        You must provide all required fields as ``kwargs``. If no password is
        given, one will be randomly generated.

        Credentials and field values will be written to ``_stdout``.
        """
        # This is a classmethod instead of a manager method so that subclasses
        # can easily override it to provide additional or derived fields. For
        # example, deriving a username from a name or email address.
        username = kwargs.pop(cls.USERNAME_FIELD)
        password = kwargs.pop('password', cls.objects.make_random_password(
            length=random.randint(19, 28)))
        try:
            return cls.objects.get(**{cls.USERNAME_FIELD: username}), False
        except cls.DoesNotExist:
            user = cls()
            setattr(user, cls.USERNAME_FIELD, username)
            user.set_password(password)
            # Collect output into a dict to be written to `_stdout` after the
            # user is saved. We have to do that last in case the username field
            # is an `AutoField`.
            out = [
                'Created user account:',
                '  {}: {{}}'.format(cls.USERNAME_FIELD),
                '  password: {}'.format(password),
            ]
            for key, value in kwargs.items():
                # Only assign values to known attributes, in case `kwargs`
                # contains data that was only used to derive field values.
                if hasattr(user, key):
                    setattr(user, key, value)
                    out.append('  {}: {}'.format(key, value))
            user.save()
            # Write output to `_stdout`, now that we know the username.
            print('\n'.join(out).format(user.get_username()), file=_stdout)
            return user, True


class AbstractAdminUser(
        NameMethodsMixin, AbstractUser, AdminFieldsMixin, NameFieldsMixin,
        PermissionsMixin):
    """
    Abstract polymorphic child model with support for Django admin and
    permissions, plus name fields.
    """

    REQUIRED_FIELDS = ['first_name', 'last_name']

    class Meta:
        abstract = True


# Monkey-patch Django 1.7's `AbstractBaseUser` fields to match the field
# settings as applied in Django 1.8, to make our `AbstractAdminUser` model
# match the one in 1.8+. This should avoid the need for differing DB migrations
# for downstream projects whether they use Django 1.7 or 1.8+
if django_version >= (1, 7) and django_version < (1, 8):
    from django.db.models.fields import NOT_PROVIDED

    groups_field = AbstractAdminUser._meta.get_field('groups')
    groups_field.help_text = 'The groups this user belongs to. A user will get all permissions granted to each of their groups.'

    last_login_field = AbstractAdminUser._meta.get_field('last_login')
    last_login_field.blank = True
    last_login_field.null = True
    last_login_field.default = NOT_PROVIDED


class User(AbstractAdminUser):
    objects = UserManager()
