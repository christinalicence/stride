import json
import os
from celery import shared_task
from anthropic import Anthropic
from django.conf import settings
from .models import UserProfile, TrainingPlan

@shared_task
def generate_training_plan_task(plan_id):
    """Asynchronous task to generate a training plan using the Claude API."""
    client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY'))
    plan = TrainingPlan.objects.get(id=plan_id)
    profile = plan.user

    feedback_context = "No previous feedback available."
    if plan.previous_plan:
        prev_plan = plan.previous_plan
        feedback_context = f"""
        Previous Plan Summary: {prev_plan.plan_summary}
        Duration: {prev_plan.start_date} to {prev_plan.end_date}
        Progress Comments: {prev_plan.progress_comment or 'None'}
        Minor Injuries: {prev_plan.minor_injuries or 'None'}

        Use this information to improve the new training plan.
        """

        # Data from user profile
        "fitness_level": profile.fitness_level,
        "exercise_days_per_week": profile.exercise_days_per_week,
        "exercise_duration": profile.exercise_duration,
        "equipment_text": profile.equipment_text,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "age": profile.age,
        "gender": profile.gender,
        "long_term_injuries": profile.long_term_injuries,
        "injury_limitations": profile.injury_limitations,
        "minor_injuries": profile.minor_injuries,

        # Define output format
        PLAN_SCHEMA = {
        "type": "object",
        "properties": {
            "plan_summary": {"type": "string", "description": "A concise, actionable, and encouraging summary for the next two weeks."},
            "plan_weeks": {
                "type": "array",
                "description": "A detailed structure for exactly 2 weeks of training.",
                "items": {
                    "type": "object",
                    "properties": {
                        "week_number": {"type": "integer", "description": "1 or 2."},
                        "focus": {"type": "string", "description": "The main goal for this week (e.g., Strength endurance, High-intensity cardio, Active recovery)."},
                        "workouts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "suggested_day": {"type": "string", "description": "E.g., Monday, Wednesday, Rest Day."},
                                    "workout_title": {"type": "string", "description": "Short, descriptive title for the session (e.g., Full Body Push, Long Run Tempo)."},
                                    "total_length_minutes": {"type": "integer", "description": "Total duration of the workout, including warm-up/cool-down."},
                                    "exercises": {
                                        "type": "array",
                                        "description": "Detailed steps or individual movements within the session.",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "exercise_name": {"type": "string", "description": "Specific exercise name (e.g., Barbell Squat, Treadmill Run, Yoga Flow)."},
                                                "exercise_type": {"type": "string", "description": "Type of movement (e.g., Compound Lift, Isolation, Interval, Steady State)."},
                                                "intensity": {"type": "string", "description": "RPE (Rate of Perceived Exertion 1-10) or specific weight/speed guidance (e.g., RPE 7-8, 70% 1RM, Zone 2 HR)."},
                                                "details": {"type": "string", "description": "Sets and Reps, Distance, or Time (e.g., 3 sets of 10 reps, 3 x 800m intervals, 30 minutes)."},
                                            },
                                            "required": ["exercise_name", "exercise_type", "intensity", "details"]
                                        }
                                    }
                                },
                                "required": ["suggested_day", "workout_title", "total_length_minutes", "exercises"]
                            }
                        }
                    }
                }
            }
        },
        "required": ["plan_summary", "plan_weeks"]
    }