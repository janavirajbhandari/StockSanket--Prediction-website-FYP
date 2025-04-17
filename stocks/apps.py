from django.apps import AppConfig

class StocksConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'stocks'  # ✅ Make sure this matches the app name exactly
