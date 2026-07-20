from django.contrib import admin
from .models import MutHero, MutImage


@admin.register(MutHero)
class MutHeroAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        return not MutHero.objects.exists()


@admin.register(MutImage)
class MutImageAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)