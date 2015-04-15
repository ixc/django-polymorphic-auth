from django.contrib import admin
from django_polymorphic_auth.models import User
from django_polymorphic_auth.usertypes.email.models import EmailUser
from django_polymorphic_auth.usertypes.username.models import UsernameUser
from polymorphic.admin import \
    PolymorphicParentModelAdmin, PolymorphicChildModelAdmin


class UserChildAdmin(PolymorphicChildModelAdmin):
    base_model = User
    # base_form = forms.ProductAdminForm


class EmailUserAdmin(UserChildAdmin):
    pass


class UsernameUserAdmin(UserChildAdmin):
    pass


class UserAdmin(PolymorphicParentModelAdmin):
    base_model = User
    child_models = (
        (EmailUser, EmailUserAdmin),
        (UsernameUser, UsernameUserAdmin),
    )
    list_filter = ('is_active', 'is_staff', 'is_superuser', 'created')
    list_display = (
        '__unicode__', 'is_active', 'is_staff', 'is_superuser', 'created')
    polymorphic_list = True


admin.site.register(User, UserAdmin)
