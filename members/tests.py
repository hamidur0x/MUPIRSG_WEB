import datetime

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from .models import ActivityCategory, MemberProfile, ScoreRecord
from .services import get_ranking, get_total_points

User = get_user_model()


def make_member(bs_id, full_name, username=None, status=MemberProfile.Status.CURRENT_STUDENT):
    user = User.objects.create_user(username=username or bs_id, password="testpass123")
    return MemberProfile.objects.create(user=user, bs_id=bs_id, full_name=full_name, status=status)


class RegistrationTests(TestCase):
    def setUp(self):
        self.url = reverse("members:register")
        self.valid_data = {
            "bs_id": "BS10001",
            "full_name": "Test Student",
            "student_id": "S1",
            "department": "CSE",
            "technology": "Computer",
            "semester": "1",
            "session": "2024",
            "phone": "0123456789",
            "email": "student1@example.com",
            "address": "Somewhere",
            "blood_group": "O+",
            "biography": "Hi",
            "password": "StrongPass123",
            "confirm_password": "StrongPass123",
        }

    def test_valid_registration_creates_user_and_profile(self):
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(User.objects.filter(username="BS10001").exists())
        member = MemberProfile.objects.get(bs_id="BS10001")
        self.assertEqual(member.status, MemberProfile.Status.CURRENT_STUDENT)
        self.assertEqual(get_total_points(member), 0)

    def test_duplicate_bs_id_rejected(self):
        make_member("BS10001", "Existing Student")
        response = self.client.post(self.url, self.valid_data)
        self.assertEqual(response.status_code, 200)  # re-renders form with errors
        self.assertContains(response, "already registered")

    def test_invalid_email_rejected(self):
        data = {**self.valid_data, "email": "not-an-email"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertFalse(User.objects.filter(username="BS10001").exists())

    def test_password_mismatch_rejected(self):
        data = {**self.valid_data, "confirm_password": "Different123"}
        response = self.client.post(self.url, data)
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, "Passwords do not match")


class AuthenticationTests(TestCase):
    def setUp(self):
        self.member = make_member("BS20001", "Login Student")

    def test_student_login(self):
        response = self.client.post(
            reverse("members:login"), {"username": "BS20001", "password": "testpass123"}
        )
        self.assertEqual(response.status_code, 302)

    def test_student_logout(self):
        self.client.login(username="BS20001", password="testpass123")
        response = self.client.get(reverse("members:logout"))
        self.assertEqual(response.status_code, 302)
        response = self.client.get(reverse("members:dashboard"))
        self.assertNotEqual(response.status_code, 200)

    def test_unauthorized_dashboard_access_redirects_to_login(self):
        response = self.client.get(reverse("members:dashboard"))
        self.assertEqual(response.status_code, 302)
        self.assertIn(reverse("members:login"), response.url)


class SecurityTests(TestCase):
    def setUp(self):
        self.member_a = make_member("BS30001", "Student A")
        self.member_b = make_member("BS30002", "Student B")
        self.admin_user = User.objects.create_user(
            username="admin1", password="adminpass123", is_staff=True
        )

    def test_student_cannot_reach_another_students_private_data_via_url(self):
        # There is no URL like /dashboard/<bs_id>/ at all - the dashboard
        # always resolves the member from request.user. Confirm student B's
        # own login only ever surfaces student B's own data.
        self.client.login(username="BS30002", password="testpass123")
        response = self.client.get(reverse("members:dashboard"))
        self.assertContains(response, self.member_b.full_name)
        self.assertNotContains(response, self.member_a.full_name)

    def test_student_cannot_add_scores(self):
        self.client.login(username="BS30001", password="testpass123")
        category = ActivityCategory.objects.create(name="Test Category")
        response = self.client.post(
            reverse("members:admin_score_add"),
            {
                "member": self.member_a.pk,
                "category": category.pk,
                "activity_name": "Hack attempt",
                "points": 100,
                "activity_date": "2026-01-01",
            },
        )
        self.assertEqual(response.status_code, 403)
        self.assertEqual(ScoreRecord.objects.count(), 0)

    def test_student_cannot_edit_scores(self):
        category = ActivityCategory.objects.create(name="Test Category")
        record = ScoreRecord.objects.create(
            member=self.member_a, category=category, activity_name="X", points=10,
            activity_date=datetime.date(2026, 1, 1),
        )
        self.client.login(username="BS30001", password="testpass123")
        response = self.client.get(reverse("members:admin_score_edit", args=[record.pk]))
        self.assertEqual(response.status_code, 403)

    def test_student_cannot_change_status(self):
        self.client.login(username="BS30001", password="testpass123")
        response = self.client.post(
            reverse("members:admin_member_status_change", args=[self.member_a.bs_id]),
            {"status": "passed_out"},
        )
        self.assertEqual(response.status_code, 403)
        self.member_a.refresh_from_db()
        self.assertEqual(self.member_a.status, MemberProfile.Status.CURRENT_STUDENT)

    def test_admin_can_change_status(self):
        self.client.login(username="admin1", password="adminpass123")
        response = self.client.post(
            reverse("members:admin_member_status_change", args=[self.member_a.bs_id]),
            {"status": "passed_out"},
        )
        self.assertEqual(response.status_code, 302)
        self.member_a.refresh_from_db()
        self.assertEqual(self.member_a.status, MemberProfile.Status.PASSED_OUT)


