from django.contrib import admin
from .models import ActivityPage, Activity


@admin.register(ActivityPage)
class ActivityPageAdmin(admin.ModelAdmin):
    list_display = ("hero_title", "updated_at")


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "order",
        "is_active",
        "created_at",
    )

    list_editable = (
        "order",
        "is_active",
    )

    search_fields = ("title",)