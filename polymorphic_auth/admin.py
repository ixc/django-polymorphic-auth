from django import forms, VERSION as django_version
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import \
    ReadOnlyPasswordHashField, UserChangeForm, UserCreationForm
from django.utils.translation import ugettext_lazy as _
from polymorphic_auth.models import User
from polymorphic.admin import \
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin
from polymorphic_auth import plugins


class ChildModelPluginPolymorphicParentModelAdmin(PolymorphicParentModelAdmin):
    """
    Get child models and choice labels from registered plugins.
    """

    child_model_plugin_class = None
    child_model_admin = None

    def get_child_models(self):
        """
        Get child models from registered plugins. Fallback to the child model
        admin and its base model if no plugins are registered.
        """
        child_models = []
        for plugin in self.child_model_plugin_class.get_plugins():
            child_models.append(
                (plugin.model, plugin.model_admin))

        if not child_models:
            child_models.append((
                self.child_model_admin.base_model,
                self.child_model_admin,
            ))
        return child_models

    def get_child_type_choices(self, request, action):
        """
        Override choice labels with ``verbose_name`` from plugins and sort.
        """
        # Get choices from the super class to check permissions.
        choices = super(ChildModelPluginPolymorphicParentModelAdmin, self) \
            .get_child_type_choices(request, action)
        # Update label with verbose name from plugins.
        plugins = self.child_model_plugin_class.get_plugins()
        if plugins:
            labels = {
                plugin.content_type.pk: plugin.verbose_name
                for plugin in plugins
            }
            choices = [(ctype, labels[ctype]) for ctype, _ in choices]
            return sorted(choices, key=lambda i: i[1])
        return choices


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
    filter_horizontal = ('groups', 'user_permissions',)

    def __init__(self, *args, **kwargs):
        super(UserChildAdmin, self).__init__(*args, **kwargs)
        self.orig_base_fieldsets = self.base_fieldsets

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
        else:
            # restore original base fieldsets
            self.base_fieldsets = self.orig_base_fieldsets
        defaults.update(kwargs)
        return super(UserChildAdmin, self).get_form(request, obj, **defaults)


class UserAdmin(ChildModelPluginPolymorphicParentModelAdmin, UserAdmin):
    base_model = User
    child_model_plugin_class = plugins.PolymorphicAuthChildModelPlugin
    child_model_admin = UserChildAdmin
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created')
    list_display = (
        '__str__', 'first_name', 'last_name', 'is_active', 'is_staff',
        'is_superuser', 'created')
    search_fields = ('first_name', 'last_name')
    polymorphic_list = True
    ordering = (base_model.USERNAME_FIELD,)

    def get_search_fields(self, request):
        """
        Append `modelname__usernamefield` to the list of fields to search.
        NB this code is a bit dumb - may break if the reverse relation isn't
        the same as model_name.
        """
        username_fields = []
        for model, _ in self.get_child_models():
            try:
                username_fields.append("%s__%s" % (model._meta.model_name, model.USERNAME_FIELD))
            except AttributeError:
                pass
        return self.search_fields + tuple(username_fields)



admin.site.register(User, UserAdmin)
