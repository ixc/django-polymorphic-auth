Overview
========

Provides a replacement `User` model that is polymorphic. You can easily replace
the active user model without any complicated schema and data migrations, or
even have multiple user types with their own model active at the same time.


How It Works
============

There is a concrete polymorphic parent model that contains the bare minimum
required by Django for a user model. This is where your foreign key fields will
point to, and this allows you to avoid schema migrations when replacing the
user model.

There are also several mixin classes that add fields and functionality, and
these can be used in combination to compose one or more polymorphic child
models.

Check out the [django-polymorphic][django-polymorphic] docs for more
information on the underlying system that makes this possible.


Plugins
=======

Two polymorphic child models are provided as optional plugins, one for email
based authentication, and another for username based authentication. You can
easily create your own plugins.

For example:

    # myproject/usertypes/foo/models.py

    from django.utils.translation import ugettext_lazy as _
    from polymorphic_auth.usertypes.email.abstract import AbstractEmailUser

    class FooUser(AbstractEmailUser):
        foo = models.CharField(unique=True)

        USERNAME_FIELD = 'foo'

        class Meta:
            verbose_name = _('user with foo login')
            verbose_name_plural = _('users with foo login')

Then just add your plugin to the `INSTALLED_APPS` setting and point to the new
model in the `AUTH_USER_MODEL` setting:

    # myproject/settings.py

    INSTALLED_APPS += ('myproject.usertypes.foo', )
    AUTH_USER_MODEL = 'foo.FooUser'


Admin
=====

If two or more plugins are installed, you will be asked which type of user you
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
    assigned to `AUTH_USER_MODEL`.


[django-polymorphic]: https://django-polymorphic.readthedocs.org/en/latest/index.html
