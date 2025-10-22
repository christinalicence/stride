#Make sure celery is imported when django runs
from .celery import app as celery_app

__all__ = ('celery_app',)
