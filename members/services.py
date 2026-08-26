"""
Business logic for the members app: totals, rankings, category
breakdowns, and date-based summaries. Kept out of views/templates so
it isn't duplicated across the admin score pages, the public ranking
page, and the student dashboard.
"""
from django.conf import settings
from django.db.models import Sum, Count
from django.db.models.functions import TruncMonth

from .models import MemberProfile, ScoreRecord


def get_total_points(member: MemberProfile) -> int:
    """Sum of every ScoreRecord for one member. Source of truth = rows, always."""
    total = member.score_records.aggregate(total=Sum("points"))["total"]
    return total or 0


def _ranking_queryset():
    """
    Members included in the ranking, controlled by
    settings.MEMBERS_RANKING_SCOPE:
      - "current"   -> only Current Student members (default)
      - "current_and_passed_out" -> current + passed out
      - "all"       -> every registered member
    """
    scope = getattr(settings, "MEMBERS_RANKING_SCOPE", "current")
    qs = MemberProfile.objects.all()
    if scope == "current":
        qs = qs.filter(status=MemberProfile.Status.CURRENT_STUDENT)
    elif scope == "current_and_passed_out":
        qs = qs.filter(status__in=[MemberProfile.Status.CURRENT_STUDENT, MemberProfile.Status.PASSED_OUT])
    # "all" -> no filter
    return qs


def get_ranking(limit=None):
    """
    Returns a list of dicts: [{"rank": 1, "member": <MemberProfile>, "total_points": 950}, ...]
    ordered by total_points DESC, using competition ranking (1224 style) for ties.
    Calculated fresh every call - nothing is stored.
    """
    qs = (
        _ranking_queryset()
        .annotate(total_points_annotated=Sum("score_records__points"))
        .order_by("-total_points_annotated", "full_name")
    )
    if limit:
        qs = qs[:limit]

    results = []
    prev_points = None
    prev_rank = 0
    for i, member in enumerate(qs, start=1):
        points = member.total_points_annotated or 0
        if points != prev_points:
            rank = i
        else:
            rank = prev_rank
        results.append({"rank": rank, "member": member, "total_points": points})
        prev_points = points
        prev_rank = rank
    return results


def get_member_rank(member: MemberProfile):
    """Find one member's current competition rank, or None if they're outside the ranking scope."""
    for entry in get_ranking():
        if entry["member"].pk == member.pk:
            return entry["rank"]
    return None


def get_category_breakdown(member: MemberProfile):
    """[{"category": <ActivityCategory>, "total": 80}, ...] ordered by category name."""
    rows = (
        member.score_records
        .values("category__id", "category__name")
        .annotate(total=Sum("points"))
        .order_by("category__name")
    )
    return [{"category_id": r["category__id"], "category_name": r["category__name"], "total": r["total"]} for r in rows]


def get_daily_breakdown(member: MemberProfile):
    """
    Score records grouped by activity_date, newest first.
    [{"date": date(...), "records": [ScoreRecord, ...], "daily_total": 25}, ...]
    """
    records = member.score_records.select_related("category", "added_by").order_by("-activity_date", "-created_at")
    grouped = {}
    order = []
    for r in records:
        if r.activity_date not in grouped:
            grouped[r.activity_date] = []
            order.append(r.activity_date)
        grouped[r.activity_date].append(r)

    return [
        {"date": d, "records": grouped[d], "daily_total": sum(r.points for r in grouped[d])}
        for d in order
    ]


def get_points_by_month(member: MemberProfile = None):
    """Aggregate points by month, optionally scoped to one member. Used in reports."""
    qs = ScoreRecord.objects.all() if member is None else member.score_records.all()
    rows = (
        qs.annotate(month=TruncMonth("activity_date"))
        .values("month")
        .annotate(total=Sum("points"))
        .order_by("month")
    )
    return list(rows)


def get_admin_dashboard_stats():
    """Aggregate counts/sums used on the admin dashboard overview cards."""
    members = MemberProfile.objects.all()
    scores = ScoreRecord.objects.all()
    top = get_ranking(limit=1)
    return {
        "total_members": members.count(),
        "current_students": members.filter(status=MemberProfile.Status.CURRENT_STUDENT).count(),
        "passed_out": members.filter(status=MemberProfile.Status.PASSED_OUT).count(),
        "total_points": scores.aggregate(total=Sum("points"))["total"] or 0,
        "total_score_records": scores.count(),
        "total_activity_categories": scores.values("category").distinct().count(),
        "top_member": top[0] if top else None,
    }


def get_points_by_category_report():
    """[{"category_name": ..., "total": ...}, ...] across all members, for the reports page."""
    rows = (
        ScoreRecord.objects.values("category__name")
        .annotate(total=Sum("points"), count=Count("id"))
        .order_by("-total")
    )
    return list(rows)
