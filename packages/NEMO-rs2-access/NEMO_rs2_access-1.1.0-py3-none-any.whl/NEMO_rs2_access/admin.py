import json

from django.contrib import admin
from django.contrib.admin import register
from django.utils.safestring import mark_safe

from NEMO_rs2_access.models import Cardholder, Reader, UserPreferencesDefaultProject
from NEMO_rs2_access.rs2 import sync_access, sync_readers


@admin.action(description="Sync all readers with RS2")
def admin_sync_readers(modeladmin, request, queryset):
    sync_readers()


@admin.action(description="Sync user access RS2")
def admin_sync_access(modeladmin, request, queryset):
    sync_access()


@register(UserPreferencesDefaultProject)
class UserPreferencesDefaultProjectAdmin(admin.ModelAdmin):
    list_display = ["get_user", "default_project"]
    list_filter = (("default_project", admin.RelatedOnlyFieldListFilter),)
    search_fields = [
        "user_preferences__user__first_name",
        "user_preferences__user__last_name",
        "user_preferences__user__username",
    ]

    @admin.display(description="User", ordering="user_preferences__user")
    def get_user(self, obj: UserPreferencesDefaultProject):
        return obj.user_preferences.user


@register(Reader)
class ReaderAdmin(admin.ModelAdmin):
    list_display = ["reader_id", "reader_name", "site_id", "area", "reader_type", "installed", "last_updated"]
    list_filter = [
        ("area", admin.RelatedOnlyFieldListFilter),
        "reader_type",
        "installed",
        "site_id",
    ]
    readonly_fields = ["reader_id", "reader_name", "site_id", "installed", "get_data", "created", "last_updated"]
    exclude = ["data"]
    search_fields = ["reader_name", "area__name"]
    actions = [admin_sync_readers, admin_sync_access]

    @admin.display(description="Data", ordering="data")
    def get_data(self, obj: Reader):
        result = json.dumps(obj.data, indent=4, sort_keys=True)
        result_str = f"<pre>{result}</pre>"
        return mark_safe(result_str)


@register(Cardholder)
class CardholderAdmin(admin.ModelAdmin):
    list_display = ["cardholder_id", "cardholder_name", "key_name", "key_value", "created", "last_updated"]
    readonly_fields = ["created", "last_updated"]
