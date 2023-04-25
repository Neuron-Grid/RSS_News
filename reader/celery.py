from celery import Celery
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSS_News.settings')

app = Celery('rss_news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

CELERY_BROKER_URL = 'redis://localhost:6379/0'                                          # RedisのURL
CELERY_RESULT_BACKEND = "db+mysql://{DB_USER}:{DB_PASSWORD}@127.0.0.1/{DB_NAME}"        # DBに結果を保存
CELERY_BEAT_SCHEDULER = 'django_celery_beat.schedulers:DatabaseScheduler'
CELERY_TASK_TRACK_STARTED = True                                                        # 開始時刻を記録
CELERY_TIMEZONE = 'Asia/Tokyo'

CELERY_BEAT_SCHEDULE = {
    'update-feeds': {
        'task': 'feeds.tasks.update_feeds',
        'schedule': 300.0,
    },
}