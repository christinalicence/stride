from django.contrib import admin
from django_summernote.admin import SummernoteModelAdmin
from .models import UserProfile, TrainingPlan, Comment

# Register your models here.
# Summernote on;y for some fields that don't go to LLM

@admin.register(UserProfile)
class UserProfileAdmin(SummernoteModelAdmin):
    # Enable Summernote for the UserProfile bio field
    summernote_fields = ('bio',)

@admin.register(TrainingPlan)
class TrainingPlanAdmin(SummernoteModelAdmin):
    # Enable Summernote for plan descriptions and user progress comments
    summernote_fields = ('plan_summary', 'progress_comment',)

@admin.register(Comment)
class CommentAdmin(SummernoteModelAdmin):
    # Enable Summernote for comment content
    summernote_fields = ('text',)
