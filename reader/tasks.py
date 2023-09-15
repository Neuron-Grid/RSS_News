from reader.helper import schedule_feed, DATE_FORMAT_STR
from django.core.cache import cache
from django.conf import settings
from celery import shared_task
from reader.models import Feed
from datetime import datetime
from celery import group
import feedparser
import pytz
import time
import re

@shared_task
def update_feed(feed_id):
    # AppRegistryNotReadyを回避する為、ここでimportする
    from reader.models import Entry 
    feed = Feed.objects.get(id=feed_id)
    try:
        parse = feedparser.parse(feed.url)
    except Exception as e:
        print(f"フィード解析中にエラーが発生しました。 {feed.url}: {e}")
        return

    for entry_data in parse.entries:
        entry, _ = Entry.objects.get_or_create(
            feed=feed,
            link=entry_data.get('link'),
            defaults={
                'title': entry_data.get('title'),
                'summary': entry_data.get('summary')
            }
        )
        pub_date = entry_data.get('published_parsed') or entry_data.get('updated_parsed')
        if pub_date:
            if isinstance(pub_date, time.struct_time):
                entry.pub_date = datetime.fromtimestamp(time.mktime(pub_date), pytz.timezone(settings.CELERY_TIMEZONE))
            elif isinstance(pub_date, str):
                for date_format, strptime_format in DATE_FORMAT_STR.items():
                    if re.match(date_format, pub_date):
                        entry.pub_date = datetime.strptime(pub_date, strptime_format)
                        break
        entry.save()
    cache.delete(f'feed_{feed_id}')
    schedule_feed(feed_id)

# views.pyのupdate_all_feeds_task関数を参照
@shared_task
def update_all_feeds_task(user_id):
    feed_ids = Feed.objects.filter(subscription__user_id=user_id).values_list('id', flat=True)
    update_feed_tasks = [update_feed.s(feed_id) for feed_id in feed_ids]
    group(update_feed_tasks)()