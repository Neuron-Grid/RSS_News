from django.shortcuts import render
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
import feedparser
from .models import Feed
from .models import Subscription


@login_required
def index(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'reader/index.html', {'subscriptions': subscriptions})


@login_required
def add_feed(request):
    if request.method == 'POST':
        feed_url = request.POST['feed_url']
        feed = feedparser.parse(feed_url)
        feed_title = feed['feed']['title']
        feed_description = feed['feed']['description']
        feed = Feed.objects.create(
            url=feed_url, title=feed_title, description=feed_description)
        Subscription.objects.create(user=request.user, feed=feed)
        return redirect('reader:index')
    return render(request, 'reader/add_feed.html')
