from django.contrib import messages
from django.contrib.auth import login as auth_login, logout as auth_logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.core.paginator import Paginator
from django.db.models import Q, Sum
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import (
    ActivityCategoryForm,
    AdminMemberEditForm,
    MemberListFilterForm,
    MemberLoginForm,
    MemberProfileSelfEditForm,
    MemberRegistrationForm,
    MemberStatusForm,
    ScoreRecordFilterForm,
    ScoreRecordForm,
)
from .models import ActivityCategory, MemberProfile, ScoreRecord
from .permissions import admin_required, member_required
from .services import (
    get_admin_dashboard_stats,
    get_category_breakdown,
    get_daily_breakdown,
    get_member_rank,
    get_points_by_category_report,
    get_ranking,
    get_total_points,
)

PAGE_SIZE = 20


# ---------------------------------------------------------------------------
# Public / auth
# ---------------------------------------------------------------------------

def register(request):
    if request.user.is_authenticated:
        return redirect("members:dashboard")

    if request.method == "POST":
        form = MemberRegistrationForm(request.POST, request.FILES)
        if form.is_valid():
            member = form.save()
            auth_login(request, member.user)
            messages.success(request, "Welcome! Your account has been created.")
            return redirect("members:dashboard")
    else:
        form = MemberRegistrationForm()

    return render(request, "members/register.html", {"form": form})


class MemberLoginView(LoginView):
    template_name = "members/login.html"
    authentication_form = MemberLoginForm
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy("members:dashboard")


@login_required
def member_logout(request):
    auth_logout(request)
    return redirect("members:login")


def member_list(request):
    form = MemberListFilterForm(request.GET or None)
    qs = MemberProfile.objects.annotate(total_points_annotated=Sum("score_records__points"))

    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            qs = qs.filter(Q(full_name__icontains=q) | Q(bs_id__icontains=q))
        sort = form.cleaned_data.get("sort") or "points"
        if sort == "name":
            qs = qs.order_by("full_name")
        else:
            qs = qs.order_by("-total_points_annotated", "full_name")
    else:
        qs = qs.order_by("-total_points_annotated", "full_name")

    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(request, "members/member_list.html", {"form": form, "page_obj": page_obj})


def member_detail(request, bs_id):
    """Public profile page - only public-safe fields are shown in the template."""
    member = get_object_or_404(MemberProfile, bs_id=bs_id)
    context = {
        "member": member,
        "total_points": get_total_points(member),
        "rank": get_member_rank(member),
        "category_breakdown": get_category_breakdown(member),
    }
    return render(request, "members/member_detail.html", context)


def ranking(request):
    return render(request, "members/ranking.html", {"ranking": get_ranking()})


# ---------------------------------------------------------------------------
# Student (private) area
# ---------------------------------------------------------------------------

@member_required
def dashboard(request):
    """
    The private dashboard. The member is ALWAYS resolved from
    request.user.member_profile - never from a URL parameter - so
    there's no BS-ID-in-the-URL access pattern to exploit.
    """
    member = request.user.member_profile
    context = {
        "member": member,
        "total_points": get_total_points(member),
        "rank": get_member_rank(member),
        "category_breakdown": get_category_breakdown(member),
        "daily_breakdown": get_daily_breakdown(member)[:5],
    }
    return render(request, "members/dashboard.html", context)


@member_required
def profile_edit(request):
    member = request.user.member_profile
    if request.method == "POST":
        form = MemberProfileSelfEditForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile updated.")
            return redirect("members:profile")
    else:
        form = MemberProfileSelfEditForm(instance=member)
    return render(request, "members/profile.html", {"form": form, "member": member})


@member_required
def score_history(request):
    member = request.user.member_profile
    records = member.score_records.select_related("category", "added_by")

    date_from = request.GET.get("date_from")
    date_to = request.GET.get("date_to")
    month = request.GET.get("month")
    year = request.GET.get("year")
    category_id = request.GET.get("category")

    if date_from:
        records = records.filter(activity_date__gte=date_from)
    if date_to:
        records = records.filter(activity_date__lte=date_to)
    if month:
        records = records.filter(activity_date__month=month)
    if year:
        records = records.filter(activity_date__year=year)
    if category_id:
        records = records.filter(category_id=category_id)

    paginator = Paginator(records.order_by("-activity_date"), PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))

    return render(
        request,
        "members/score_history.html",
        {
            "member": member,
            "page_obj": page_obj,
            "categories": ActivityCategory.objects.filter(is_active=True),
        },
    )


# ---------------------------------------------------------------------------
# Administrator area
# ---------------------------------------------------------------------------

@admin_required
def admin_dashboard(request):
    stats = get_admin_dashboard_stats()
    recent_members = MemberProfile.objects.order_by("-created_at")[:5]
    recent_scores = ScoreRecord.objects.select_related("member", "category").order_by("-created_at")[:5]
    return render(
        request,
        "members/admin_dashboard.html",
        {"stats": stats, "recent_members": recent_members, "recent_scores": recent_scores},
    )


