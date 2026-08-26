from django import forms
from django.contrib.auth import get_user_model
from django.contrib.auth.forms import AuthenticationForm
from django.core.exceptions import ValidationError

from .models import ActivityCategory, MemberProfile, ScoreRecord

User = get_user_model()

MAX_PHOTO_SIZE_BYTES = 5 * 1024 * 1024  # 5MB


class MemberRegistrationForm(forms.ModelForm):
    """
    Registration form: creates both the Django User and the MemberProfile.
    All fields are validated server-side; nothing here trusts the client.
    """

    bs_id = forms.CharField(max_length=32, required=True, label="BS ID")
    email = forms.EmailField(required=True)
    password = forms.CharField(widget=forms.PasswordInput, min_length=8, label="Password")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = MemberProfile
        fields = [
            "bs_id",
            "full_name",
            "profile_photo",
            "student_id",
            "department",
            "technology",
            "semester",
            "session",
            "phone",
            "email",
            "address",
            "blood_group",
            "joining_date",
            "registration_number",
            "biography",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "biography": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_bs_id(self):
        bs_id = self.cleaned_data["bs_id"].strip()
        if MemberProfile.objects.filter(bs_id__iexact=bs_id).exists():
            raise ValidationError("A member with this BS ID is already registered.")
        return bs_id

    def clean_email(self):
        email = self.cleaned_data["email"].strip().lower()
        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError("An account with this email already exists.")
        return email

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo:
            if photo.size > MAX_PHOTO_SIZE_BYTES:
                raise ValidationError("Profile photo must be smaller than 5MB.")
            content_type = getattr(photo, "content_type", "")
            if content_type and not content_type.startswith("image/"):
                raise ValidationError("Uploaded file must be an image.")
        return photo

    def clean(self):
        cleaned = super().clean()
        password = cleaned.get("password")
        confirm_password = cleaned.get("confirm_password")
        if password and confirm_password and password != confirm_password:
            self.add_error("confirm_password", "Passwords do not match.")
        return cleaned

    def save(self, commit=True):
        """Creates the User first, then the MemberProfile pointed at it."""
        bs_id = self.cleaned_data["bs_id"]
        email = self.cleaned_data["email"]
        password = self.cleaned_data["password"]

        user = User(username=bs_id, email=email)
        user.set_password(password)
        user.save()

        member = super().save(commit=False)
        member.user = user
        member.status = MemberProfile.Status.CURRENT_STUDENT
        if commit:
            member.save()
        return member


class MemberLoginForm(AuthenticationForm):
    """Thin wrapper so the template can show 'BS ID' instead of 'username'."""

    username = forms.CharField(label="BS ID or Username")


class MemberProfileSelfEditForm(forms.ModelForm):
    """
    Fields a student is allowed to edit about themselves.
    bs_id, status, and anything score/rank related is deliberately excluded.
    """

    class Meta:
        model = MemberProfile
        fields = ["profile_photo", "phone", "address", "biography", "email"]
        widgets = {
            "address": forms.Textarea(attrs={"rows": 3}),
            "biography": forms.Textarea(attrs={"rows": 4}),
        }

    def clean_profile_photo(self):
        photo = self.cleaned_data.get("profile_photo")
        if photo and hasattr(photo, "size"):
            if photo.size > MAX_PHOTO_SIZE_BYTES:
                raise ValidationError("Profile photo must be smaller than 5MB.")
        return photo


class AdminMemberEditForm(forms.ModelForm):
    """Full profile edit, for administrators. bs_id stays read-only by view logic, not just here."""

    class Meta:
        model = MemberProfile
        fields = [
            "full_name",
            "profile_photo",
            "student_id",
            "department",
            "technology",
            "semester",
            "session",
            "phone",
            "email",
            "address",
            "blood_group",
            "joining_date",
            "registration_number",
            "biography",
            "status",
        ]
        widgets = {
            "joining_date": forms.DateInput(attrs={"type": "date"}),
            "address": forms.Textarea(attrs={"rows": 3}),
            "biography": forms.Textarea(attrs={"rows": 4}),
        }


class MemberStatusForm(forms.ModelForm):
    class Meta:
        model = MemberProfile
        fields = ["status"]


class ActivityCategoryForm(forms.ModelForm):
    class Meta:
        model = ActivityCategory
        fields = ["name", "description", "is_active"]
        widgets = {"description": forms.Textarea(attrs={"rows": 3})}


class ScoreRecordForm(forms.ModelForm):
    """
    Used by administrators to add/edit a score entry.
    member and category are validated server-side against real DB rows -
    never trust an id posted from the browser without this.
    """

    member = forms.ModelChoiceField(
        queryset=MemberProfile.objects.all().order_by("full_name"),
        label="Student",
        widget=forms.Select(attrs={"class": "form-select", "id": "id_member_select"}),
    )
    category = forms.ModelChoiceField(
        queryset=ActivityCategory.objects.filter(is_active=True),
        widget=forms.Select(attrs={"class": "form-select"}),
    )

    class Meta:
        model = ScoreRecord
        fields = ["member", "category", "activity_name", "points", "activity_date", "description"]
        widgets = {
            "activity_date": forms.DateInput(attrs={"type": "date", "class": "form-control"}),
            "description": forms.Textarea(attrs={"rows": 3, "class": "form-control"}),
            "activity_name": forms.TextInput(attrs={"class": "form-control"}),
            "points": forms.NumberInput(attrs={"class": "form-control"}),
        }
        help_texts = {
            "activity_date": "The date the activity actually happened - can be in the past.",
        }

class ScoreRecordFilterForm(forms.Form):
    """Non-model form for the admin score list's search/filter bar (all GET params)."""

    q = forms.CharField(
        required=False,
        label="Search (name or BS ID)",
        widget=forms.TextInput(attrs={"placeholder": "Search name or BS ID", "class": "form-control"}),
    )
    category = forms.ModelChoiceField(
        queryset=ActivityCategory.objects.all(),
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )
    date_from = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    date_to = forms.DateField(
        required=False,
        widget=forms.DateInput(attrs={"type": "date", "class": "form-control"}),
    )
    month = forms.IntegerField(
        required=False,
        min_value=1,
        max_value=12,
        widget=forms.NumberInput(attrs={"placeholder": "Month (1-12)", "class": "form-control"}),
    )
    year = forms.IntegerField(
        required=False,
        min_value=2026,
        max_value=2100,
        widget=forms.NumberInput(attrs={"placeholder": "Year", "class": "form-control"}),
    )

class MemberListFilterForm(forms.Form):
    """Non-model form for the public member list search/filter bar."""

    q = forms.CharField(
        required=False,
        label="Search",
        widget=forms.TextInput(attrs={"placeholder": "Search by name or BS ID", "class": "form-control"}),
    )
    sort = forms.ChoiceField(
        choices=[("points", "Points (high to low)"), ("name", "Name (A-Z)")],
        required=False,
        widget=forms.Select(attrs={"class": "form-select"}),
    )