import os
from celery import Celery
from django.conf import settings

# Set the default Django settings module for the 'celery' program.
# Replace 'stride.settings' with 'your_project_name.settings'
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "strideai.settings")

# Create Celery application instance
app = Celery("strideai")

# Using a string here means the worker doesn't have to serialize
# the configuration object to child processes.
# - namespace='CELERY' means all celery-related configuration keys
#   should have a `CELERY_` prefix in settings.py.
app.config_from_object("django.conf:settings", namespace="CELERY")

# Load task modules from all registered Django app configs.
app.autodiscover_tasks()
