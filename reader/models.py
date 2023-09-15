from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from reader.helper import ERROR_MESSAGES
from django.db import models

# Feedモデル
class Feed(models.Model):
    # フィードのURL
    url = models.URLField(unique=True)
    # フィードのタイトル
    title = models.CharField(max_length=100, unique=True)
    # フィードの説明
    description = models.TextField(blank=True, null=True)
    # フィードのURLとタイトルの重複をチェックする
    def clean(self):
        if Feed.objects.filter(url=self.url).exclude(id=self.id).exists():
            raise ValidationError({f'url': ERROR_MESSAGES['feed_url_duplicate_error']}) 
        if Feed.objects.filter(title=self.title).exclude(id=self.id).exists():
            raise ValidationError({f'title': ERROR_MESSAGES['feed_title_duplicate_error']})

    def __str__(self):
        return self.title

# Entryモデル
class Entry(models.Model):
    # フィード
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='entries')
    # エントリのタイトル
    title = models.CharField(null=False, max_length=100)
    # エントリのリンク
    link = models.URLField(null=False)
    # エントリの要約
    summary = models.TextField()
    # エントリの公開日時
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.title

# Subscriptionモデル
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    # ユーザーとフィードの組み合わせを文字列で返す
    def __str__(self):
        return f"{self.user.username}:{self.feed.title}"
    # ユーザーとフィードの組み合わせがユニークであることを保証する
    class Meta:
        unique_together = ('user', 'feed')