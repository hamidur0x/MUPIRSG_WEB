from django.contrib import admin
from .models import EventHero, EventImage


@admin.register(EventHero)
class EventHeroAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        return not EventHero.objects.exists()


@admin.register(EventImage)
class EventImageAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)