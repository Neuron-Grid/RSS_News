import feedparser
from celery import shared_task
from django.core.cache import cache
from reader.models import Feed, Entry

@shared_task
def update_feed(feed_id):
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
