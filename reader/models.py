from django.contrib.auth.models import User
from django.db import models
from django.core.exceptions import ValidationError


# Feedモデル
class Feed(models.Model):
    url = models.URLField(unique=True)
    title = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.title

    def clean(self):
        if Feed.objects.filter(url=self.url).exclude(id=self.id).exists():
            raise ValidationError('既に登録されているフィードです。')


# Entryモデル
class Entry(models.Model):
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)
    title = models.CharField()
    link = models.URLField()
    summary = models.TextField()
    pub_date = models.DateTimeField()

    def __str__(self):
        return self.title


# Subscriptionモデル
class Subscription(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    feed = models.ForeignKey(Feed, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username}:{self.feed.title}"
