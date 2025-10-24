from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from fitness.models import UserProfile, TrainingPlan
from fitness.forms import UserProfileForm, PlanGenerationForm
import datetime
import json


class FitnessViewsTest(TestCase):
    """Tests for profile views: list, detail, and edit"""

    @classmethod
    def setUpTestData(cls):
        # Create two users
        cls.user1 = User.objects.create_user(username='user1', password='test_password1') # Dummy passwords
        cls.user2 = User.objects.create_user(username='user2', password='test_password2')

        # If profiles are auto-created via signals, just fetch and update them
        cls.profile1 = UserProfile.objects.get(user=cls.user1)
        cls.profile1.display_name = 'User One'
        cls.profile1.bio = 'Bio1'
        cls.profile1.save()

        cls.profile2 = UserProfile.objects.get(user=cls.user2)
        cls.profile2.display_name = 'User Two'
        cls.profile2.bio = 'Bio2'
        cls.profile2.save()

        # Profile related views

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
        self.client.login(username='user1', password='test_password1')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_detail.html')
        self.assertEqual(response.context['profile'], self.profile1)
        self.assertIn('comment_form', response.context)

    def test_edit_profile_view(self):
        """Tests that a logged-in user can edit their profile"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('edit_profile')

    # Training Plan related Views

    def test_create_training_plan_view(self):
        """Tests that a user can create a training plan and add fields"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('create_training_plan')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertIsInstance(response.context['form'], PlanGenerationForm)
        # Create a new plan 
        post_data = {
            'goal_type': 'strength',  
            'target_event': 'Marathon',
            'target_date': '2025-12-01',
            'progress_comment': 'Feeling good',
            'minor_injuries': '',  
        }
        response = self.client.post(url, post_data)
        plan = TrainingPlan.objects.filter(user=self.profile1).last()
        self.assertIsNotNone(plan)
        self.assertEqual(plan.goal_type, 'strength')
        self.assertRedirects(response, reverse('plan_detail', args=[plan.pk]))
    
    def test_plan_detail_view(self):
        """Tests that a user can view the details of their own plan"""
        self.client.login(username='user1', password='test_password1')
        # create a plan for the test
        plan = TrainingPlan.objects.create(
            user=self.profile1,
            goal_type='strength',
            target_event='Marathon',
            target_date='2025-12-01',
            plan_json=json.dumps({})  # empty JSON for testing
        )
        url = reverse('plan_detail', args=[plan.pk])
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/plan_detail.html')
        self.assertEqual(response.context['plan'], plan)   

    def test_previous_plans_view(self):
        """Tests that a user can see their previous plans"""
        self.client.login(username='user1', password='test_password1')

        # Create a couple of plans for the user
        plan1 = TrainingPlan.objects.create(
            user=self.profile1,
            goal_type='strength',
            target_event='Marathon',
            target_date='2025-12-01',
            plan_json=json.dumps({})
        )
        plan2 = TrainingPlan.objects.create(
            user=self.profile1,
            goal_type='cardio',
            target_event='Triathlon',
            target_date='2025-11-01',
            plan_json=json.dumps({})
        )
        url = reverse('previous_plans')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'plans/previous_plans.html')
        # Check that the plans appear in the context and in order
        self.assertEqual(list(response.context['plans']), [plan1, plan2])
