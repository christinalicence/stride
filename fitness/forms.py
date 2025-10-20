from django import forms
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field
from .models import UserProfile, TrainingPlan, Comment

class UserProfileForm(forms.ModelForm):
    """Form for editing user profiles."""
    class Meta:
        model = UserProfile
        exclude = ['user', 'followers',]


class TrainingPlanForm(forms.ModelForm):
    """Form for creating or editing training plans, excluding AI-generated fields."""
    class Meta:
        model = TrainingPlan
        exclude = ['user', 'plan_json', 'end_date', 'previous_plan', 'progress_comment', 'minor_injuries']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
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

class PlanGenerationForm(forms.Form):
    """Form to request AI-generated training plan."""
    goal = forms.CharField(
        label='Fitness Goal',
        widget=forms.Textarea(attrs={'rows': 3}),
        help_text='Describe your fitness goal for the training plan.'
    )
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

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.layout = Layout(
            Field('goal'),
            Field('last_plan_feedback'),
            Field('plan_preferences'),
            Submit('submit', 'Generate Plan', css_class='btn-primary')
        )