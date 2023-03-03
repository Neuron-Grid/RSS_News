from RSS_News.celery import shared_task
from reader.models import Subscription

@shared_task
def update_feeds():
    for subscription in Subscription.objects.all():
        subscription.feed.update()

