from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from django.db.models.signals import post_save
from django.dispatch import receiver

# Create your models here.

class UserProfile(models.Model):
    DURATION_CHOICES = [
        ('0-30', '0-30 minutes'),
        ('31-60', '31-60 minutes'),
        ('61-90', '61-90 minutes'),
        ('91+', '91+ minutes'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100, blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True, null=True)

    # Equipment info text
    equipment_text = models.TextField(
        blank=True,
        null=True,
        help_text="List your available equipment (e.g., dumbbells 5 -12kg, resistance bands medium, exercise bike, etc.)"
    )

    # private physical info
    weight_kg = models.FloatField(blank=True, null=True, help_text="kg(private)")
    height_cm = models.FloatField(blank=True, null=True, help_text="cm(private)")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="years(private)")
    fitness_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        blank=True,
        help_text="(private)")
    
    # injuries & accessibility 
    long_term_injuries = models.TextField(blank=True, null=True, help_text="Please describe any long-term limitations (describe functional limitations).")
    injury_limitations = models.TextField(blank=True, null=True, help_text="Describe specific movement limitations / accessibility needs.")
    minor_injuries = models.TextField(blank=True, null=True, help_text="Minor injuries in last 2 weeks (e.g., 'tight hamstring').")

    # exercise habits
    exercise_days_per_week = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(7)])
    exercise_duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='30-60')

    @property
    def appoved_followers(self):
        return UserProfile.objects.filter(
            sent_follow_requests__to_user=self,
            sent_follow_requests__accepted=True
        )
    
    @property
    def appoved_following(self):
        return UserProfile.objects.filter(
            received_follow_requests__from_user=self,
            received_follow_requests__accepted=True
        )

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def public_profile(self):
        """Data for public profile view.(some fields are private)"""
        return {
            "display_name": self.display_name,
            "profile_picture": self.profile_picture.url if self.profile_picture else None,
            "bio": self.bio,
            "equipment_text": self.equipment_text,
            "fitness_level": self.fitness_level,
            "exercise_days_per_week": self.exercise_days_per_week,
            "exercise_duration": self.exercise_duration,
            "followers_count": self.followers.count(),
            "following_count": self.following.count(),
        }

    def __str__(self):
        return self.display_name or self.user.username
    

class TrainingPlan(models.Model):
    user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='plans')
    # The JSON from Claude is stored here
    plan_json = models.JSONField()
    plan_summary = models.CharField(max_length=400, blank=True)
    goal_type = models.CharField(max_length=20, choices=[('strength','Strength'),('cardio','Cardio'),('combined','Combined')], default='combined')
    target_event = models.CharField(max_length=100, blank=True, help_text="E.g., '5K run', '10K cycle', 'Half marathon', 'Marathon', 'General fitness'")
    target_date = models.DateField(blank=True, null=True)
    start_date = models.DateField(auto_now_add=True)
    end_date = models.DateField(blank=True, null=True)
    previous_plan = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True)
    progress_comment = models.TextField(blank=True, null=True)   # user feedback after plan
    minor_injuries = models.TextField(blank=True, null=True)     # injuries during plan

    def __str__(self):
        return f"Plan for {self.id} for {self.user}"
    

class Comment(models.Model):
    """Comments made by users on profiles or plans."""
    author = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='comments_made', null=True, blank=True)
    
    """For profile comments, 'profile' is set."""
    profile = models.ForeignKey(
        UserProfile,
        on_delete=models.CASCADE,
        related_name='comments_received',
        null=True,
        blank=True
    )

    """For plan comments, 'plan' is set."""
    plan = models.ForeignKey(
        'TrainingPlan',
        on_delete=models.CASCADE,
        related_name='comments',
        null=True,
        blank=True
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    approved = models.BooleanField(default=True)  # For moderation if needed

    def __str__(self):
        target = self.profile or self.plan
        return f"Comment by {self.author} on {target}"

    class Meta:
        ordering = ['-created_at']


class FollowRequest(models.Model):
    """Model to handle follow requests for private profiles."""
    from_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='sent_follow_requests')
    to_user = models.ForeignKey(UserProfile, on_delete=models.CASCADE, related_name='received_follow_requests')
    created_at = models.DateTimeField(auto_now_add=True)
    accepted = models.BooleanField(default=False)

    def __str__(self):
        status = "Accepted" if self.accepted else "Pending"
        return f"Follow request from {self.from_user} to {self.to_user} - {status}"

    class Meta:
        unique_together = ('from_user', 'to_user')


# Signal to create UserProfile when a new User is created
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(
            user=instance,
            display_name=instance.username  # set display_name to username by default
        )

# Signal to save UserProfile when User is saved
@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'userprofile'):
        instance.userprofile.save()