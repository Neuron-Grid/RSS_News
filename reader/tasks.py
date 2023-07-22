from reader.helper import get_redis_connection, schedule_feed
# from reader.models import Feed, Entry 
from django.core.cache import cache
from celery import shared_task
import feedparser

@shared_task
def update_feed(feed_id):
    from reader.models import Feed, Entry
    feed = Feed.objects.get(id=feed_id)
    d = feedparser.parse(feed.url)
    for entry_data in d.entries:
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
    schedule_feed(get_redis_connection(), feed_id)
