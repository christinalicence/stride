from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Create your models here.

class UserProfile(models.Model):
    DURATION_CHOICES = [
        ('0-30', '0-30 minutes'),
        ('31-60', '31-60 minutes'),
        ('61-90', '61-90 minutes'),
        ('91+', '91+ minutes'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE)
    display_name = models.CharField(max_length=100 blank=True)
    profile_picture = models.ImageField(upload_to='profiles/', blank=True, null=True)
    bio = models.TextField(blank=True null=True)

    # Equipment info text
    equipment_text = models.TextField(
        blank=True,
        null=True,
        help_text="List your available equipment (e.g., dumbbells 5 -12kg, resistance bands medium, exercise bike, etc.)"
    )

    # private physical info
    weight_kg = models.FloatField(blank=True, null=True, help_text="kg(privates)")
    height_cm = models.FloatField(blank=True, null=True, help_text="cm(private)")
    age = models.PositiveIntegerField(blank=True, null=True, help_text="years(private)")
    fitness_level = models.CharField(
        max_length=20,
        choices=[('beginner', 'Beginner'), ('intermediate', 'Intermediate'), ('advanced', 'Advanced')],
        blank=True,
        help_text="(private)")
    
    # injuries & accessibility 
    long_term_injuries = models.TextField(blank=True, null=True help_text="Please describe any long-term limitations (describe functional limitations).")
    injury_limitations = models.TextField(blank=True, null=True help_text="Describe specific movement limitations / accessibility needs.")
    minor_injuries = models.TextField(blank=True, null=True help_text="Minor injuries in last 2 weeks (e.g., 'tight hamstring').")

    # exercise habits
    exercise_days_per_week = models.PositiveIntegerField(default=3, validators=[MinValueValidator(1), MaxValueValidator(7)])
    exercise_duration = models.CharField(max_length=10, choices=DURATION_CHOICES, default='30-60')

    # social
    followers = models.ManyToManyField('self', symmetrical=False, related_name='following', blank=True)

    # timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    