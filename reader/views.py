from django.contrib.auth.decorators import login_required
from django.db import IntegrityError, transaction
from .models import Feed, Subscription, Entry
from django.shortcuts import render, redirect
# from celery.result import AsyncResult
from django.contrib import messages
from .forms import AddFeedForm
import feedparser
import datetime
import re

# indexページ
def index(request):
    return render(request, 'reader/index.html')

# エラー処理
@login_required
def error_page(request):
    return render(request, 'reader/error_page.html')

# フィード一覧
@login_required
def feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})

# 文字列値をdatetimeオブジェクトに変換する。
# 変換できなければ、formal_error.htmlにリダイレクトする。
def custom_parse_datetime(value, request):
    # 既にdatetimeオブジェクトが渡されている場合はそのまま返す
    if isinstance(value, datetime.datetime):
        return value
    # valueがNoneの場合はNoneを返す
    if value is None:
        return None
    # valueがstr型の場合
    if isinstance(value, str):
        # 日付のフォーマットを調整する
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
            messages.error(request, 'RSSフィードの日付のフォーマットが正しくない場合に発生します。\nもしくは、フィードのパースに失敗した場合に発生します。')
            return redirect('reader:error_page')
            # return redirect('reader:formal_error')
        # datetimeオブジェクトに変換して返す
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            messages.error('RSSフィードの日付のフォーマットが正しくない場合に発生します。\nもしくは、フィードのパースに失敗した場合に発生します。')
            return redirect('reader:error_page')
            # return redirect('reader:formal_error')

# フィードの追加
@login_required
def add_feed(request):
    # POSTリクエストの場合（フォームが送信された場合）
    if request.method == 'POST':
        # フォームのインスタンスを作成し、送信されたデータをバインドする
        form = AddFeedForm(request.POST)
        # フォームのバリデーションを行う
        if form.is_valid():
            # バリデーションが成功した場合、クリーンデータからフィードのURLとタイトルを取得する
            feed_url = form.cleaned_data['url']
            feed_title = form.cleaned_data['feed_name']
            # フィードをパースする
            feed = feedparser.parse(feed_url)
            # フィードが存在しない場合、エラーメッセージを表示して同じページに留まる
            if not feed:
                messages.error(request, '指定されたURLのフィードが見つかりませんでした。')
                return render(request, 'reader/add_feed.html', {'form': form})
            # フィードにエントリがない場合、エラーメッセージを表示して同じページに留まる
            if not feed.entries:
                messages.error(request, '指定されたURLのフィードにエントリがありません。')
                return render(request, 'reader/add_feed.html', {'form': form})
            # フィードの説明を取得する
            feed_description = feed.get('feed', {}).get('description')
            # フィードのエントリをリストとして取得する
            entries = list(feed.entries)
            try:
                # データベースの操作をアトミック（一体化）に行う
                with transaction.atomic():
                    # フィードをデータベースに保存する
                    feed = Feed.objects.create(
                        url=feed_url,
                        title=feed_title,
                        description=feed_description,
                    )
                    # 各エントリをデータベースに保存する
                    for entry in entries:
                        try:
                            Entry.objects.create(
                                feed=feed,
                                title = entry.get('title', ''),
                                link = entry.get('link', ''),
                                summary = entry.get('summary', ''),
                                pub_date = custom_parse_datetime(request, entry.get('published', ''))
                            )
                        except ValueError:
                            # 日付のパースに失敗した場合、エラーメッセージを表示してエラーページにリダイレクトする
                            messages.error(request, '日付のパースに失敗しました。\n RSSフィードの日付のフォーマットが正しくない場合に発生します。\nもしくは、フィードのパースに失敗した場合に発生します。')
                            return redirect('reader:error_page')
                    # ユーザーの購読をデータベースに保存する
                    Subscription.objects.create(user=request.user, feed=feed)
            except IntegrityError:
                # 既に登録されているフィードの場合、エラーメッセージを表示してエラーページにリダイレクトする
                messages.error(request, '既に登録されているフィードです。')
                return redirect('reader:error_page')
            # フォームの送信とデータの保存が成功した場合、フィードリストのページにリダイレクトする
            return redirect('reader:feed_list')
        else:
            # フォームのバリデーションが失敗した場合、エラーメッセージを表示してエラーページにリダイレクトする
            messages.error(request, '不正な値が入力されました。')
            return redirect('reader:error_page')
    else:
        # GETリクエストの場合(ページが初めて表示された場合)に、新しい（空の）フォームを作成する
        form = AddFeedForm()
    # フォームをテンプレートに渡してレンダリングする
    return render(request, 'reader/add_feed.html', {'form': form})


# フィードの更新
# postを受け取った場合だけフィードを更新する
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
    return redirect('reader:feed_list', pk=feed_id)

# フィードの削除
@login_required
def remove_feed(request, feed_id):
    # ログインしているユーザーがフィードを購読しているかを確認し、登録されたフィードが0件だった場合delete_feed_errorページにリダイレクトする
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() == 0:
        return redirect('reader:delete_feed_error')
    # フィードを削除するときは、remove_feedのページにリダイレクトし、そのフィードの削除確認をする。
    # フィードの購読を解除すると、そのフィードに紐づく記事も削除される
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() > 0:
        feed = Feed.objects.get(id=feed_id)
        if request.method == 'POST':
            feed.delete()
            return redirect('reader:feed_list')
        return render(request, 'reader/remove_feed', {'feed': feed})
    return redirect('reader:feed_list')

# フィードの詳細
@login_required
def detailed_list(request, pk):
    feed = Feed.objects.get(id=pk)
    entries = Entry.objects.filter(feed=feed).order_by('pub_date')
    # entry.titleを表示させる
    title = feed.title
    return render(request, 'reader/detailed_list.html', {'entries': entries})