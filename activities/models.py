from django.db import models


class ActivityPage(models.Model):
    hero_title = models.CharField(max_length=150, default= 'আমাদের কার্যক্রম')
    hero_description = models.TextField()
    hero_image = models.ImageField(upload_to="activities/hero/")

    section_title = models.CharField(max_length=150, default= 'আমাদের কার্যক্রম')
    section_description = models.TextField()

    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return "Activities Page"


class Activity(models.Model):
    title = models.CharField(max_length=150)
    short_description = models.TextField()
    image = models.ImageField(upload_to="activities/")
    facebook_link = models.URLField(blank=True)

    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return self.title