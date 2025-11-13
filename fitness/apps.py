from django.apps import AppConfig


class FitnessConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "fitness"


# imports signals so profiles are created/updated automatically
def ready(self):
    import fitness.signals
    _ = fitness.signals