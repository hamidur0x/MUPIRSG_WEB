from django.db import models


class ContactPage(models.Model):
    hero_title = models.CharField(max_length=150, default="যোগাযোগ করুন")
    hero_description = models.TextField(blank=True, default="আমাদের সাথে যোগাযোগ করতে নিচের ফর্মটি ব্যবহার করুন")

    address = models.TextField(default="মুন্সীগঞ্জ পলিটেকনিক ইন্সটিটিউট, কমলাঘাট, মিরকাদিম, মুন্সীগঞ্জ")
    phone_one = models.CharField(max_length=30, blank=True)
    phone_two = models.CharField(max_length=30, blank=True)
    email = models.EmailField(blank=True)
    working_hours = models.CharField(max_length=150, default="শনিবার - বৃহস্পতিবার, সকাল ৯:০০ - বিকাল ৫:০০")

    form_submit_email = models.EmailField(help_text="ফর্ম সাবমিট হলে যে ইমেইলে পাঠাবে")

    map_embed_url = models.URLField(
        
        max_length=2000,
        blank=True,
        help_text="Google Maps embed URL (iframe src)"
    )

    def __str__(self):
        return "Contact Page"

    class Meta:
        verbose_name = "Contact Page"
        verbose_name_plural = "Contact Page"


class SocialLink(models.Model):
    ICON_CHOICES = [
        ("fab fa-facebook-f", "Facebook"),
        ("fab fa-twitter", "Twitter"),
        ("fab fa-instagram", "Instagram"),
        ("fab fa-youtube", "YouTube"),
        ("fab fa-whatsapp", "WhatsApp"),
        ("fab fa-linkedin-in", "LinkedIn"),
    ]

    icon_class = models.CharField(max_length=50, choices=ICON_CHOICES)
    url = models.URLField()

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.get_icon_class_display()


class FAQItem(models.Model):
    question = models.CharField(max_length=250)
    answer = models.TextField()

    order = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)

    class Meta:
        ordering = ["order"]

    def __str__(self):
        return self.question