class ScoringTests(TestCase):
    def setUp(self):
        self.member = make_member("BS40001", "Score Student")
        self.category = ActivityCategory.objects.get(name="Crew Meeting")
        self.admin_user = User.objects.create_user(
            username="admin2", password="adminpass123", is_staff=True
        )

    def test_add_score_and_total_calculation(self):
        ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="A", points=10,
            activity_date=datetime.date(2026, 8, 25), added_by=self.admin_user,
        )
        ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="B", points=15,
            activity_date=datetime.date(2026, 8, 25), added_by=self.admin_user,
        )
        ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="C", points=20,
            activity_date=datetime.date(2026, 8, 28), added_by=self.admin_user,
        )
        self.assertEqual(get_total_points(self.member), 45)

    def test_edit_score_updates_total(self):
        record = ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="A", points=10,
            activity_date=datetime.date(2026, 8, 25),
        )
        record.points = 30
        record.save()
        self.assertEqual(get_total_points(self.member), 30)

    def test_delete_score_updates_total(self):
        r1 = ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="A", points=10,
            activity_date=datetime.date(2026, 8, 25),
        )
        ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="B", points=15,
            activity_date=datetime.date(2026, 8, 25),
        )
        r1.delete()
        self.assertEqual(get_total_points(self.member), 15)

    def test_historical_activity_date_preserved(self):
        record = ScoreRecord.objects.create(
            member=self.member, category=self.category, activity_name="Old event", points=25,
            activity_date=datetime.date(2026, 8, 10),
        )
        self.assertEqual(record.activity_date, datetime.date(2026, 8, 10))
        self.assertNotEqual(record.created_at.date(), record.activity_date)


class RankingTests(TestCase):
    def setUp(self):
        self.category = ActivityCategory.objects.create(name="General")

    def _score(self, member, points):
        ScoreRecord.objects.create(
            member=member, category=self.category, activity_name="X", points=points,
            activity_date=datetime.date(2026, 8, 1),
        )

    def test_correct_ranking_order(self):
        a = make_member("BS50001", "A")
        b = make_member("BS50002", "B")
        self._score(a, 100)
        self._score(b, 50)
        ranking = get_ranking()
        self.assertEqual(ranking[0]["member"].bs_id, "BS50001")
        self.assertEqual(ranking[0]["rank"], 1)
        self.assertEqual(ranking[1]["rank"], 2)

    def test_ranking_changes_after_score_update(self):
        a = make_member("BS50003", "A2")
        b = make_member("BS50004", "B2")
        self._score(a, 10)
        self._score(b, 50)
        ranking = get_ranking()
        self.assertEqual(ranking[0]["member"].bs_id, "BS50004")

        self._score(a, 100)  # a now leads
        ranking = get_ranking()
        self.assertEqual(ranking[0]["member"].bs_id, "BS50003")

    def test_tied_scores_use_competition_ranking(self):
        a = make_member("BS50005", "TieA")
        b = make_member("BS50006", "TieB")
        c = make_member("BS50007", "TieC")
        d = make_member("BS50008", "TieD")
        self._score(a, 500)
        self._score(b, 450)
        self._score(c, 450)
        self._score(d, 400)

        ranking = {entry["member"].bs_id: entry["rank"] for entry in get_ranking()}
        self.assertEqual(ranking["BS50005"], 1)
        self.assertEqual(ranking["BS50006"], 2)
        self.assertEqual(ranking["BS50007"], 2)
        self.assertEqual(ranking["BS50008"], 4)
