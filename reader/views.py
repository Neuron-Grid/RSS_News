from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feed, Subscription, Entry
from django.views.generic.detail import DetailView
from django.contrib import messages
import feedparser

# indexページ
def index(request):
    return render(request, 'reader/index.html')

# フィード一覧
@login_required
def feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})

# フィードの追加
@login_required
def add_feed(request):
    if request.method == 'POST':
        feed_url = request.POST.get('feed_url')
        feed = feedparser.parse(feed_url)
        if not feed:
            messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
            return render(request, 'reader/add_feed.html')
        if not feed.entries:
            messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
            return render(request, 'reader/add_feed.html')

        feed_title = feed['feed']['title']
        feed_description = feed['feed']['description']
        feed = Feed.objects.create(
            url=feed_url,
            title=feed_title,
            description=feed_description
            )
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
    return redirect('reader:feed_list')

# フィードの削除
@login_required
def delete_feed(request, feed_id):
    # ログインしているユーザーがフィードを購読しているかを確認し、登録されたフィードが0件だった場合エラーを表示
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() == 0:
        messages.error(request, 'フィードは購読されていません。')
        return redirect('reader:feed_list')
    # ログインしているユーザーがフィードを1件以上購読している場合は、フィードの追加時に指定したタイトルを表示し何を削除するかを選択させる
    # 削除ボタンを押すとフィードの購読が解除される
    # フィードの購読を解除すると、そのフィードに紐づく記事も削除される
    # 何も選択されなかった場合はフィード一覧に戻る
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() > 0:
        feed = Feed.objects.get(id=feed_id)
        if request.method == 'POST':
            feed.delete()
            return redirect('reader:feed_list')
        return render(request, 'reader/delete_feed.html', {'feed': feed})
    return redirect('reader:feed_list')

# フィードの詳細
@login_required
class FeedDetailView(DetailView):
    model = Feed
    template_name = 'reader/feed_detail.html'
    context_object_name = 'feed'