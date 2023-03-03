from celery.schedules import crontab
from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSS_News.settings')

app = Celery('rss_news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

CELERY_TIMEZONE = 'Asia/Tokyo'
CELERY_BEAT_SCHEDULE = {
    'update-feeds': {
        'task': 'reader.tasks.update_feeds',
        'schedule': crontab(minute='*/5'),
    },
}