import json
import os
import logging
from celery import shared_task
from anthropic import Anthropic
from django.conf import settings
from .models import UserProfile, TrainingPlan

logger = logging.getLogger(__name__)


@shared_task
def generate_training_plan_task(plan_id):
    """Asynchronous task to generate a training plan using the Claude API."""
    client = Anthropic(api_key=os.getenv('CLAUDE_API_KEY', settings.CLAUDE_API_KEY))
    #Error checking
    try:
        plan = TrainingPlan.objects.get(id=plan_id)
    except TrainingPlan.DoesNotExist:
        logger.error(f"TrainingPlan with id {plan_id} does not exist")
        return   
    profile = plan.user

    # Check for previous plan feedback
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

    # Data from user profile - with safe attribute access
    profile_data = {
        "fitness_level": profile.fitness_level,
        "exercise_days_per_week": profile.exercise_days_per_week,
        "exercise_duration": profile.exercise_duration,
        "equipment_text": profile.equipment_text,
        "weight_kg": profile.weight_kg,
        "height_cm": profile.height_cm,
        "age": profile.age,
        "gender": getattr(profile, 'gender', None),  # Safe access in case field doesn't exist yet
        "long_term_injuries": profile.long_term_injuries,
        "injury_limitations": profile.injury_limitations,
        "minor_injuries": profile.minor_injuries,
    }

    # Define output format
    PLAN_SCHEMA = {
        "type": "object",
        "properties": {
            "plan_summary": {
                "type": "string", 
                "description": "A concise, actionable, and encouraging summary for the next two weeks."
            },
            "plan_weeks": {
                "type": "array",
                "description": "A detailed structure for exactly 2 weeks of training.",
                "items": {
                    "type": "object",
                    "properties": {
                        "week_number": {
                            "type": "integer", 
                            "description": "1 or 2."
                        },
                        "focus": {
                            "type": "string", 
                            "description": "The main goal for this week (e.g., Strength endurance, High-intensity cardio, Active recovery)."
                        },
                        "workouts": {
                            "type": "array",
                            "items": {
                                "type": "object",
                                "properties": {
                                    "suggested_day": {
                                        "type": "string", 
                                        "description": "E.g., Monday, Wednesday, Rest Day."
                                    },
                                    "workout_title": {
                                        "type": "string", 
                                        "description": "Short, descriptive title for the session (e.g., Full Body Push, Long Run Tempo)."
                                    },
                                    "total_length_minutes": {
                                        "type": "integer", 
                                        "description": "Total duration of the workout, including warm-up/cool-down."
                                    },
                                    "exercises": {
                                        "type": "array",
                                        "description": "Detailed steps or individual movements within the session.",
                                        "items": {
                                            "type": "object",
                                            "properties": {
                                                "exercise_name": {
                                                    "type": "string", 
                                                    "description": "Specific exercise name (e.g., Barbell Squat, Treadmill Run, Yoga Flow)."
                                                },
                                                "exercise_type": {
                                                    "type": "string", 
                                                    "description": "Type of movement (e.g., Compound Lift, Isolation, Interval, Steady State)."
                                                },
                                                "intensity": {
                                                    "type": "string", 
                                                    "description": "RPE (Rate of Perceived Exertion 1-10) or specific weight/speed guidance (e.g., RPE 7-8, 70% 1RM, Zone 2 HR)."
                                                },
                                                "details": {
                                                    "type": "string", 
                                                    "description": "Sets and Reps, Distance, or Time (e.g., 3 sets of 10 reps, 3 x 800m intervals, 30 minutes)."
                                                },
                                            },
                                            "required": ["exercise_name", "exercise_type", "intensity", "details"]
                                        }
                                    }
                                },
                                "required": ["suggested_day", "workout_title", "total_length_minutes", "exercises"]
                            }
                        }
                    },
                    "required": ["week_number", "focus", "workouts"]
                }
            }
        },
        "required": ["plan_summary", "plan_weeks"]
    }

    # Construct the prompt
    prompt = f"""
You are an expert fitness coach. Create a personalized 2-week training plan for the user based on their profile and previous plan feedback.
Your primary goal is to generate a safe, effective, and engaging plan that aligns with their goals and limitations.

Previous Plan Feedback:
{feedback_context}

Current Goals:
- Goal Type: {plan.goal_type}
- Target Event: {plan.target_event or 'General fitness'}
- Target Date: {plan.target_date or 'No specific date'}

User Profile: {json.dumps(profile_data, indent=2)}

RULES FOR GENERATION:
1. The plan MUST contain exactly two weeks (week_number 1 and 2).
2. The total number of workouts per week MUST match the user's "exercise_days_per_week" field ({profile.exercise_days_per_week} days). Use 'Rest Day' for non-training days.
3. Every workout MUST detail multiple specific exercises, their type, a clear intensity measure, and sets/reps/distance in the 'details' field.
4. The intensity field must use RPE (1-10) for strength, or HR zones/speed guidance for cardio.
5. Take into account any injuries or limitations mentioned in the user profile.
6. Respect the user's available equipment: {profile.equipment_text or 'Not specified'}
7. Each workout should fit within their typical duration: {profile.exercise_duration}
"""

    try:
        # Call the Claude API
        response = client.messages.create(
            model="claude-sonnet-4-20250514",  
            max_tokens=4096,
            system="You are an expert personal trainer who ONLY responds with a single, valid JSON object following the provided schema.",
            messages=[{"role": "user", "content": prompt}],
            tool_choice={"type": "tool", "name": "get_plan_json"},
            tools=[{
                "name": "get_plan_json", 
                "description": "Generates the 2-week fitness plan.", 
                "input_schema": PLAN_SCHEMA
            }]
        )
        
        # Extract JSON 
        tool_use_block = response.content[0]
        ai_data = tool_use_block.input

        # Update the plan model instance
        plan.plan_json = ai_data.get('plan_weeks', [])
        plan.plan_summary = ai_data.get('plan_summary', 'Plan generated successfully.')
        plan.save()
        
        logger.info(f"Successfully generated training plan {plan_id}")
        
    except (json.JSONDecodeError, IndexError, AttributeError, KeyError) as e:
        # Handle API or JSON parsing errors
        error_msg = f"Error processing Claude response for plan {plan_id}: {str(e)}"
        logger.error(error_msg)
        plan.plan_summary = f"Generation failed due to API/JSON error: {str(e)}"
        plan.plan_json = {"error": error_msg}
        plan.save()
    except Exception as e:
        error_msg = f"An unexpected error occurred for plan {plan_id}: {str(e)}"
        logger.exception(error_msg)  # .exception() includes the full traceback
        plan.plan_summary = f"Generation failed unexpectedly: {str(e)}"
        plan.plan_json = {"error": error_msg}
        plan.save()


# Celery Tester
@shared_task
def test_celery():
    print("✅ Celery test task executed successfully!")
    return "Celery is working fine!"