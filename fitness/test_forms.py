from datetime import date, timedelta
from django.test import TestCase
from django.contrib.auth.models import User
from fitness.forms import UserProfileForm, TrainingPlanForm, PlanGenerationForm, CommentForm



class TestUserProfileForm(TestCase):
    def test_valid_data(self):
        form = UserProfileForm(data={
            'bio': 'Runner',
            'equipment_text': 'Skipping rope',
            'long_term_injuries': 'Knee pain',
            'minor_injuries': 'Twisted ankle',
            'exercise_days_per_week': 3,
            'exercise_duration': '31-60',
        })
        if not form.is_valid():
            print(form.errors)
        assert form.is_valid()

    def test_missing_required_fields(self):
        form = UserProfileForm(data={
            'exercise_days_per_week': '',
            'exercise_duration': '',
        })
        assert not form.is_valid()

    def test_optional_fields_blank(self):
        form = UserProfileForm(data={
            'exercise_days_per_week': 3,
            'exercise_duration': '31-60',
        })
        assert form.is_valid()


class TestTrainingPlanForm(TestCase):
    def test_valid_data(self):
        form = TrainingPlanForm(data={
            'goal_type': 'cardio',  
            'target_event': 'Brighton Half Marathon',
            'target_date': date.today() + timedelta(days=60),
            'progress_comment': 'Currently running 15k per week',
            'minor_injuries': ''
        })
        assert form.is_valid()
    
    def test_optional_fields_are_blank(self):
        form = TrainingPlanForm(data={
            'goal_type': 'cardio',
            'target_event': '',  # optional field left blank
            'progress_comment': '',
            'minor_injuries': '',
        })
        assert form.is_valid()

    def test_past_target_date_invalid(self):
        form = TrainingPlanForm(data={
            'target_date': date.today() - timedelta(days=1),
        })
        assert not form.is_valid()


class TestPlanGenerationForm(TestCase):
    def test_valid_with_optional_fields(self):
        form = PlanGenerationForm(data={
            'goal_type': 'cardio',
            'target_event': '10K run',
            'target_date': date.today() + timedelta(days=30),
            'progress_comment': 'Running 5k per week',
            'minor_injuries': '',
            'last_plan_feedback': 'Too easy',
            'plan_preferences': 'Include hills'
        })
        assert form.is_valid()
    
    def test_without_optional_fields(self):
        form = PlanGenerationForm(data={
            'goal_type': 'strength',
            'target_event': '5K run',
            'target_date': date.today() + timedelta(days=30),
            'progress_comment': 'Running 3k per week',
            'minor_injuries': ''
        })
        assert form.is_valid()


class TestCommentForm(TestCase):
    def test_valid_comment(self):
        form = CommentForm(data={'content': 'Great plan!'})
        assert form.is_valid()

    def test_empty_comment_invalid(self):
        form = CommentForm(data={'content': ''})
        assert not form.is_valid()
        