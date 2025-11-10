from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib.auth.admin import UserAdmin as DefaultUserAdmin
from django_summernote.admin import SummernoteModelAdmin
from .models import UserProfile, TrainingPlan, Comment


# --- Custom User Admin to include UserProfile inline ---
class UserProfileInline(admin.StackedInline):
    model = UserProfile
    can_delete = False
    verbose_name_plural = 'Profile Details'


class CustomUserAdmin(DefaultUserAdmin):
    inlines = (UserProfileInline, )
    list_display = ('username', 'email', 'first_name', 'last_name', 'is_staff')


@admin.register(UserProfile)
class UserProfileAdmin(SummernoteModelAdmin):
    summernote_fields = ('bio',)
    list_display = ('user', 'display_name', 'goal_event')
    search_fields = ('user__username', 'display_name')
    list_filter = ('fitness_level', 'exercise_days_per_week')


@admin.register(TrainingPlan)
class TrainingPlanAdmin(SummernoteModelAdmin):
    summernote_fields = ('plan_summary', 'progress_comment',)
    list_display = ('plan_title', 'user', 'goal_type', 'start_date')
    search_fields = ('plan_title', 'user__user__username')
    list_filter = ('goal_type', 'start_date')


@admin.register(Comment)
class CommentAdmin(SummernoteModelAdmin):
    summernote_fields = ('content',)
    list_display = ('author', 'profile', 'plan', 'created_at', 'approved')
    search_fields = ('author__username', 'content')
    list_filter = ('approved', 'created_at')