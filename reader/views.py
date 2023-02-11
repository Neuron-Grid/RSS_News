from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feed, Subscription, Entry
import feedparser

# フィード一覧
@login_required
def index(request):
    subscriptions = Subscription.objects.filter(user=request.user)
    return render(request, 'reader/index.html', {'subscriptions': subscriptions})

# フィードの追加
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

# フィードの更新
@login_required
def update_feed(request, feed_id):
    feed = Feed.objects.get(id=feed_id)
    entries = feedparser.parse(feed.url)['entries']
    for entry in entries:
        Entry.objects.get_or_create(
            feed=feed,
            title=entry['title'],
            link=entry['link'],
            summary=entry['summary'],
            pub_date=entry['published'],
        )
    return redirect('reader:index')

# フィードの削除
@login_required
def delete_feed(request, feed_id):
    # ログインしているユーザーが一件もフィードを購読していない場合はエラーを表示
    if Subscription.objects.filter(user=request.user).count() == 1:
        return render(request, 'reader/delete_feed_error.html')
    Subscription.objects.filter(user=request.user, feed=feed_id).delete()
    # 購読しているフィードに登録されているタイトルを取得し、タイトルに紐づくエントリを削除
    feed_title = Feed.objects.get(id=feed_id).title
    Entry.objects.filter(feed__title=feed_title).delete()
    return redirect('reader:index')

