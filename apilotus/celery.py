from __future__ import absolute_import

import os

from celery import Celery

from django.conf import settings


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'apilotus.settings')

app = Celery('apilotus', broker='redis://127.0.0.1')

app.config_from_object('django.conf:settings')
app.autodiscover_tasks(lambda: settings.LOCAL_APPS)
app.conf.update(
    CELERY_BROKER_URL='redis://127.0.0.1',
    CELERY_TASK_SERIALIZER='json',
    CELERY_ACCEPT_CONTENT=['json'],
    CELERY_RESULT_SERIALIZER='json',
)
