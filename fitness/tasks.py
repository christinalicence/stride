import json
import os
import logging
from celery import shared_task
from anthropic import Anthropic
from django.conf import settings
from .models import TrainingPlan

# Initialize logger
logger = logging.getLogger(__name__)


@shared_task
def generate_training_plan_task(plan_id):
    """Generate a 2-week training plan using Claude API."""
    client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY', settings.CLAUDE_API_KEY))
    try:
        plan = TrainingPlan.objects.get(id=plan_id)
    except TrainingPlan.DoesNotExist:
        logger.error(f"TrainingPlan {plan_id} not found")
        return
    profile = plan.user

    # Prepare feedback context
    feedback_context = "No previous feedback."
    if plan.previous_plan:
        prev = plan.previous_plan
        feedback_context = (
            f"Previous summary: {prev.plan_summary or 'None'}. "
            f"Progress: {prev.progress_comment or 'None'}. "
            f"Injuries: {prev.minor_injuries or 'None'}."
        )

    # Prepare user profile data
    profile_data = {
        "fitness_level": profile.fitness_level,
        "exercise_days_per_week": profile.exercise_days_per_week,
        "exercise_duration": profile.exercise_duration,
        "equipment_text": profile.equipment_text,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "age": profile.age,
        "gender": getattr(profile, 'gender', None),
        "long_term_injuries": profile.long_term_injuries,
        "injury_limitations": profile.injury_limitations,
        "minor_injuries": profile.minor_injuries
    }

    # output format
    PLAN_SCHEMA = {
        "type": "object",
        "properties": {
            "plan_summary": {"type": "string"},
            "plan_weeks": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "week_number": {"type": "integer"},
                        "focus": {"type": "string"},
                        "workouts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "day": {"type": "string"},
                                    "title": {"type": "string"},
                                    "length_minutes": {"type": "integer"},
                                    "exercises": {
                                        "type": "array",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "name": {"type": "string"},
                                                "type": {"type": "string"},
                                                "intensity": {"type": "string"},
                                                "details": {"type": "string"}
                                            },
                                            "required": ["name", "type", "intensity", "details"]
                                        }
                                    }
                                },
                                "required": ["day", "title", "length_minutes", "exercises"]
                            }
                        }
                    },
                    "required": ["week_number", "focus", "workouts"]
                }
            }
        },
        "required": ["plan_summary", "plan_weeks"]
    }

    # Construct the prompt for the AI model - no whitespace injson to shorten
    prompt = f"""You are a fitness coach. Generate a 2-week training plan.
Previous feedback: {feedback_context}
Goals: {plan.goal_type}, Event: {plan.target_event or 'General'}, Date: {plan.target_date or 'None'}
Profile: {json.dumps(profile_data, separators=(',', ':'))} 
RULES:

Exactly 2 weeks, matching exercise_days_per_week ({profile.exercise_days_per_week}).
Rest days on non-training days.
Each workout lists exercises with type, intensity (RPE 1-10 or HR zone), sets/reps/time.
Respect injuries and available equipment ({profile.equipment_text or 'None'}).
Each workout fits within {profile.exercise_duration}.

Respond only with valid JSON matching the schema.
"""

    try:
        response = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=4096,
            system="You are an expert trainer returning a single valid JSON object.",
            messages=[{"role": "user", "content": prompt}],
            tool_choice={"type": "tool", "name": "get_plan_json"},
            tools=[{"name": "get_plan_json", "description": "Generates 2-week plan", "input_schema": PLAN_SCHEMA}]
        )
        ai_data = response.content[0].input
        plan.plan_json = ai_data.get("plan_weeks", [])
        plan.plan_summary = ai_data.get("plan_summary", "Plan generated.")
        plan.save()
        logger.info(f"Training plan {plan_id} generated successfully")
    except Exception as e:
        logger.exception(f"Error generating plan {plan_id}: {str(e)}")
        plan.plan_json = {"error": str(e)}
        plan.plan_summary = f"Generation failed: {str(e)}"
        plan.save()


# Celery tester
@shared_task
def test_celery():
    """Simple Celery test to check task execution."""
    print("Celery task executed!")
    return "Celery working!"