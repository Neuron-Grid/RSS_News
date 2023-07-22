from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from reader.helper import ERROR_MESSAGES
from django.db import models

# Feedモデル
class Feed(models.Model):
    url = models.URLField(unique=True)                      # フィードのURL
    title = models.CharField(max_length=100, unique=True)   # フィードのタイトル
    description = models.TextField(blank=True, null=True)   # フィードの説明

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
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='entries')    # フィード
    title = models.CharField(null=False, max_length=100)                                # エントリのタイトル
    link = models.URLField(null=False)                                                  # エントリのリンク
    summary = models.TextField()                                                        # エントリの要約
    pub_date = models.DateTimeField()                                                   # エントリの公開日時
    created_at = models.DateTimeField(auto_now_add=True)                                # エントリの作成日時

    def __str__(self):
        return self.title

# Subscriptionモデル
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}:{self.feed.title}"
    
    class Meta:
        unique_together = ('user', 'feed')