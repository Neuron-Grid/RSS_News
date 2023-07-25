from RSS_News.settings import CELERY_BROKER_URL
from reader.helper import get_feeds_to_update
from celery import Celery
import redis
import os

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'RSS_News.settings')

app = Celery('rss_news')
app.config_from_object('django.conf:settings', namespace='CELERY')
app.autodiscover_tasks()
app.conf.broker_url = CELERY_BROKER_URL

# Redis接続の生成
redis_connection = redis.Redis.from_url(app.conf.broker_url)

@app.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(300.0, update_feeds.s(), name='5分ごとにフィードを自動更新')

@app.task
def update_feeds():
    # AppRegistryNotReadyを回避する為、ここでimportする
    from reader.tasks import update_feed
    feed_ids = get_feeds_to_update(redis_connection)
    for feed_id in feed_ids:
        update_feed.delay(feed_id)
