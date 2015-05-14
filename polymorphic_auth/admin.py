from django.conf import settings
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.forms import UserChangeForm, UserCreationForm
from polymorphic_auth.models import User
from polymorphic.admin import \
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


def create_user_creation_form(user_model, user_model_fields):
    """
    Creates a creation form for the user model and model fields.
    """
    class CreationForm(UserCreationForm):
        class Meta:
            model = user_model
            fields = user_model_fields
    return CreationForm


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
    base_form = UserChangeForm
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
        from polymorphic_auth.usertypes.email.admin import EmailUserAdmin
        from polymorphic_auth.usertypes.email.models import EmailUser
        from polymorphic_auth.usertypes.username.admin import UsernameUserAdmin
        from polymorphic_auth.usertypes.username.models import UsernameUser
        child_models = []
        if 'polymorphic_auth.usertypes.email' in \
                settings.INSTALLED_APPS:
            child_models.append((EmailUser, EmailUserAdmin))
        if 'polymorphic_auth.usertypes.username' in \
                settings.INSTALLED_APPS:
            child_models.append((UsernameUser, UsernameUserAdmin))
        return child_models


admin.site.register(User, UserAdmin)
