from celery import task
import feedparser
from django.utils import timezone
from .models import Feed, Entry

@task
def update_feed():
    # 登録されているフィードをすべて取得する
    feeds = Feed.objects.all()
    for feed in feeds:
        # フィードをパースする
        parsed_feed = feedparser.parse(feed.url)
        # エントリを更新する
        for entry in parsed_feed.entries:
            # エントリがDBに既に存在するかチェックする
            if not Entry.objects.filter(link=entry.link).exists():
                # エントリを作成する
                Entry.objects.create(
                    feed=feed,
                    title=entry.title,
                    link=entry.link,
                    summary=entry.summary,
                    pub_date=timezone.make_aware(entry.published_parsed)
                )
