from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Feed, Subscription, Entry
from django.views.generic.detail import DetailView
from django.contrib import messages
import feedparser
from .forms import AddFeedForm
from django.db import IntegrityError
from django.views.generic import ListView

# indexページ
def index(request):
    return render(request, 'reader/index.html')

# エラー処理
@login_required
def duplicate_error(request):
    return render(request, 'reader/duplicate_error.html')

# フィード一覧
@login_required
def feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})

# フィードの追加
@login_required
def add_feed(request):
    if request.method == 'POST':
        form = AddFeedForm(request.POST)
        if form.is_valid():
            feed_url = form.cleaned_data['url']
            feed = feedparser.parse(feed_url)
            if not feed:
                messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
                return render(request, 'reader/add_feed.html', {'form': form})
            if not feed.entries:
                messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
                return render(request, 'reader/add_feed.html', {'form': form})

            feed_title = form.cleaned_data['feed_name']
            feed_description = feed['feed']['description']
            try:
                feed = Feed.objects.create(
                    url=feed_url,
                    title=feed_title,
                    description=feed_description
                )
            except IntegrityError:
                return redirect('reader:duplicate_error')

            # エントリーを登録する
            for entry in feed.entries:
                Entry.objects.create(
                    feed=feed,
                    title=entry.get('title'),
                    link=entry.get('link'),
                    summary=entry.get('summary'),
                    pub_date=entry.get('published_parsed'),
                )

            Subscription.objects.create(user=request.user, feed=feed)
            return redirect('reader:feed_list')
    else:
        form = AddFeedForm()
    return render(request, 'reader/add_feed.html', {'form': form})


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
def remove_feed(request, feed_id):
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
        return render(request, 'reader/remove_feed.html', {'feed': feed})
    return redirect('reader:feed_list')

# フィードの詳細
@login_required
def feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})


class FeedDetailView(DetailView):
    model = Feed
    template_name = 'reader/feed_detail.html'
    context_object_name = 'feed'

class DetailedListView(ListView):
    model = Feed
    template_name = 'reader/detailed_list.html'
    context_object_name = 'feeds'

def detailed_list(request, feed_id):
    feed = Feed.objects.get(id=feed_id)
    entries = Entry.objects.filter(feed=feed)
    return render(request, 'reader/detailed_list.html', {'feed': feed, 'entries': entries})
