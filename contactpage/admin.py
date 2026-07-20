from django.contrib import admin
from .models import ContactPage, SocialLink, FAQItem


@admin.register(ContactPage)
class ContactPageAdmin(admin.ModelAdmin):
    list_display = ("__str__", "email")

    def has_add_permission(self, request):
        return not ContactPage.objects.exists()


@admin.register(SocialLink)
class SocialLinkAdmin(admin.ModelAdmin):
    list_display = ("icon_class", "url", "order", "is_active")
    list_editable = ("order", "is_active")


@admin.register(FAQItem)
class FAQItemAdmin(admin.ModelAdmin):
    list_display = ("question", "order", "is_active")
    list_editable = ("order", "is_active")