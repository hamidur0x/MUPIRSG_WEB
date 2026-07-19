from django.db import models


class AboutPage(models.Model):
    hero_title = models.CharField(max_length=150, default="আমাদের সম্পর্কে")
    hero_description = models.TextField(blank=True)
    hero_image = models.ImageField(upload_to="about/")

    history_title = models.CharField(max_length=150, default="আমাদের ইতিহাস")
    history_paragraph_one = models.TextField(blank=True)
    history_paragraph_two = models.TextField(blank=True)
    history_image = models.ImageField(upload_to="about/")

    mission_section_title = models.CharField(max_length=150, default="আমাদের লক্ষ্য ও উদ্দেশ্য")

    mission_title = models.CharField(max_length=100, default="আমাদের মিশন")
    mission_text = models.TextField(blank=True)

    vision_title = models.CharField(max_length=100, default="আমাদের ভিশন")
    vision_text = models.TextField(blank=True)

    method_title = models.CharField(max_length=100, default="আমাদের পদ্ধতি")
    method_text = models.TextField(blank=True)

    values_title = models.CharField(max_length=100, default="আমাদের মূল্যবোধ")
    values_text = models.TextField(blank=True)

    def __str__(self):
        return "About Page"