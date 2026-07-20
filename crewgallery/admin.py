from django.contrib import admin
from .models import CrewHero, CrewImage


@admin.register(CrewHero)
class CrewHeroAdmin(admin.ModelAdmin):
    list_display = ("title",)

    def has_add_permission(self, request):
        # keep this a singleton
        return not CrewHero.objects.exists()


@admin.register(CrewImage)
class CrewImageAdmin(admin.ModelAdmin):
    list_display = ("title", "order", "is_active", "created_at")
    list_editable = ("order", "is_active")
    list_filter = ("is_active",)
    search_fields = ("title",)