import json
import os
import logging
from celery import shared_task
from anthropic import Anthropic
from django.conf import settings
from .models import TrainingPlan

logger = logging.getLogger(__name__)

# --- JSON SCHEMA DEFINITION ---
PLAN_SCHEMA = {
    "type": "object",
    "properties": {
        "plan_title": {
            "type": "string",
            "description": "A short, descriptive title for the plan.",
        },
        "plan_summary": {
            "type": "string",
            "description": "A brief summary of the two-week plan.",
        },
        "plan_weeks": {
            "type": "array",
            "description": ("An array containing details " "for Week 1 and Week 2."),
            "items": {
                "type": "object",
                "properties": {
                    "week_number": {"type": "integer"},
                    "days": {
                        "type": "array",
                        "items": {
                            "type": "object",
                            "properties": {
                                "day": {
                                    "type": "string",
                                    "description": (
                                        "Day of the week " "(e.g., Monday)."
                                    ),
                                },
                                "workout": {
                                    "type": "array",
                                    "description": (
                                        "List of exercises for the day. "
                                        "For rest days, return a single"
                                        "object with exercise='Rest Day'."
                                    ),
                                    "items": {
                                        "type": "object",
                                        "properties": {
                                            "exercise": {"type": "string"},
                                            "type": {
                                                "type": "string",
                                                "enum": [
                                                    "strength",
                                                    "cardio",
                                                    "flexibility",
                                                    "rest",
                                                ],
                                            },
                                            "sets": {"type": ["integer", "null"]},
                                            "reps": {
                                                "type": ["string", "null"],
                                                "description": (
                                                    "Use string for reps, "
                                                    "time or distance (e.g., "
                                                    "'12', 30 sec', '5 km'). "
                                                    "Null for rest days."
                                                ),
                                            },
                                            "intensity": {
                                                "type": ["integer", "null"],
                                                "description": (
                                                    "RPE (Rate of Perceived "
                                                    "Exertion) "
                                                    "1–10. Null for rest days."
                                                ),
                                            },
                                        },
                                        "required": ["exercise", "type"],
                                    },
                                },
                            },
                            "required": ["day", "workout"],
                        },
                    },
                },
                "required": ["week_number", "days"],
            },
        },
    },
    "required": ["plan_title", "plan_summary", "plan_weeks"],
}


@shared_task
def generate_training_plan_task(plan_id):
    """Generate a 2-week training plan using Claude API."""
    client = Anthropic(api_key=os.getenv("CLAUDE_API_KEY", settings.CLAUDE_API_KEY))

    try:
        plan = TrainingPlan.objects.get(id=plan_id)
    except TrainingPlan.DoesNotExist:
        logger.error("TrainingPlan %s not found", plan_id)
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
        "Fitness_Level": profile.get_fitness_level_display(),
        "Exercise_Duration_Minutes": profile.get_exercise_duration_display(),
        "exercise_duration": getattr(profile, "exercise_duration", "30 min"),
        "equipment_text": getattr(profile, "equipment_text", "None"),
        "long_term_injuries": getattr(profile, "injuries_and_limitations", ""),
        "minor_injuries": plan.minor_injuries or "",
    }

    user_preferences = "None"
    if plan.plan_json and isinstance(plan.plan_json, dict):
        user_preferences = plan.plan_json.get("user_preferences", "None")

    # Build prompt
    prompt = f"""
You are an expert fitness coach. Your task is to generate a comprehensive
2-week training plan.

Previous plan summary and feedback: {feedback_context}
User profile data: {json.dumps(profile_data, separators=(',', ':'))}
User preferences/goals: {user_preferences}

PLAN RULES:
1. Duration: Exactly 2 weeks, with training days
   matching `exercise_days_per_week`
   ({profile.exercise_days_per_week}).
2. Rest Days: For rest days, return EXACTLY ONE exercise object with:
   - "exercise": "Rest Day"
   - "type": "rest"
   - DO NOT include sets, reps, or intensity fields
   Example: {{"exercise": "Rest Day", "type": "rest"}}
3. Training Days: Each workout must list exercises including:
   - exercise name
   - type (strength/cardio/flexibility)
   - sets (integer)
   - reps (string - e.g. '12', '30 sec', '5 km')
   - intensity (RPE 1-10)
4. Safety: Respect all injuries and available equipment
   ({profile.equipment_text or 'None'}).
5. Time: Each workout must fit within the user's specified duration
   ({profile.exercise_duration}).

CRITICAL: Your response MUST include:
1. plan_title (string)
2. plan_summary (string)
3. plan_weeks (array with 2 weeks of complete training data)

Never return incomplete data. Always generate the full 2-week plan structure.

Use the `get_plan_json` tool to return the complete plan.
Do not include any text, conversation, or markdown outside of the tool's input.
"""

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=4096,
            system=(
                "You are an expert fitness trainer. "
                "You MUST return a complete training plan "
                "using the get_plan_json tool. "
                "The response MUST include: plan_title, "
                "plan_summary, and plan_weeks "
                "(with all weeks, days, and exercises). "
                "For rest days, use: "
                "{'exercise': 'Rest Day', 'type': 'rest'}. "
                "Never return partial data, "
                "always include the complete 2-week plan structure."
            ),
            messages=[{"role": "user", "content": prompt}],
            tool_choice={"type": "tool", "name": "get_plan_json"},
            tools=[
                {
                    "name": "get_plan_json",
                    "description": (
                        "Generates 2-week plan based " "on user profile and rules."
                    ),
                    "input_schema": PLAN_SCHEMA,
                }
            ],
        )

        if response.content and response.content[0].type == "tool_use":
            tool_use = response.content[0]
            if tool_use.name == "get_plan_json":
                ai_data = tool_use.input
                if "plan_weeks" not in ai_data or not ai_data["plan_weeks"]:
                    raise ValueError("AI did not return plan_weeks data")
                plan.plan_json = ai_data
                plan.plan_summary = ai_data.get("plan_summary", "Plan generated.")
                plan.plan_title = ai_data.get(
                    "plan_title", plan.plan_title or "New Training Plan"
                )
                plan.save()
                logger.info("Training plan %s generated successfully", plan_id)
            else:
                raise ValueError(f"Unexpected tool used: {tool_use.name}")
        else:
            raise ValueError("AI response did not contain a tool use block.")

    except Exception as exc:
        logger.exception("Error generating plan %s: %s", plan_id, str(exc))
        plan.plan_json = {"error": f"Generation failed: {exc}"}
        plan.plan_summary = f"Generation failed: {exc}"
        plan.save()
