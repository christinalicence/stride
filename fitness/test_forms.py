from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from fitness.forms import UserProfileForm, TrainingPlanForm
from fitness.models import UserProfile, TrainingPlan


class TestUserProfileForm(TestCase):
    def test_valid_data(self):
        form = UserProfileForm(data={
            'bio': 'Runner',
            'equipment_text': 'Skipping rope',
            'long_term_injuries': 'Knee pain',
            'minor_injuries': 'Twisted ankle'
        })
        if not form.is_valid():
            print(form.errors)
        assert form.is_valid()


class TestTrainingPlanForm(TestCase):
    def test_valid_data(self):
        form = TrainingPlanForm(data ={
            'goal_type': 'Endurance',
            'target_event': 'Brighton Half Marathon',
            'target_date': date.today() + timedelta(days=60),
            'progress_comment': 'Currently running 15k per week',
            'minor_injuries': ''
        })
        if not form.is_valid():
            print(form.errors)
        assert form.is_valid()
    