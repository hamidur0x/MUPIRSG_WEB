from django.contrib import admin
from .models import DikkhaHero, DikkhaImage


@admin.register(DikkhaHero)
class DikkhaHeroAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        return not DikkhaHero.objects.exists()


@admin.register(DikkhaImage)
class DikkhaImageAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)