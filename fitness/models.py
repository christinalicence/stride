from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from cloudinary.models import CloudinaryField
from django.templatetags.static import static

# Create your models here.


class UserProfile(models.Model):
    FITNESS_LEVEL_CHOICES = [
        ("beginner", "Beginner (New to exercise)"),
        ("novice", "Novice (Irregular exercise)"),
        ("intermediate", "Intermediate (Regular exercise)"),
        ("advanced", "Advanced (Highly trained/competitive)"),
    ]
    EXERCISE_DURATION_CHOICES = [
        ("30", "Up to 30 minutes"),
        ("31-60", "31 - 60 minutes"),
        ("61-90", "61 - 90 minutes"),
        ("91-120", "91 - 120 minutes"),
        ("120+", "More than 120 minutes"),
    ]
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = CloudinaryField("image", blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Equipment info text
    equipment_text = models.TextField(
        blank=True,
        null=True,
        help_text=(
            "List your available equipment "
            "(e.g., dumbbells 5–12kg, resistance bands medium, bike etc.)"
        ),
    )
    fitness_level = models.CharField(
        max_length=20,
        choices=FITNESS_LEVEL_CHOICES,
        default="novice",
        help_text="Current fitness level",
    )
    injuries_and_limitations = models.TextField(
        blank=True,
        null=True,
        help_text="Describe any long-term injuries or mobility limitations.",
    )
    exercise_days_per_week = models.PositiveIntegerField(
        default=3, validators=[MinValueValidator(1), MaxValueValidator(7)]
    )
    exercise_duration = models.CharField(
        max_length=20,
        choices=EXERCISE_DURATION_CHOICES,
        default="31-60",
        help_text="Average duration of your exercise sessions.",
    )
    fitness_level = models.CharField(
        max_length=20,
        choices=FITNESS_LEVEL_CHOICES,
        default="novice",
        help_text="Current fitness level (Used by AI for intensity setting).",
    )
    goal_event = models.CharField(
        max_length=100,
        blank=True,
        null=True,
        help_text="E.g., '5K run', 'Build muscle', 'Improve flexibility'",
    )
    goal_date = models.DateField(
        blank=True, null=True, help_text="Target date for achieving your goal"
    )

    def get_profile_picture_url(self):
        """Return Cloudinary URL if exists, otherwise default static image"""
        if self.profile_picture and hasattr(self.profile_picture, "url"):
            return self.profile_picture.url
        return static("fitness/images/weights.jpg")

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    @property
    def approved_followers(self):
        return UserProfile.objects.filter(
            sent_follow_requests__to_user=self, sent_follow_requests__accepted=True
        )

    @property
    def approved_following(self):
        return UserProfile.objects.filter(
            received_follow_requests__from_user=self,
            received_follow_requests__accepted=True,
        )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def public_profile(self):
        """Data for public profile view.(some fields are private)"""
        return {
            "display_name": self.display_name,
            "profile_picture": (
                self.profile_picture.url if self.profile_picture else None
            ),
            "bio": self.bio,
            "equipment_text": self.equipment_text,
            "fitness_level": self.fitness_level,
            "exercise_days_per_week": self.exercise_days_per_week,
            "exercise_duration": self.exercise_duration,
            "followers_count": self.approved_followers.count(),
            "following_count": self.approved_following.count(),
        }

    def __str__(self):
        return self.display_name or self.user.username


class TrainingPlan(models.Model):
    user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="plans"
    )
    plan_json = models.JSONField(
        help_text="JSON containing weeks, workouts, and exercises."
    )
    plan_title = models.CharField(max_length=200, blank=True, null=True)
    plan_summary = models.TextField(blank=True, null=True)
    goal_type = models.CharField(
        max_length=20,
        choices=[
            ("strength", "Strength"),
            ("cardio", "Cardio"),
            ("combined", "Combined"),
        ],
        default="combined",
    )
    plan_preferences = models.TextField(blank=True, null=True)
    target_event = models.CharField(max_length=100, blank=True)
    target_date = models.DateField(blank=True, null=True)
    previous_plan = models.ForeignKey(
        "self", on_delete=models.SET_NULL, null=True, blank=True
    )
    progress_comment = models.TextField(blank=True, null=True)
    minor_injuries = models.TextField(blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return self.plan_title or f"Plan {self.id} for {self.user}"


class Comment(models.Model):
    """Comments made by users on profiles or plans."""

    author = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="comments_made",
        null=True,
        blank=True,
    )

    """For profile comments, 'profile' is set."""
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="comments_received",
        null=True,
        blank=True,
    )

    """For plan comments, 'plan' is set."""
    plan = models.ForeignKey(
        "TrainingPlan",
        on_delete=models.CASCADE,
        related_name="comments",
        null=True,
        blank=True,
    )

    """For comment replies 'parent' is set"""
    parent = models.ForeignKey(
        "self", on_delete=models.CASCADE, related_name="replies", null=True, blank=True
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    approved = models.BooleanField(default=True)  # For moderation

    def __str__(self):
        target = self.profile or self.plan
        return f"Comment by {self.author} on {target}"

    class Meta:
        ordering = ["-created_at"]


class FollowRequest(models.Model):
    """Model to handle follow requests for private profiles."""

    from_user = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name="sent_follow_requests",
    )
    to_user = models.ForeignKey(
        UserProfile, on_delete=models.CASCADE, related_name="received_follow_requests"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        status = "Accepted" if self.accepted else "Pending"
        return f"Follow request from {self.from_user} " f"to {self.to_user} - {status}"

    class Meta:
        unique_together = (
            "from_user",
            "to_user",
        )
