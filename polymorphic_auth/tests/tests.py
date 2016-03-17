"""
Tests for ``polymorphic_auth`` app.
"""

# WebTest API docs: http://webtest.readthedocs.org/en/latest/api.html

import re

from django.contrib.admin.sites import AdminSite
from django_webtest import WebTest
from django.core.urlresolvers import reverse

from polymorphic_auth.usertypes.email.models import EmailUser


class TestUserAdminBaseFieldsets(WebTest):
    """
    Tests a fix applied to ensure `base_fieldsets` are not
    lost in `UserChildAdmin` after calling `get_form()` with
    no existing instance (i.e. for a new user).
    """
    csrf_checks = False

    def setUp(self):
        self.site = AdminSite()
        self.staff_user = EmailUser.objects.create(
            email='staff@test.com',
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        self.staff_user.set_password('abc123')
        self.staff_user.save()

    def test_user_base_fieldsets(self):

        # edit our staff user and capture the form response.

        response = self.app.get(
            reverse('admin:polymorphic_auth_user_change',
                    args=(self.staff_user.pk,)),
            user=self.staff_user
        ).maybe_follow(user=self.staff_user)
        form1_response = response.form.text

        # create a another new user

        response = self.app.get(
            reverse('admin:polymorphic_auth_user_add'),
            user=self.staff_user
        ).maybe_follow(user=self.staff_user)
        form = response.form
        form['email'] = 'test@test.com'
        form['password1'] = 'testpassword'
        form['password2'] = 'testpassword'
        form.submit(user=self.staff_user)

        # Edit our staff user again and capture the form response.

        response = self.app.get(
            reverse('admin:polymorphic_auth_user_change',
                    args=(self.staff_user.pk,)),
            user=self.staff_user
        )
        form2_response = response.form.text

        # Rip out fields we expect to differ between the two responses.

        form1_response = re.sub(
            r'<input name="csrfmiddlewaretoken" (.*?)/>', '', form1_response)
        form1_response = re.sub(
            r'<input class="vTimeField" (.*?)/>', '', form1_response)
        form1_response = re.sub(
            r'<input id="initial-id_last_login_1" (.*?)/>', '', form1_response)

        form2_response = re.sub(
            r'<input name="csrfmiddlewaretoken" (.*?)/>', '', form2_response)
        form2_response = re.sub(
            r'<input class="vTimeField" (.*?)/>', '', form2_response)
        form2_response = re.sub(
            r'<input id="initial-id_last_login_1" (.*?)/>', '', form2_response)

        # Form output should be identical to the first.
        # This will not be the case if the base_fieldsets have been lost.

        self.assertEqual(form1_response, form2_response)
