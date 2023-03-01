from django.core.exceptions import ObjectDoesNotExist
from .models import Feed, Entry
from django.utils import timezone
from celery import shared_task
from celery import Celery
import feedparser
from django.conf import settings

app = Celery('rss_news')

# Celeryタスク
@shared_task
def update_feeds():
    feeds = Feed.objects.all()
    for feed in feeds:
        parsed_feed = feedparser.parse(feed.url)
        for entry in parsed_feed.entries:
            try:
                Entry.objects.get(link=entry.link)
            except ObjectDoesNotExist:
                new_entry = Entry(
                    feed=feed,
                    title=entry.title,
                    link=entry.link,
                    summary=entry.summary,
                    pub_date=timezone.make_aware(entry.published_parsed),
                )
            new_entry.save()
    # エントリーの総数が500件を超えたら、日時が古い物から順番にエントリーを削除する
    # entries_count = Entry.objects.count()
    # if entries_count > 500:
    #     entries_to_delete = entries_count - 500
    #     oldest_entries = Entry.objects.order_by('pub_date')[:entries_to_delete]
    #     oldest_entries.delete()