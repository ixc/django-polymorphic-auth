Overview
========

Provides a polymorphic parent `User` model and several child models.

You can enable and disable child models without affecting foreign keys to the
the parent model, and avoid complicated schema and data migrations.

You can even have multiple child models active at the same time!


How It Works
============

The polymorphic parent model contains the bare minimum required by Django for a
user model. This is where your foreign keys will point to (via the
`AUTH_USER_MODEL` setting), and this allows you to avoid schema migrations when
changing child models.

Check out the [django-polymorphic][django-polymorphic] docs for more
information on the underlying system that makes this possible.


Plugins
=======

Several child models are also provided as user type plugins for common use
cases (email login, username login, etc.), along with a number of abstract
models and mixin classes that you can use to create your own plugins.

For example:

    # myproject/usertypes/foo/models.py

    from django.utils.translation import ugettext_lazy as _
    from polymorphic_auth.usertypes.email.abstract import AbstractUser

    class FooUser(AbstractUser):
        foo = models.CharField(unique=True)

        USERNAME_FIELD = 'foo'

        class Meta:
            verbose_name = _('user with foo login')
            verbose_name_plural = _('users with foo login')

Then just add your plugin to the `INSTALLED_APPS` setting and point to your
model in the `POLYMORPHIC_AUTH['DEFAULT_CHILD_MODEL']` setting:

    # myproject/settings.py

    AUTH_USER_MODEL = 'polymorphic_auth.User'
    INSTALLED_APPS += ('myproject.usertypes.foo', )
    POLYMORPHIC_AUTH = {'DEFAULT_CHILD_MODEL': 'foo.FooUser'}


ADMINS and MANAGERS
===================

The default app contains a `post_migrate` signal handler that will create
superuser and staff accounts for each name and email in the `ADMINS` and
`MANAGERS` settings, and write the credentials to `sys.stdout` (configurable).

Say goodbye to `./manage.py createsuperuser`!

To add support to your custom plugins, override the `AbstractUser.try_create`
classmethod and have it derive values for required fields from the `name` and
`email` kwargs.

For example:

    # myproject/usertypes/foo/models.py

    import re

    class FooUser(AbstractUser):
        ...

        @classmethod
        def try_create(self, **kwargs):
            email = kwargs.get('email', '')
            kwargs.setdefault('foo', re.sub(r'@.+', '', email))
            return super(FooUser, cls).try_create(**kwargs)


Admin
=====

If more than one plugin is installed, you will be asked which type of user you
want to create when adding a new user via the admin. If there is only one
plugin installed, it will take you directly to the change form for that plugin.

You can customise the admin class for your plugins:

    # myproject/usertypes/foo/admin.py

    from myproject.usertypes.foo.forms import FooForm
    from polymorphic_auth.admin import UserChildAdmin

    class EmailUserAdmin(UserChildAdmin):

        # define custom features here


TODO
====

  * Registration system for plugins, instead of hard coding the provided ones
    and checking `INSTALLED_APPS`.
  * Authentication backend that checks all registered plugins, not just the one
    assigned to `POLYMORPHIC_AUTH['DEFAULT_CHILD_MODEL']`.
  * Make `email` field case insensitive.


[django-polymorphic]: https://django-polymorphic.readthedocs.org/en/latest/index.html
