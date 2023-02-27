from django.utils.dateparse import parse_datetime as django_parse_datetime
from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
# from django.utils.dateparse import parse_datetime
from .models import Feed, Subscription, Entry
from django.shortcuts import render, redirect
from django.db import IntegrityError
from django.contrib import messages
from .forms import AddFeedForm
import feedparser
import datetime
# import time
import re

# indexページ
def index(request):
    return render(request, 'reader/index.html')

# 管理者ページ
def site_manager(request):
    return render(request, 'reader/site_manager.html') 

# エラー処理
@login_required
def duplicate_error(request):
    return render(request, 'reader/duplicate_error.html')

# エラー処理
@login_required
def formal_error(request):
    return render(request, 'reader/formal_error.html')

# エラー処理
@login_required
def delete_feed_error(request):
    return render(request, 'reader/delete_feed_error.html')

# フィード一覧
@login_required
def feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})

# 文字列値をdatetimeオブジェクトに変換する。
# @login_required
def custom_parse_datetime(value):
    # 既にdatetimeオブジェクトが渡されている場合はそのまま返す
    if isinstance(value, datetime.datetime):
        return value
    # valueがNoneの場合はNoneを返す
    if value is None:
        return None
    # valueがstr型の場合
    if isinstance(value, str):
        # 日付文字列のフォーマットを調整する
        for pattern in [
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?Z$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$',
        ]:
            match = re.match(pattern, value)
            if match:
                value = match.group(0)
                break
        else:
            return redirect('reader:formal_error')
        # datetimeオブジェクトに変換して返す
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            return redirect('reader:formal_error')

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
            entries = list(feed.entries)
            try:
                with transaction.atomic():
                    feed = Feed.objects.create(
                        url=feed_url,
                        title=feed_title,
                        description=feed_description,
                    )
                    # エントリーを登録する
                    for entry in entries:
                        try:
                            Entry.objects.create(
                                feed=feed,
                                title=entry.get('title', ''),
                                link=entry.get('link', ''),
                                summary=entry.get('summary', ''),
                                pub_date=custom_parse_datetime(entry.get('published', '')),
                            )
                        except ValueError:
                            return redirect('reader:formal_error')
                    Subscription.objects.create(user=request.user, feed=feed)
            except IntegrityError:
                return redirect('reader:duplicate_error')
        else:
            # フォームが無効な場合はエラーを表示する
            messages.error(request, '不正な値が入力されました。')
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

# フィードの削除
@login_required
def remove_feed(request, feed_id):
    # ログインしているユーザーがフィードを購読しているかを確認し、登録されたフィードが0件だった場合delete_feed_errorページにリダイレクトする
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() == 0:
        return redirect('reader:delete_feed_error')
    # フィードを削除するときは、remove_feedのページにリダイレクトし、そのフィードの削除確認をする。
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
def detailed_list(request, pk):
    feed = Feed.objects.get(id=pk)
    entries = Entry.objects.filter(
        feed=feed,
        title=request.GET.get('title', ''),
    ).order_by('-pub_date')
    
    if request.method == 'POST':
        update_feed(pk)
        # 更新が終了したら、再度詳細ページにリダイレクトする
        return redirect('reader:detailed_list', pk=pk)

    return render(request, 'reader/detailed_list.html', {
        'feed_id': pk,
        'entries': entries,
    })