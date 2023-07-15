from celery import Celery
from reader.redis_helper import get_redis_connection, get_feeds_to_update
from reader.tasks import update_feed
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSS_News.settings')

app = Celery('rss_news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, update_feeds.s(), name='5分ごとにフィードを自動更新')

@app.task
def update_feeds():
    redis_conn = get_redis_connection()
    feed_ids = get_feeds_to_update(redis_conn)
    for feed_id in feed_ids:
        update_feed.delay(feed_id)
