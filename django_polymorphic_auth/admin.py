from django.conf import settings
from django.contrib import admin
from django.contrib.auth.forms import UserChangeForm
from django_polymorphic_auth.models import User
from django_polymorphic_auth.usertypes.email.models import EmailUser
from django_polymorphic_auth.usertypes.username.models import UsernameUser
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
        '__unicode__', 'is_active', 'is_staff', 'is_superuser', 'created')
    polymorphic_list = True

    def get_child_models(self):
        from django_polymorphic_auth.usertypes.email.admin import \
            EmailUserAdmin
        from django_polymorphic_auth.usertypes.username.admin import \
            UsernameUserAdmin
        child_models = []
        if 'django_polymorphic_auth.usertypes.email' in \
                settings.INSTALLED_APPS:
            child_models.append((EmailUser, EmailUserAdmin))
        if 'django_polymorphic_auth.usertypes.username' in \
                settings.INSTALLED_APPS:
            child_models.append((UsernameUser, UsernameUserAdmin))
        return child_models

admin.site.register(User, UserAdmin)
