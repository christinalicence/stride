import json
import os
import logging
from celery import shared_task
from anthropic import Anthropic
from django.conf import settings
from .models import TrainingPlan

# Initialize logger
logger = logging.getLogger(__name__)

# --- JSON SCHEMA DEFINITION ---
# This is the key to forcing the AI to return valid, structured JSON.
# It should be defined outside the task for cleaner code.
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_title": {"type": "string", "description": "A short, descriptive title for the plan."},
        "plan_summary": {"type": "string", "description": "A brief summary of the two-week plan."},
        "plan_weeks": {
            "type": "array",
            "description": "An array containing details for Week 1 and Week 2.",
            "items": {
                "type": "object",
                "properties": {
                    "week_number": {"type": "integer"},
                    "days": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "day": {"type": "string", "description": "Day of the week (e.g., Monday)."},
                                "workout": {
                                    "type": "array",
                                    "description": "List of exercises for the day, or ['Rest Day'].",
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "exercise": {"type": "string"},
                                            "type": {"type": "string", "enum": ["strength", "cardio", "flexibility"]},
                                            "sets": {"type": "integer"},
                                            "reps": {"type": "string", "description": "Use string for reps, time, or distance (e.g., '12', '30 sec', '5 km')."},
                                            "intensity": {"type": "integer", "description": "RPE (Rate of Perceived Exertion) 1-10."}
                                        },
                                        "required": ["exercise", "type", "sets", "reps", "intensity"]
                                    }
                                }
                            },
                            "required": ["day", "workout"]
                        }
                    }
                },
                "required": ["week_number", "days"]
            }
        }
    },
    "required": ["plan_title", "plan_summary", "plan_weeks"]
}

# --- TRAINING PLAN GENERATION TASK ---
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
        "fitness_level": getattr(profile, "fitness_level", "unknown"),
        "exercise_days_per_week": getattr(profile, "exercise_days_per_week", 3),
        "exercise_duration": getattr(profile, "exercise_duration", "30 min"),
        "equipment_text": getattr(profile, "equipment_text", "None"),
        "weight_kg": getattr(profile, "weight_kg", 0),
        "height_cm": getattr(profile, "height_cm", 0),
        "age": getattr(profile, "age", 0),
        "gender": getattr(profile, "gender", None),
        "long_term_injuries": getattr(profile, "injuries_and_limitations", ""),
        "minor_injuries": plan.minor_injuries or ""
    }

    # Safe handling for user preferences
    user_preferences = "None"
    if plan.plan_json and isinstance(plan.plan_json, dict):
        user_preferences = plan.plan_json.get("user_preferences", "None")


    # Construct the prompt for the AI model
    prompt = f"""You are an expert fitness coach. Your task is to generate a comprehensive 2-week training plan.

Previous plan summary and feedback: {feedback_context}
User profile data: {json.dumps(profile_data, separators=(',', ':'))}
User preferences/goals: {user_preferences}

**PLAN RULES:**
1. **Duration:** Exactly 2 weeks, with training days matching `exercise_days_per_week` ({profile.exercise_days_per_week}).
2. **Rest:** Designate rest days on all non-training days.
3. **Format:** Each workout must list exercises including the type, intensity (RPE 1-10), and sets/reps/time.
4. **Safety:** Strictly respect all injuries and available equipment ({profile.equipment_text or 'None'}).
5. **Time:** The total time for each workout must fit within the user's specified duration ({profile.exercise_duration}).

Use the `get_plan_json` tool to return the complete plan. Do not include any text, conversation, or markdown (like ```json) outside of the tool's input.
"""

    try:
        # 1. Call the Claude API
        response = client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=4096,
            system="You are an expert trainer returning a single valid JSON object.",
            messages=[{"role": "user", "content": prompt}],
            tool_choice={"type": "tool", "name": "get_plan_json"},
            tools=[{"name": "get_plan_json", "description": "Generates 2-week plan based on user profile and rules.", "input_schema": PLAN_SCHEMA}]
        )

        # 2. Extract and Parse AI response safely
        # When using tool_choice, the response content is a list of ToolUse blocks.
        if response.content and response.content[0].type == 'tool_use':
            tool_use = response.content[0]
            if tool_use.name == 'get_plan_json':
                ai_data = tool_use.input
                plan.plan_json = ai_data.get("plan_weeks", [])
                plan.plan_summary = ai_data.get("plan_summary", "Plan generated.")
                plan.plan_title = ai_data.get("plan_title", plan.plan_title or "New Training Plan")
                plan.save()
                logger.info(f"Training plan {plan_id} generated successfully")
            else:
                raise ValueError(f"Unexpected tool used: {tool_use.name}")
        else:
             raise ValueError("AI response did not contain a tool use block.")


    except Exception as e:
        logger.exception(f"Error generating plan {plan_id}: {str(e)}")
        plan.plan_json = {"error": f"Generation failed: {str(e)}"}
        plan.plan_summary = f"Generation failed: {str(e)}"
        plan.save()


# Celery tester (kept for completeness)
@shared_task
def test_celery():
    """Simple Celery test to check task execution."""
    print("Celery task executed!")
    return "Celery working!"