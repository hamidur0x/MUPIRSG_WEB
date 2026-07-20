from django.db import models


class DikkhaHero(models.Model):
    title = models.CharField(max_length=150, default="দীক্ষা অনুষ্টান")
    description = models.TextField(blank=True, default="রোভার স্কাউট কার্যক্রমের স্মৃতি")
    image = models.ImageField(upload_to="dikkhagallery/hero/")

    def __str__(self):
        return "Dikkha Gallery Hero"

    class Meta:
        verbose_name = "Dikkha Gallery Hero"
        verbose_name_plural = "Dikkha Gallery Hero"


class DikkhaImage(models.Model):
    title = models.CharField(max_length=200, blank=True, help_text="ছবির ক্যাপশন (alt text)")
    image = models.ImageField(upload_to="dikkhagallery/")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Image #{self.pk}"