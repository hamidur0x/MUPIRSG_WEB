from django.contrib import admin
from .models import HomePage

@admin.register(HomePage)
class HomePageAdmin(admin.ModelAdmin):
    list_display = ("title", "created_at")