@admin_required
def admin_member_list(request):
    q = request.GET.get("q", "")
    qs = MemberProfile.objects.annotate(total_points_annotated=Sum("score_records__points"))
    if q:
        qs = qs.filter(Q(full_name__icontains=q) | Q(bs_id__icontains=q) | Q(student_id__icontains=q))
    qs = qs.order_by("full_name")

    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "members/admin_members.html", {"page_obj": page_obj, "q": q})


@admin_required
def admin_member_edit(request, bs_id):
    member = get_object_or_404(MemberProfile, bs_id=bs_id)
    if request.method == "POST":
        form = AdminMemberEditForm(request.POST, request.FILES, instance=member)
        if form.is_valid():
            form.save()
            messages.success(request, "Member updated.")
            return redirect("members:admin_member_list")
    else:
        form = AdminMemberEditForm(instance=member)
    return render(request, "members/admin_member_edit.html", {"form": form, "member": member})


@admin_required
@require_POST
def admin_member_status_change(request, bs_id):
    """POST-only: status changes must never happen via a GET link."""
    member = get_object_or_404(MemberProfile, bs_id=bs_id)
    form = MemberStatusForm(request.POST, instance=member)
    if form.is_valid():
        form.save()
        messages.success(request, f"{member.full_name}'s status updated to {member.get_status_display()}.")
    return redirect("members:admin_member_list")


@admin_required
def admin_score_list(request):
    form = ScoreRecordFilterForm(request.GET or None)
    qs = ScoreRecord.objects.select_related("member", "category", "added_by")

    if form.is_valid():
        q = form.cleaned_data.get("q")
        if q:
            qs = qs.filter(Q(member__full_name__icontains=q) | Q(member__bs_id__icontains=q))
        if form.cleaned_data.get("category"):
            qs = qs.filter(category=form.cleaned_data["category"])
        if form.cleaned_data.get("date_from"):
            qs = qs.filter(activity_date__gte=form.cleaned_data["date_from"])
        if form.cleaned_data.get("date_to"):
            qs = qs.filter(activity_date__lte=form.cleaned_data["date_to"])
        if form.cleaned_data.get("month"):
            qs = qs.filter(activity_date__month=form.cleaned_data["month"])
        if form.cleaned_data.get("year"):
            qs = qs.filter(activity_date__year=form.cleaned_data["year"])

    qs = qs.order_by("-activity_date", "-created_at")
    paginator = Paginator(qs, PAGE_SIZE)
    page_obj = paginator.get_page(request.GET.get("page"))
    return render(request, "members/admin_scores.html", {"form": form, "page_obj": page_obj})


@admin_required
def admin_score_add(request):
    if request.method == "POST":
        form = ScoreRecordForm(request.POST)
        if form.is_valid():
            record = form.save(commit=False)
            record.added_by = request.user
            record.save()
            messages.success(request, "Score added.")
            return redirect("members:admin_score_list")
    else:
        form = ScoreRecordForm()
    return render(request, "members/score_form.html", {"form": form, "mode": "add"})


@admin_required
def admin_score_edit(request, pk):
    record = get_object_or_404(ScoreRecord, pk=pk)
    if request.method == "POST":
        form = ScoreRecordForm(request.POST, instance=record)
        if form.is_valid():
            form.save()
            messages.success(request, "Score updated.")
            return redirect("members:admin_score_list")
    else:
        form = ScoreRecordForm(instance=record)
    return render(request, "members/score_form.html", {"form": form, "mode": "edit", "record": record})


@admin_required
@require_POST
def admin_score_delete(request, pk):
    record = get_object_or_404(ScoreRecord, pk=pk)
    record.delete()
    messages.success(request, "Score record deleted.")
    return redirect("members:admin_score_list")


@admin_required
def admin_category_list(request):
    categories = ActivityCategory.objects.all()
    return render(request, "members/activity_categories.html", {"categories": categories})


@admin_required
def admin_category_add(request):
    if request.method == "POST":
        form = ActivityCategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, "Category created.")
            return redirect("members:admin_category_list")
    else:
        form = ActivityCategoryForm()
    return render(request, "members/category_form.html", {"form": form, "mode": "add"})


@admin_required
def admin_category_edit(request, pk):
    category = get_object_or_404(ActivityCategory, pk=pk)
    if request.method == "POST":
        form = ActivityCategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, "Category updated.")
            return redirect("members:admin_category_list")
    else:
        form = ActivityCategoryForm(instance=category)
    return render(request, "members/category_form.html", {"form": form, "mode": "edit", "category": category})


@admin_required
def admin_reports(request):
    context = {
        "stats": get_admin_dashboard_stats(),
        "points_by_category": get_points_by_category_report(),
        "ranking_top10": get_ranking(limit=10),
    }
    return render(request, "members/reports.html", context)
