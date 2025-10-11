from django import forms
from .models import UserProfile, TrainingPlan, Comment

class UserProfileForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        exclude = ['user', 'followers', 'created_at', 'updated_at']


class TrainingPlanForm(forms.ModelForm):
    class Meta:
        model = TrainingPlan
        exclude = ['user', 'plan_json', 'end_date', 'previous_plan', 'progress_comment', 'minor_injuries']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
         }
        
        
class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['content']
        widgets = {
            'content': forms.Textarea(attrs={'rows': 3, 'placeholder': 'Add a comment...'}),
        }
    