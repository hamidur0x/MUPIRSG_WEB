from django.contrib import admin
from .models import HikingHero, HikingImage


@admin.register(HikingHero)
class HikingHeroAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        return not HikingHero.objects.exists()


@admin.register(HikingImage)
class HikingImageAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)