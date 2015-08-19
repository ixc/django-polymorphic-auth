from django import forms, VERSION as django_version
from django.apps import apps
from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import \
    ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import User
from polymorphic.admin import \
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


def create_user_creation_form(user_model, user_model_fields):
    """
    Creates a creation form for the user model and model fields.
    """
    class _UserCreationForm(forms.ModelForm):
        """
        ``UserCreationForm`` without username field hardcoded for backward
        compatibility with Django < 1.8.
        """
        error_messages = {
            'password_mismatch': _("The two password fields didn't match."),
        }
        password1 = forms.CharField(label=_("Password"),
            widget=forms.PasswordInput)
        password2 = forms.CharField(label=_("Password confirmation"),
            widget=forms.PasswordInput,
            help_text=_("Enter the same password as above, for verification."))

        class Meta:
            model = user_model
            fields = user_model_fields

        def clean_password2(self):
            password1 = self.cleaned_data.get("password1")
            password2 = self.cleaned_data.get("password2")
            if password1 and password2 and password1 != password2:
                raise forms.ValidationError(
                    self.error_messages['password_mismatch'],
                    code='password_mismatch',
                )
            return password2

        def save(self, commit=True):
            user = super(_UserCreationForm, self).save(commit=False)
            user.set_password(self.cleaned_data["password1"])
            if commit:
                user.save()
            return user

    class CreationForm(UserCreationForm):
        class Meta:
            model = user_model
            fields = user_model_fields

    if django_version < (1, 8):
        return _UserCreationForm
    return CreationForm


class _UserChangeForm(forms.ModelForm):
    """
    ``UserChangeForm`` without username field hardcoded for backward
    compatibility with Django < 1.8.
    """
    password = ReadOnlyPasswordHashField(label=_("Password"),
        help_text=_("Raw passwords are not stored, so there is no way to see "
                    "this user's password, but you can change the password "
                    "using <a href=\"password/\">this form</a>."))

    class Meta:
        model = User
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(_UserChangeForm, self).__init__(*args, **kwargs)
        f = self.fields.get('user_permissions', None)
        if f is not None:
            f.queryset = f.queryset.select_related('content_type')

    def clean_password(self):
        # Regardless of what the user provides, return the initial value.
        # This is done here, rather than on the field, because the
        # field does not have access to the initial value
        return self.initial["password"]


class UserChildAdmin(PolymorphicChildModelAdmin):
    base_fieldsets = (
        ('Meta', {
            'classes': ('collapse', ),
            'fields': ('last_login', )
        }),
        ('Permissions', {
            'fields': (
                'is_active', 'is_staff', 'is_superuser', 'groups',
                'user_permissions')
        }),
    )
    base_form = _UserChangeForm if django_version < (1, 8) else UserChangeForm
    base_model = User

    def get_form(self, request, obj=None, **kwargs):
        """
        Use special form during user creation
        """
        defaults = {}
        # If an object has not yet been created we can ignorethe base_fieldsets and use a form
        # designed for user creation. This emulated the behaviour of the django user creation
        # process.
        if obj is None:
            self.base_fieldsets = None
            defaults['form'] = create_user_creation_form(self.model, (self.model.USERNAME_FIELD, ))
        defaults.update(kwargs)
        return super(UserChildAdmin, self).get_form(request, obj, **defaults)


class UserAdmin(PolymorphicParentModelAdmin, UserAdmin):
    base_model = User
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created')
    list_display = (
        '__unicode__', 'first_name', 'last_name', 'is_active', 'is_staff',
        'is_superuser', 'created')
    search_fields = ('first_name', 'last_name')
    polymorphic_list = True
    ordering = (base_model.USERNAME_FIELD,)

    def get_child_models(self):
        child_models = []

        def import_class(cl):
            d = cl.rfind(".")
            classname = cl[d+1:len(cl)]
            m = __import__(cl[0:d], globals(), locals(), [classname])
            return getattr(m, classname)

        # First try the auth model overrides via the
        # `POLYMORPHIC_AUTH_CHILD_MODELS` setting.
        for modelPath, adminModelPath in getattr(
                settings, 'POLYMORPHIC_AUTH_CHILD_MODELS', []):
            try:
                # try [appname].[modelname] format first
                model = apps.get_model(modelPath)
            except LookupError:
                # try full path to module
                model = import_class(modelPath)

            adminModel = import_class(adminModelPath)

            if model and adminModel:
                child_models.append((model, adminModel))

        if len(child_models) == 0:
            # fall back to auto-detection of built-in user types
            from polymorphic_auth.usertypes.email.admin import EmailUserAdmin
            from polymorphic_auth.usertypes.email.models import EmailUser
            from polymorphic_auth.usertypes.username.admin import UsernameUserAdmin
            from polymorphic_auth.usertypes.username.models import UsernameUser
            if 'polymorphic_auth.usertypes.email' in \
                    settings.INSTALLED_APPS:
                child_models.append((EmailUser, EmailUserAdmin))
            if 'polymorphic_auth.usertypes.username' in \
                    settings.INSTALLED_APPS:
                child_models.append((UsernameUser, UsernameUserAdmin))

        return child_models


admin.site.register(User, UserAdmin)
