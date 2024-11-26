from django.contrib import admin
from django.utils.translation import ngettext
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from django.utils.safestring import mark_safe
from .models import Profile, Address

User = get_user_model()


class ProfileInline(admin.StackedInline):
    model = Profile
    can_delete = False
    verbose_name_plural = 'Profile'
    fk_name = 'user'

class AddressInline(admin.StackedInline):
    model = Address
    can_delete = False
    verbose_name_plural = 'Addresses'
    fk_name = 'user'
    
    
class CustomUserAdmin(UserAdmin):
    inlines = (ProfileInline, AddressInline )
    
    list_display = [
        "profile_image",
        "username",
        "email",
        "is_staff",
        "is_active",
        "last_login",
    ]
    list_select_related = ('profile',)
    list_display_links = ["email", "profile_image"]
    list_editable = ["is_staff", "is_active"]
    list_filter = ["is_staff", "is_superuser", "is_active"]
    actions = ["make_inactive"]
    readonly_fields = ('date_joined','last_login',)

    fieldsets = (
        (None, {"fields": ("password",)}),
        (
            "personal info",
            {
                "fields": ('username',)
            },
        ),
        (
            "contact info",
            {
                "fields": ("phone", "email",)
            },
        ),
        (
            "permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("important dates", {"fields": ("last_login", 'date_joined')}),
    )

    def make_inactive(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(
            request,
            ngettext("%d user is inactivated", "%d user are inactivated", updated)
            % updated,
            messages.SUCCESS,
        )

    make_inactive.short_description = "Make inactive"
    
    def profile_image(self, obj):
        return mark_safe(
            '<img src="{url}" width="{width}" height={height} />'.format(
                url=obj.profile.avatar.url,
                width=70,
                height=70,
            )
        )
    
    def get_inline_instances(self, request, obj=None):
        if not obj:
            return list()
        return super(CustomUserAdmin, self).get_inline_instances(request, obj)


admin.site.register(User, CustomUserAdmin)