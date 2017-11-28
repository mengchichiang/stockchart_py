from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'stockchart.settings')

app = Celery('stockchart', result_backend='rpc://', broker='pyamqp://guest@localhost//')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks() #自動尋找在 django installed apps 內的所有tasks,不須要設定CELERY_IMPORTS參數

from celery.schedules import crontab
from .tasks import downloadDataTask

@app.task
def downloadDataTask_celery():
  #print("downloadDataTask_celery...")
  downloadDataTask()

app.conf.beat_schedule = {
    'download-data-every-4-hour': {
        'task': 'stockchart.celery.downloadDataTask_celery',
        'schedule': crontab(minute=0, hour='*/4'),
    },
}
app.conf.timezone = 'UTC'


