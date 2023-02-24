# Celery
import os
from celery import Celery
from celery.schedules import crontab

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

CELERY_BROKER_URL = 'redis://localhost:6379/1'  # RedisのURL
CELERY_RESULT_BACKEND = 'django-db'             # DBに結果を保存
CELERY_CACHE_BACKEND = 'django-cache'           # キャッシュに結果を保存
CELERY_TASK_TRACK_STARTED = True                # 開始時刻を記録