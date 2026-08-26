from django.contrib import admin

from .models import ActivityCategory, MemberProfile, ScoreRecord


@admin.register(MemberProfile)
class MemberProfileAdmin(admin.ModelAdmin):
    list_display = ("full_name", "bs_id", "department", "session", "status", "total_points", "created_at")
    list_filter = ("status", "department", "session", "blood_group")
    search_fields = ("full_name", "bs_id", "student_id", "email", "user__username")
    ordering = ("full_name",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("user",)

    @admin.display(description="Total points")
    def total_points(self, obj):
        return obj.total_points


@admin.register(ActivityCategory)
class ActivityCategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "is_active", "created_at")
    list_filter = ("is_active",)
    search_fields = ("name",)
    ordering = ("name",)


@admin.register(ScoreRecord)
class ScoreRecordAdmin(admin.ModelAdmin):
    list_display = ("member", "activity_name", "category", "points", "activity_date", "added_by", "created_at")
    list_filter = ("category", "activity_date")
    search_fields = (
        "member__bs_id",
        "member__full_name",
        "activity_name",
        "category__name",
        "added_by__username",
    )
    ordering = ("-activity_date",)
    readonly_fields = ("created_at", "updated_at")
    autocomplete_fields = ("member", "category", "added_by")
    date_hierarchy = "activity_date"
