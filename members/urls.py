from django.urls import path

from . import views

app_name = "members"

urlpatterns = [
    # --- Public ---------------------------------------------------------
    path("", views.member_list, name="member_list"),
    path("register/", views.register, name="register"),
    path("login/", views.MemberLoginView.as_view(), name="login"),
    path("logout/", views.member_logout, name="logout"),
    path("ranking/", views.ranking, name="ranking"),
    path("profile/<str:bs_id>/", views.member_detail, name="member_detail"),

    # --- Private student area (resolved from request.user, not the URL) -
    path("dashboard/", views.dashboard, name="dashboard"),
    path("dashboard/edit/", views.profile_edit, name="profile"),
    path("dashboard/scores/", views.score_history, name="score_history"),

    # --- Administrator area ----------------------------------------------
    path("admin/dashboard/", views.admin_dashboard, name="admin_dashboard"),
    path("admin/reports/", views.admin_reports, name="admin_reports"),

    path("admin/members/", views.admin_member_list, name="admin_member_list"),
    path("admin/members/<str:bs_id>/edit/", views.admin_member_edit, name="admin_member_edit"),
    path("admin/members/<str:bs_id>/status/", views.admin_member_status_change, name="admin_member_status_change"),

    path("admin/scores/", views.admin_score_list, name="admin_score_list"),
    path("admin/scores/add/", views.admin_score_add, name="admin_score_add"),
    path("admin/scores/<int:pk>/edit/", views.admin_score_edit, name="admin_score_edit"),
    path("admin/scores/<int:pk>/delete/", views.admin_score_delete, name="admin_score_delete"),

    path("admin/categories/", views.admin_category_list, name="admin_category_list"),
    path("admin/categories/add/", views.admin_category_add, name="admin_category_add"),
    path("admin/categories/<int:pk>/edit/", views.admin_category_edit, name="admin_category_edit"),
]
