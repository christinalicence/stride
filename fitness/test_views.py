from django.contrib.auth.models import User
from django.urls import reverse
from django.test import TestCase
from fitness.models import UserProfile, TrainingPlan, Comment, FollowRequest
from fitness.forms import UserProfileForm, PlanGenerationForm
from datetime import date
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
        self.assertEqual(plan.goal_type, 'combined')
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

        # Comments tests 

    def test_add_comment(self):
        """ Tests you can add a comment"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('add_comment', args=[self.profile2.pk])
        post_data = {'content': 'plan comment'}
        response = self.client.post(url, post_data)
        comment = Comment.objects.filter(author=self.profile1, profile=self.profile2).last()
        self.assertIsNotNone(comment)            
        self.assertEqual(comment.content, 'plan comment')
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile2.user.username]))

    def test_edit_comment(self):
        """Tests you can edit a comment"""
        comment = Comment.objects.create(author=self.profile1, profile=self.profile2, content='Original comment')
        self.client.login(username='user1', password='test_password1')
        url = reverse('edit_comment', args=[comment.pk])
        post_data = {'content': 'Updated'}
        response = self.client.post(url, post_data)
        comment.refresh_from_db()
        self.assertEqual(comment.content, 'Updated')
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile2.user.username]))

    def test_delete_comment(self):
        """Tests you can delete a comment"""
        comment = Comment.objects.create(author=self.profile1, profile=self.profile2, content='To delete')
        self.client.login(username='user1', password='test_password1')
        url = reverse('delete_comment', args=[comment.pk])
        response = self.client.post(url)
        self.assertFalse(Comment.objects.filter(pk=comment.pk).exists())
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile2.user.username]))

    def test_approve_comment(self):
        """Tests you can approve a comment"""
        comment = Comment.objects.create(author=self.profile2, profile=self.profile1, content='Pending', approved=False)
        self.client.login(username='user1', password='test_password1')
        url = reverse('approve_comment', args=[comment.pk])
        response = self.client.post(url)
        comment.refresh_from_db()
        self.assertTrue(comment.approved)
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile1.user.username]))

    def test_add_reply_comment(self):
        """Tests you can reply to an exisiting comment"""
        parent_comment = Comment.objects.create(
            author=self.profile2,
            profile=self.profile1,
            content='Orginial Comment'
        )
        self.client.login(username='user1', password='test_password1')
        # post a reply
        url = reverse('reply_comment', args=[self.profile1.pk, parent_comment.pk])
        post_data = {'content': 'Reply to original comment'}
        response = self.client.post(url, post_data)
        reply = Comment.objects.filter(
            author=self.profile1,
            profile=self.profile1,
            parent=parent_comment
        ).last()
        self.assertIsNotNone(reply)
        self.assertEqual(reply.content, 'Reply to original comment')
        self.assertEqual(reply.parent, parent_comment)
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile1.user.username]))

        # Tests for follows
    def test_send_follow_request(self):
        """Tests if follow requests send and redirect"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('send_follow_request', args=[self.profile2.pk])
        response = self.client.post(url)
        fr = FollowRequest.objects.filter(from_user=self.profile1, to_user=self.profile2).last()
        self.assertIsNotNone(fr)
        self.assertFalse(fr.accepted)
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile2.user.username]))

    def test_approve_follow_request(self):
        """Tests if you can approve follow requests, then redirects"""
        fr = FollowRequest.objects.create(from_user=self.profile2, to_user=self.profile1, accepted=False)
        self.client.login(username='user1', password='test_password1')
        url = reverse('approve_follow_request', args=[fr.pk])
        response = self.client.post(url)
        fr.refresh_from_db()
        self.assertTrue(fr.accepted)
        self.assertRedirects(response, reverse('profile_detail', args=[self.profile1.user.username]))

        # Tests for saerch views
    def test_search_profiles_by_username(self):
        """Tests searching profiles by username"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('search_profiles_by_username')
        response = self.client.get(url, {'q': 'user2'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_search_results.html')
        self.assertIn(self.profile2, response.context['profiles'])
        self.assertNotIn(self.profile1, response.context['profiles'])

    def test_search_by_username_no_query(self):
        """Tests searching profiles by username with no query returns all"""
        self.client.login(username='user1', password='test_password1')
        url = reverse('search_profiles_by_username')
        response = self.client.get(url, {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_search_results.html')
        self.assertEqual(len(response.context['profiles']), 0)

    def test_search_profiles_by_goal_event(self):
        """Tests searching profiles by goal/event"""
        self.profile1.goal_event = 'Marathon'
        self.profile1.save()
        self.profile2.goal_event = 'Triathlon'
        self.profile2.save()
        self.client.login(username='user1', password='test_password1')
        url = reverse('search_profiles_by_goal_event')
        response = self.client.get(url, {'q': 'Triathlon'})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_search_results.html') 
        self.assertIn(self.profile2, response.context['profiles'])
        self.assertNotIn(self.profile1, response.context['profiles'])

    def test_search_by_goal_event_no_query(self):
        """Tests searching profiles by goal/event with no query returns all"""
        self.profile1.goal_event = 'Marathon'
        self.profile1.save()
        self.profile2.goal_event = 'Triathlon'
        self.profile2.save()

        self.client.login(username='user1', password='test_password1')
        url = reverse('search_profiles_by_goal_event')
        response = self.client.get(url, {'q': ''})
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'profiles/profile_search_results.html')
        self.assertEqual(len(response.context['profiles']), 0)