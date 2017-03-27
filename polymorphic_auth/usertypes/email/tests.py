from django_webtest import WebTest

from django.core.urlresolvers import reverse

from .models import EmailUser


class TestEmailUser(WebTest):

    def setUp(self):
        self.superuser = EmailUser.objects.create(
            email='superuser@test.com',
            is_staff=True,
            is_active=True,
            is_superuser=True,
        )
        self.superuser.set_password('abc123')
        self.superuser.save()

    def test_cannot_create_user_with_same_email(self):
        # Cannot create a user with an exactly matching email
        try:
            EmailUser.objects.create(email='superuser@test.com')
        except Exception, ex:
            self.assertTrue('matches existing users' in ex.message)

        # Cannot create a user with an equivalent email when case is ignored
        try:
            EmailUser.objects.create(email='Superuser@test.com')
        except Exception, ex:
            self.assertTrue('matches existing users' in ex.message)

    def test_cannot_modify_user_to_have_same_email(self):
        user = EmailUser.objects.create(email='another@test.com')
        # Cannot create a user with an exactly matching email
        user.email = 'superuser@test.com'
        try:
            user.save()
        except Exception, ex:
            self.assertTrue('matches existing users' in ex.message)

        # Cannot create a user with an equivalent email when case is ignored
        user.email = 'Superuser@test.com'
        try:
            user.save()
        except Exception, ex:
            self.assertTrue('matches existing users' in ex.message)

    def test_can_modify_existing_user(self):
        self.superuser.first_name = 'Sir'
        self.superuser.last_name = 'Test'
        self.superuser.save()
        reloaded_superuser = EmailUser.objects.get(pk=self.superuser.pk)
        self.assertEqual('Sir', reloaded_superuser.first_name)
        self.assertEqual('Test', reloaded_superuser.last_name)

    def test_cannot_create_user_with_same_email_in_admin(self):
        response = self.app.get(
            reverse('admin:polymorphic_auth_user_add'),
            user=self.superuser
        ).maybe_follow()
        form = response.form

        # Cannot create a user with an exactly matching email
        form['email'] = 'superuser@test.com'
        form['password1'] = 'testpassword'
        form['password2'] = 'testpassword'
        response = form.submit(user=self.superuser)
        self.assertTrue(
            # Default form field error on 'email' field
            'A user with that email address already exists' in response.text)
        self.assertTrue(
            # General error on "username" identifier field
            'A user with that email already exists' in response.text)

        # Cannot create a user with an equivalent email when case is ignored
        form['email'] = 'Superuser@test.com'
        form['password1'] = 'testpassword'
        form['password2'] = 'testpassword'
        response = form.submit(user=self.superuser)
        self.assertFalse(
            # Default form field error on 'email' field NOT PRESENT
            'A user with that email address already exists' in response.text)
        self.assertTrue(
            # General error on "username" identifier field
            'A user with that email already exists' in response.text)

    def test_cannot_modify_user_to_have_same_email_in_admin(self):
        user = EmailUser.objects.create(email='another@test.com')

        response = self.app.get(
            reverse('admin:polymorphic_auth_user_change',
                    args=(user.pk,)),
            user=self.superuser
        ).maybe_follow()
        form = response.form

        # Cannot modify a user to have an exactly matching email
        form['email'] = 'superuser@test.com'
        response = form.submit(user=self.superuser)
        self.assertTrue(
            # Default form field error on 'email' field
            'A user with that email address already exists' in response.text)
        self.assertTrue(
            # General error on "username" identifier field
            'A user with that email already exists' in response.text)

        # Cannot modify a user to have an equivalent email when case is ignored
        form['email'] = 'Superuser@test.com'
        response = form.submit(user=self.superuser)
        self.assertFalse(
            # Default form field error on 'email' field NOT PRESENT
            'A user with that email address already exists' in response.text)
        self.assertTrue(
            # General error on "username" identifier field
            'A user with that email already exists' in response.text)

    def test_can_modify_existing_user_in_admin(self):
        self.superuser.first_name = 'Sir Test'
        response = self.app.get(
            reverse('admin:polymorphic_auth_user_change',
                    args=(self.superuser.pk,)),
            user=self.superuser
        ).maybe_follow()
        form = response.form
        form['first_name'] = 'Sir'
        form['last_name'] = 'Test'
        response = form.submit()
        reloaded_superuser = EmailUser.objects.get(pk=self.superuser.pk)
        self.assertEqual('Sir', reloaded_superuser.first_name)
        self.assertEqual('Test', reloaded_superuser.last_name)
