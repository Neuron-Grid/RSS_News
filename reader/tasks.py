from django.contrib.contenttypes.models import ContentType
from django.core.exceptions import ObjectDoesNotExist
from .models import Feed, Entry
from django.utils import timezone
from celery import shared_task
import feedparser

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
