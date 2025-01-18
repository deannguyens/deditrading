import os
from celery import Celery

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "api.settings")
app = Celery("api", include=["api.asset_address.task.cron"])
app.config_from_object("django.conf:settings", namespace="CELERY")
app.autodiscover_tasks()