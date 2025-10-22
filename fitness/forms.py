from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from .models import UserProfile, TrainingPlan, Comment

class UserProfileForm(forms.ModelForm):
    """Form for editing user profiles."""
    class Meta:
        model = UserProfile
        exclude = ['user', 'created at', 'updated_at']
        widgets = {
            'bio':forms.Textarea(attrs={'rows': 4}),
            'equipment_text': forms.Textarea(attrs={'rows': 3}),
            'long_term_injuries': forms.Textarea(attrs={'rows': 3}),
            'minor_injuries': forms.Textarea(attrs={'rows': 3},)
        }


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
        fields = ['goal_type', 'target_event', 'target_date', 'progress_comment', 'minor_injuries']
        widgets = {
            'target_date': forms.DateInput(attrs={'type': 'date'}),
            'progress_comment': forms.Textarea(attrs={'rows': 3}),
            'minor_injuries': forms.Textarea(attrs={'rows': 3}),
        }
        labels = {
            'goal_type': 'Training Goal Type',
            'target_event': 'Target Event or Goal',
            'progress_comment': 'Notes about your current fitness level',
            'minor_injuries': 'Current minor injuries or concerns',
        }
        #Helper calls for the AI
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('goal_type'),
            Field('target_event'),
            Field('target_date'),
            Field('progress_comment'),
            Field('minor_injuries'),
            Field('last_plan_feedback'),
            Field('plan_preferences'),
            Submit('submit', 'Generate Training Plan', css_class='btn btn-primary')
        )