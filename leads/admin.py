from django.contrib import admin

from .models import Lead, LeadActivity


@admin.register(Lead)
class LeadAdmin(admin.ModelAdmin):
    list_display = ("name", "phone", "email", "source", "status", "owner", "created_at")
    list_filter = ("status", "source")
    search_fields = ("name", "phone", "email")
    readonly_fields = ("id", "created_at", "updated_at")


@admin.register(LeadActivity)
class LeadActivityAdmin(admin.ModelAdmin):
    list_display = ("action", "lead_name_snapshot", "user", "old_value", "new_value", "created_at")
    list_filter = ("action",)
    readonly_fields = ("id", "created_at")