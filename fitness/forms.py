from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from datetime import date, timedelta
from django.core.exceptions import ValidationError
from .models import UserProfile, TrainingPlan, Comment

class UserProfileForm(forms.ModelForm):
    """Form for editing user profiles."""
    class Meta:
        model = UserProfile
        fields = [
            'display_name',
            'bio',
            'profile_picture',
            'equipment_text',
            'goal_event',
            'goal_date',
            'injuries_and_limitations',
            'exercise_days_per_week',
            'exercise_duration',
            'fitness_level',
        ]
        widgets = {
            'bio':forms.Textarea(attrs={'rows': 4}),
            'equipment_text': forms.Textarea(attrs={'rows': 3}),
            'long_term_injuries': forms.Textarea(attrs={'rows': 3}),
            'goal_event': forms.TextInput(attrs={'placeholder': 'E.g., 5K run, Marathon'}),
            'goal_date': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'bio': 'About Me',
            'equipment_text': 'My Equipment',
            'long_term_injuries': 'Long-term Injuries or Limitationa',
            'goal_event': 'Fitness Goal or Event',
            'goal_date': 'Target Date for Goal/Event',
            'fitness_level': 'Current Fitness Level',
            'exercise_duration': 'Avg. Exercise Duration'
        }
    def clean_goal_date(self):
        goal_date = self.cleaned_data.get('goal_date')

        if goal_date:
            today = date.today()
            one_year_from_now = today + timedelta(days=365) 
            # Must be a future date
            if goal_date <= today:
                raise ValidationError("The target date must be set for a date in the future.")
            # Must be within the next 12 months
            if goal_date > one_year_from_now:
                raise ValidationError("The target date cannot be more than one year away.")
        return goal_date


class TrainingPlanForm(forms.ModelForm):
    """Form for creating or editing training plans, excluding AI-generated fields."""
    class Meta:
        model = TrainingPlan
        exclude = ['user', 'plan_json', 'plan_summary', 'end_date', 'previous_plan', 'start_date']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'progress_comment': forms.Textarea(attrs={'rows': 3}),
            'minor_injuries': forms.Textarea(attrs={'rows': 3}),
         }
    
       
class CommentForm(forms.ModelForm):
    """Form for adding comments to profiles or plans."""
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }


# AI Gen Form
class PlanGenerationForm(forms.ModelForm):
    """Form to request AI-generated training plan."""
    # Fields for info to AI
    last_plan_feedback = forms.CharField(
        label='Feedback on Last Plan (Optional)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Provide any feedback or comments on your previous training plan.'
    )
    plan_preferences = forms.CharField(
        label='Plan Preferences (Optional)',
        required=False,
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Any specific preferences or requirements for your new training plan.'
    )
    class Meta:
        model = TrainingPlan
        fields = ['minor_injuries', 'last_plan_feedback', 'plan_preferences']
        widgets = {'minor_injuries': forms.Textarea(attrs={'rows': 3})}
        labels = {'minor_injuries': 'Current minor injuries or concerns'}

        #Helper calls for the AI
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('minor_injuries'),
            Field('last_plan_feedback'),
            Field('plan_preferences'),
            Submit('submit', 'Generate Training Plan', css_class='btn btn-primary')
        )
