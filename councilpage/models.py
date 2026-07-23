from django.db import models
from django.core.exceptions import ValidationError


def validate_image_size(image):
    max_size_kb = 1500
    if image.size > max_size_kb * 1024:
        raise ValidationError(f"ছবির সাইজ {max_size_kb}KB-এর বেশি হতে পারবে না। বর্তমান সাইজ: {image.size // 1024}KB")


class Council(models.Model):
    name = models.CharField(max_length=150, help_text="যেমন: ১২তম ক্রু কাউন্সিল")
    year = models.CharField(max_length=50, blank=True, help_text="যেমন: ২০২৫-২৬")

    order = models.PositiveIntegerField(default=0, help_text="ট্যাব ক্রম")
    is_active = models.BooleanField(default=True)

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["order", "-created_at"]

    def __str__(self):
        return f"{self.name} ({self.year})" if self.year else self.name


class CouncilMember(models.Model):
    ROLE_CHOICES = [
        ("senior_rover", "সিনিয়র রোভার মেট"),
        ("rover_mate", "রোভার মেট"),
        ("assistant_rover_mate", "সহকারী রোভার মেট"),
    ]

    council = models.ForeignKey(Council, on_delete=models.CASCADE, related_name="members")
    role = models.CharField(max_length=30, choices=ROLE_CHOICES)

    name = models.CharField(max_length=150)
    department = models.CharField(max_length=150, blank=True)
    subgroup = models.CharField(max_length=100, blank=True)
    image = models.ImageField(
        upload_to="council/members/",
        blank=True,
        null=True,
        validators=[validate_image_size],
        help_text="সর্বোচ্চ ৫০০ KB সাইজের ছবি আপলোড করুন"
    )

    order = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["role", "order"]

    def __str__(self):
        return f"{self.name} - {self.get_role_display()}"