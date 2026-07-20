from django.contrib import admin
from .models import Council, CouncilMember


class CouncilMemberInline(admin.TabularInline):
    model = CouncilMember
    extra = 1
    fields = ("role", "name", "department", "subgroup", "image", "order")


@admin.register(Council)
class CouncilAdmin(admin.ModelAdmin):
    list_display = ("name", "year", "order", "is_active")
    list_editable = ("order", "is_active")
    inlines = [CouncilMemberInline]


@admin.register(CouncilMember)
class CouncilMemberAdmin(admin.ModelAdmin):
    list_display = ("name", "council", "role", "order")
    list_filter = ("council", "role")
    search_fields = ("name",)