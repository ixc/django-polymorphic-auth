from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from polymorphic_auth.models import User
from polymorphic.admin import \
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


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


class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created')
    list_display = (
        '__unicode__', 'first_name', 'last_name', 'is_active', 'is_staff',
        'is_superuser', 'created')
    search_fields = ('first_name', 'last_name')
    polymorphic_list = True

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
