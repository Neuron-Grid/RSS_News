from reader.helper import schedule_feed
from django.core.cache import cache
from django.conf import settings
from celery import shared_task
from reader.models import Feed
import feedparser

broker_url = settings.CELERY_BROKER_URL

@shared_task
def update_feed(feed_id):
    # AppRegistryNotReadyを回避する為、ここでimportする
    from reader.models import Entry
    feed = Feed.objects.get(id=feed_id)
    parse = feedparser.parse(feed.url)
    for entry_data in parse.entries:
        entry, _ = Entry.objects.get_or_create(
            feed=feed,
            link=entry_data.get('link'),
            defaults={
                'title': entry_data.get('title'),
                'summary': entry_data.get('summary')
            }
        )
        entry.pub_date = entry_data.get('published_parsed') or entry_data.get('updated_parsed')
        entry.save()
    cache.delete(f'feed_{feed_id}')
    schedule_feed(broker_url, feed_id)

# 特定のユーザーが購読している全てのフィードを更新する
# views.pyのpdate_all_feeds_task関数を参照
@shared_task
def update_all_feeds_task():
    for feed in Feed.objects.all():
        update_feed.delay(feed.id)