import os

import celery
from raven.contrib.celery import register_logger_signal, register_signal

from ws.sentry import client

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'ws.settings')


class Celery(celery.Celery):
    @staticmethod
    def on_configure():  # pylint: disable=method-hidden
        if not client:
            return

        # register a custom filter to filter out duplicate logs
        register_logger_signal(client)

        # hook into the Celery error handler
        register_signal(client)


app = Celery('ws')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()
