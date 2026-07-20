from django.db import models


class MutHero(models.Model):
    title = models.CharField(max_length=150, default="রোভার মুট")
    description = models.TextField(blank=True, default="রোভার স্কাউট কার্যক্রমের স্মৃতি")
    image = models.ImageField(upload_to="mutgallery/hero/")

    def __str__(self):
        return "Mut Gallery Hero"

    class Meta:
        verbose_name = "Mut Gallery Hero"
        verbose_name_plural = "Mut Gallery Hero"


class MutImage(models.Model):
    title = models.CharField(max_length=200, blank=True, help_text="ছবির ক্যাপশন (alt text)")
    image = models.ImageField(upload_to="mutgallery/")

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title or f"Image #{self.pk}"