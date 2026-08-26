from django.conf import settings
from django.core.validators import FileExtensionValidator, MinValueValidator, MaxValueValidator
from django.db import models
from django.urls import reverse


def profile_photo_upload_path(instance, filename):
    """Store profile photos under media/members/profile_photos/<bs_id>/<filename>."""
    return f"members/profile_photos/{instance.bs_id}/{filename}"


class MemberProfile(models.Model):
    """
    One member/student record, tied 1-to-1 to a Django auth User.
    The BS ID (existing Bangladesh Scouts ID) is the single canonical
    identifier for the member - we never generate a separate member number.
    """

    class Status(models.TextChoices):
        CURRENT_STUDENT = "current", "Current Student"
        PASSED_OUT = "passed_out", "Passed Out"

    class BloodGroup(models.TextChoices):
        A_POS = "A+", "A+"
        A_NEG = "A-", "A-"
        B_POS = "B+", "B+"
        B_NEG = "B-", "B-"
        AB_POS = "AB+", "AB+"
        AB_NEG = "AB-", "AB-"
        O_POS = "O+", "O+"
        O_NEG = "O-", "O-"
        UNKNOWN = "unknown", "Unknown"

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="member_profile",
    )

    # --- Identity -------------------------------------------------------
    bs_id = models.CharField(
        "BS ID",
        max_length=32,
        unique=True,
        db_index=True,
        help_text="The member's existing Bangladesh Scouts ID. This is the only member identifier used in this app.",
    )
    full_name = models.CharField(max_length=150)
    profile_photo = models.ImageField(
        upload_to=profile_photo_upload_path,
        blank=True,
        null=True,
        validators=[FileExtensionValidator(allowed_extensions=["jpg", "jpeg", "png", "webp"])],
    )

    # --- Academic info ----------------------------------------------------
    student_id = models.CharField("Student ID / Roll Number", max_length=50, blank=True)
    department = models.CharField("Upodol", max_length=100, blank=True, db_index=True)
    technology = models.CharField("Technology / Trade", max_length=100, blank=True)
    semester = models.CharField(max_length=20, blank=True)
    session = models.CharField(max_length=20, blank=True, db_index=True)

    # --- Contact ----------------------------------------------------------
    phone = models.CharField(max_length=20, blank=True)
    email = models.EmailField(blank=True, help_text="Optional if it duplicates the account email.")
    address = models.TextField(blank=True)

    # --- Personal -----------------------------------------------------------
    blood_group = models.CharField(max_length=10, choices=BloodGroup.choices, default=BloodGroup.UNKNOWN, blank=True)
    joining_date = models.DateField(null=True, blank=True)
    registration_number = models.CharField(max_length=50, blank=True)
    biography = models.TextField("Short Biography", blank=True, max_length=1000)

    # --- Membership status --------------------------------------------------
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.CURRENT_STUDENT, db_index=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["full_name"]
        indexes = [
            models.Index(fields=["status", "session"]),
            models.Index(fields=["department", "session"]),
        ]

    def __str__(self):
        return f"{self.full_name} ({self.bs_id})"

    def get_absolute_url(self):
        return reverse("members:member_detail", args=[self.bs_id])

    # --- Derived data (thin wrappers around services.py) -----------------
    @property
    def total_points(self):
        from .services import get_total_points
        return get_total_points(self)


class ActivityCategory(models.Model):
    """Flexible, admin-managed category for scoring activities."""

    name = models.CharField(max_length=100, unique=True)
    description = models.TextField(blank=True)
    is_active = models.BooleanField(default=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["name"]
        verbose_name_plural = "Activity categories"

    def __str__(self):
        return self.name


class ScoreRecord(models.Model):
    """
    A single point entry earned by a member on a specific date.
    Totals and rankings are always derived from these rows - never
    stored as an editable running total.
    """

    member = models.ForeignKey(
        MemberProfile,
        on_delete=models.CASCADE,
        related_name="score_records",
    )
    category = models.ForeignKey(
        ActivityCategory,
        on_delete=models.PROTECT,
        related_name="score_records",
    )
    activity_name = models.CharField(max_length=150)
    points = models.IntegerField(validators=[MinValueValidator(-1000), MaxValueValidator(1000)])
    activity_date = models.DateField(
        db_index=True,
        help_text="The date the activity actually happened / points were earned (not the entry date).",
    )
    description = models.TextField(blank=True)
    added_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        related_name="score_records_added",
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-activity_date", "-created_at"]
        indexes = [
            models.Index(fields=["member", "activity_date"]),
            models.Index(fields=["category", "activity_date"]),
        ]

    def __str__(self):
        return f"{self.member.bs_id} | {self.activity_date} | {self.activity_name} ({self.points:+d})"
