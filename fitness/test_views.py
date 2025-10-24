from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from fitness.models import UserProfile
from fitness.forms import UserProfileForm


class FitnessViewsTest(TestCase):
    """Tests for profile views: list, detail, and edit"""

    @classmethod
    def setUpTestData(cls):
        # Create two users
        cls.user1 = User.objects.create_user(username='user1', password='pass123')
        cls.user2 = User.objects.create_user(username='user2', password='pass123')

        # If profiles are auto-created via signals, just fetch and update them
        cls.profile1 = UserProfile.objects.get(user=cls.user1)
        cls.profile1.display_name = 'User One'
        cls.profile1.bio = 'Bio1'
        cls.profile1.save()

        cls.profile2 = UserProfile.objects.get(user=cls.user2)
        cls.profile2.display_name = 'User Two'
        cls.profile2.bio = 'Bio2'
        cls.profile2.save()

    def test_profile_list_view(self):
        """Tests that a list of profiles appears in profile list view"""
        url = reverse('profile_list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_list.html')
        self.assertIn(self.profile1, response.context['profiles'])
        self.assertIn(self.profile2, response.context['profiles'])

    def test_profile_detail_login_required(self):
        """Tests that profile detail view requires login and displays correct profile"""
        url = reverse('profile_detail', args=[self.user1.username])
        # Not logged in — should redirect to login
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        # Log in and retry
        self.client.login(username='user1', password='pass123')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_detail.html')
        self.assertEqual(response.context['profile'], self.profile1)
        self.assertIn('comment_form', response.context)

    def test_edit_profile_view(self):
        """Tests that a logged-in user can edit their profile"""
        self.client.login(username='user1', password='pass123')
        url = reverse('edit_profile')
