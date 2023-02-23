from django.contrib.auth.decorators import login_required
from django.views.generic.detail import DetailView
from django.db import IntegrityError, transaction
from .models import Feed, Subscription, Entry
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from .forms import AddFeedForm
import feedparser

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
            feed_title = form.cleaned_data['feed_name']
            feed = feedparser.parse(feed_url)
            if not feed:
                messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
                return render(request, 'reader/add_feed.html', {'form': form})
            if not feed.entries:
                messages.error(request, '指定されたURLのフィードにエントリがありません。')
                return render(request, 'reader/add_feed.html', {'form': form})
            feed_description = feed.get('feed', {}).get('description')
            # RelatedManagerオブジェクトをリストに変換する
            entries = list(feed.entries)
            try:
                with transaction.atomic():
                    feed = Feed.objects.create(
                        url=feed_url,
                        title=feed_title,
                        description=feed_description,
                    )
                    # エントリーを登録する
                    entries = [
                        Entry(
                            feed=feed,
                            title=entry.get('title', ''),
                            link=entry.get('link', ''),
                            summary=entry.get('summary', ''),
                            pub_date=entry.get('published_parsed'),
                        )
                        # 変数名を変更する
                        for entry in entries
                    ]
                    Entry.objects.bulk_create(entries)
                    Subscription.objects.create(user=request.user, feed=feed)
            except IntegrityError:
                return redirect('reader:duplicate_error')
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
    # ログインしているユーザーがフィードを購読しているかを確認し、登録されたフィードが0件だった場合delete_feed_errorページにリダイレクトする
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() == 0:
        return redirect('reader:delete_feed_error')
    # ログインしているユーザーがフィードを1件以上購読している場合は、フィードの追加時に指定したタイトルを表示し何を削除するかを選択させる
    # 削除ボタンを押すとフィードの購読が解除される
    # フィードの購読を解除すると、そのフィードに紐づく記事も削除される
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

@login_required
class FeedDetailView(DetailView):
    model = Feed
    template_name = 'reader/feed_detail.html'
    context_object_name = 'feed'

@login_required
def detailed_list(request, pk):
    feed = Feed.objects.get(id=pk)
    entries = Entry.objects.filter(feed=feed)
    return render(request, 'reader/detailed_list.html', {
        'feed_id': pk,
        'entries': entries,
        }
    )
