from django.core.exceptions import ValidationError
from django.contrib.auth.models import User
from django.db import models

# Feedモデル
class Feed(models.Model):
    url = models.URLField(unique=True)                      # フィードのURL
    title = models.CharField(max_length=100, unique=True)   # フィードのタイトル
    description = models.TextField(blank=True, null=True)   # フィードの説明

    # フィードのURLとタイトルの重複をチェックする
    def clean(self):
        if Feed.objects.filter(url=self.url).exclude(id=self.id).exists():
            raise ValidationError({'url': 'フィードのURLが重複しています。'}) 
        if Feed.objects.filter(title=self.title).exclude(id=self.id).exists():
            raise ValidationError({'title': 'フィードのタイトルが重複しています。'})

    def __str__(self):
        return self.title

# Entryモデル
class Entry(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE, related_name='entries')    # フィード
    title = models.CharField(null=False, max_length=100)                                # エントリのタイトル
    link = models.URLField(null=False)                                                  # エントリのリンク
    summary = models.TextField()                                                        # エントリの要約
    pub_date = models.DateTimeField(auto_now_add=True)                                  # エントリの公開日時

    def __str__(self):
        return self.title

# Subscriptionモデル
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}:{self.feed.title}"