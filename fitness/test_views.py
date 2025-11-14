from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from django.db.models.signals import post_save
from fitness.signals import create_user_profile, save_user_profile
from fitness.models import UserProfile, TrainingPlan, Comment, FollowRequest
from fitness.forms import UserProfileForm
from datetime import date, timedelta


class FitnessViewsTest(TestCase):
    """Tests for profile views: list, detail, and edit"""

    @classmethod
    def setUpTestData(cls):
        # Disconnect signals to prevent automatic profile creation during tests
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)
        try:
            # Create test users
            cls.user1 = User.objects.create_user(
                username="user1", password="test_password1"
            )
            cls.user2 = User.objects.create_user(
                username="user2", password="test_password2"
            )
            # Create UserProfiles for the test users
            cls.profile1 = UserProfile.objects.create(
                user=cls.user1,
                display_name="User One",
                bio="Bio1",
                profile_picture="placeholder",
            )
            cls.profile2 = UserProfile.objects.create(
                user=cls.user2,
                display_name="User Two",
                bio="Bio2",
                profile_picture="placeholder",
            )
            # Create a TrainingPlan for one user
            cls.plan1 = TrainingPlan.objects.create(
                user=cls.profile1,
                plan_title="Test Plan 1",
                goal_type="Running",
                start_date=date.today(),
                plan_json={},
            )
        finally:
            # Reconnect the signals after setup is complete
            post_save.connect(create_user_profile, sender=User)
            post_save.connect(save_user_profile, sender=User)

    def test_profile_list_view(self):
        """Tests that a list of profiles appears in profile list view"""
        url = reverse("profile_list")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_list.html")
        self.assertIn(self.profile1, response.context["profiles"])
        self.assertIn(self.profile2, response.context["profiles"])

    def test_profile_detail_view_authenticated(self):
        """Tests that a profile detail page."""
        self.client.login(username="user1", password="test_password1")
        url = reverse("profile_detail", kwargs={"username": self.user2.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_detail.html")
        self.assertEqual(response.context["profile"], self.profile2)

    def test_profile_detail_view_unauthenticated(self):
        """Tests that unauthenticated users are redirected to login."""
        url = reverse("profile_detail", kwargs={"username": self.user1.username})
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, f"/accounts/login/?next={url}")

    def test_edit_profile_view_get(self):
        """Tests the GET request for the edit profile view."""
        self.client.login(username="user1", password="test_password1")
        url = reverse("edit_profile")
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context["form"], UserProfileForm)

    def test_edit_profile_view_post_success(self):
        """Tests successful form submission for profile editing."""
        self.client.login(username="user1", password="test_password1")
        url = reverse("edit_profile")
        new_bio = "Updated Bio Content"
        new_data = {
            "display_name": "New Display Name",
            "bio": new_bio,
            "profile_picture": "",
            "equipment_text": "",
            "goal_event": "5K Run",
            "goal_date": (date.today() + timedelta(days=30)).strftime("%Y-%m-%d"),
            "injuries_and_limitations": "None",
            "exercise_days_per_week": 5,
            "exercise_duration": "31-60",
            "fitness_level": "intermediate",
        }
        response = self.client.post(url, new_data, follow=True)
        # Check for success
        self.assertEqual(response.status_code, 200)
        self.profile1.refresh_from_db()
        self.assertEqual(self.profile1.bio, new_bio)
        self.assertRedirects(
            response,
            reverse("profile_detail", kwargs={"username": self.user1.username}),
        )

    def test_search_profiles_by_username(self):
        """Tests searching profiles by username"""
        self.client.login(username="user1", password="test_password1")
        url = reverse("search_profiles_by_username")
        response = self.client.get(url, {"q": "user2"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_search_results.html")
        self.assertIn(self.profile2, response.context["profiles"])
        self.assertNotIn(self.profile1, response.context["profiles"])

    def test_search_by_username_no_query_returns_all(self):
        """Tests searching profiles by username with no query returns all"""
        self.client.login(username="user1", password="test_password1")
        url = reverse("search_profiles_by_username")
        response = self.client.get(url, {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_search_results.html")
        self.assertEqual(
            len(response.context["profiles"]), 2
        )  # Should include user1 and user2

    def test_search_profiles_by_goal_event(self):
        """Tests searching profiles by goal/event"""
        self.profile1.goal_event = "Marathon"
        self.profile1.save()
        self.profile2.goal_event = "Triathlon"
        self.profile2.save()
        self.client.login(username="user1", password="test_password1")
        url = reverse("search_profiles_by_goal_event")
        response = self.client.get(url, {"q": "Triathlon"})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_search_results.html")
        self.assertIn(self.profile2, response.context["profiles"])
        self.assertNotIn(self.profile1, response.context["profiles"])

    def test_search_by_goal_event_no_query_returns_all(self):
        """Tests searching profiles by goal/event with no query returns all"""
        self.profile1.goal_event = "Marathon"
        self.profile1.save()
        self.profile2.goal_event = "Triathlon"
        self.profile2.save()

        self.client.login(username="user1", password="test_password1")
        url = reverse("search_profiles_by_goal_event")
        response = self.client.get(url, {"q": ""})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "profiles/profile_search_results.html")
        self.assertEqual(
            len(response.context["profiles"]), 2
        )  # Should include user1 and user2


class DeletePlanAndRetryViewTest(TestCase):
    """Tests for the delete_plan_and_retry view, covering authorization,
    deletion, and redirection logic."""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        # Disconnect signals to prevent automatic UserProfile creation
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)

    def setUp(self):
        # Create the main user
        self.user = User.objects.create_user(
            username="plan_owner", password="testpassword"
        )
        self.profile = UserProfile.objects.create(
            user=self.user, display_name="plan_owner", profile_picture="placeholder"
        )
        # Create the other user
        self.other_user = User.objects.create_user(
            username="other_user", password="testpassword"
        )
        UserProfile.objects.create(
            user=self.other_user,
            display_name="other_user",
            profile_picture="placeholder",
        )
        # Create a TrainingPlan using the UserProfile instance
        self.plan = TrainingPlan.objects.create(
            user=self.profile,
            plan_title="Test Plan to Delete",
            goal_type="Running",
            start_date=date.today(),
            plan_json={},
        )
        self.url = reverse("delete_plan_and_retry", kwargs={"pk": self.plan.pk})
        self.redirect_url = reverse("create_training_plan")


# Tests for comments and follows


class FitnessSocialTests(TestCase):
    """Sets up tests for comments and follows between profiles."""

    @classmethod
    def setUpTestData(cls):
        # Disconnect signals to prevent automatic profile creation during tests
        post_save.disconnect(create_user_profile, sender=User)
        post_save.disconnect(save_user_profile, sender=User)
        try:
            # Create test users and profiles
            cls.user_author = User.objects.create_user(
                username="comment_author", password="test_password"
            )
            cls.profile_author = UserProfile.objects.create(
                user=cls.user_author, display_name="Author Profile", bio="Author Bio"
            )
            cls.user_target = User.objects.create_user(
                username="comment_target", password="test_password"
            )
            cls.profile_target = UserProfile.objects.create(
                user=cls.user_target, display_name="Target Profile", bio="Target Bio"
            )
            # Create a comment by the author on the target's profile
            cls.comment = Comment.objects.create(
                author=cls.profile_author,
                profile=cls.profile_target,
                content="Test comment.",
                approved=False,
            )
        finally:
            # Reconnect the signals after setup is complete
            post_save.connect(create_user_profile, sender=User)
            post_save.connect(save_user_profile, sender=User)

    # Tests for comments
    def test_add_comment_success(self):
        """Tests successful POST request to add a new comment."""
        self.client.login(username="comment_author", password="test_password")
        url = reverse("add_comment", kwargs={"profile_id": self.profile_target.pk})
        new_comment_content = "This is a new test comment."
        response = self.client.post(url, {"content": new_comment_content}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse("profile_detail", kwargs={"username": self.user_target.username}),
        )
        # Check if the comment was created in the database
        self.assertTrue(
            Comment.objects.filter(
                content=new_comment_content, author=self.profile_author
            ).exists()
        )

    def test_delete_comment_non_author_failure(self):
        """Tests that a non-author user cannot
        delete another user's comment."""
        # Create a third user/profile
        user_intruder = User.objects.create_user(
            username="intruder", password="test_password_i"
        )
        UserProfile.objects.get_or_create(user=user_intruder)
        self.client.login(username="intruder", password="test_password_i")
        url = reverse("delete_comment", kwargs={"comment_id": self.comment.pk})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse(
                "profile_detail",
                kwargs={"username": self.user_target.username},
            ),
        )
        self.assertContains(
            response, "You do not have permission to delete this comment."
        )
        # Ensure comment still exists
        self.assertTrue(Comment.objects.filter(pk=self.comment.pk).exists())

    def test_approve_comment_owner_success(self):
        """Tests that the profile owner can approve a comment."""
        self.client.login(
            username="comment_target", password="test_password"
        )  # Login as target (owner)
        self.assertFalse(self.comment.approved)
        url = reverse("approve_comment", kwargs={"comment_id": self.comment.pk})
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse("profile_detail", kwargs={"username": self.user_target.username}),
        )
        self.comment.refresh_from_db()
        self.assertTrue(self.comment.approved)

    # Tests for follows
    def test_send_follow_request_success(self):
        """Tests successful follow request from author to target."""
        self.client.login(username="comment_author", password="test_password")
        url = reverse(
            "send_follow_request", kwargs={"profile_pk": self.profile_target.pk}
        )
        response = self.client.post(url, follow=True)

        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse("profile_detail", kwargs={"username": self.user_target.username}),
        )
        # Check if the FollowRequest exists
        self.assertTrue(
            FollowRequest.objects.filter(
                from_user=self.profile_author,
                to_user=self.profile_target,
                accepted=False,
            ).exists()
        )

    def test_approve_follow_request_success(self):
        """Tests successful approval of a follow request by the recipient."""
        follow_request = FollowRequest.objects.create(
            from_user=self.profile_author, to_user=self.profile_target, accepted=False
        )
        self.assertFalse(follow_request.accepted)
        self.client.login(username="comment_target", password="test_password")
        url = reverse(
            "approve_follow_request", kwargs={"request_id": follow_request.pk}
        )
        response = self.client.post(url, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertRedirects(
            response,
            reverse("profile_detail", kwargs={"username": self.user_target.username}),
        )
        follow_request.refresh_from_db()
        self.assertTrue(follow_request.accepted)
