from django.contrib.auth.decorators import login_required
from reader.models import Feed, Subscription, Entry
from django.db import IntegrityError, transaction
from reader.error_message import ERROR_MESSAGES
from django.shortcuts import render, redirect
# from celery.result import AsyncResult
from reader.forms import AddFeedForm
from django.contrib import messages
import feedparser
import datetime
import re

# エラーメッセージ
def get_error_message(error_code):
    error_message = ERROR_MESSAGES.get(error_code, '予期せぬエラーが発生しました。\n 操作の詳細を管理者に報告してください。')
    return error_message

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
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}:\d{2}$', 
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}:\d{2}$', 
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}:\d{2}$', 
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}$',
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?[+-]\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$',
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}(\.\d+)?$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}(\.\d+)?$',
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2}T\d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2} \d{2}:\d{2}$',
            r'^\d{4}/\d{2}/\d{2} \d{2}:\d{2}$',
            r'^\d{4}-\d{2}-\d{2}$',
            r'^\d{4}/\d{2}/\d{2}$',
            r'^\d{2}-\d{2}-\d{4}$',
            r'^\d{2}/\d{2}/\d{4}$',
        ]:
            match = re.match(pattern, value)
            if match:
                value = match.group(0)
                break
        else:
            # error_message.pyのfeed_date_parse_errorを表示して同じページに留まる
            messages.error(request, get_error_message('date_parse_error'))
            return redirect('reader:add_feed')
        # datetimeオブジェクトに変換して返す
        try:
            return datetime.datetime.fromisoformat(value)
        except ValueError:
            messages.error(request, get_error_message('date_parse_error'))
            return redirect('reader:add_feed')

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
                messages.error(request, get_error_message('not_found_error'))
                return render(request, 'reader/add_feed.html', {'form': form})
            # フィードにエントリがない場合、エラーメッセージを表示して同じページに留まる
            if not feed.entries:
                messages.error(request, get_error_message('entry_not_found_error'))
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
                            messages.error(request, get_error_message('date_parse_error'))
                            return redirect('reader:error_page')
                    # ユーザーの購読をデータベースに保存する
                    Subscription.objects.create(user=request.user, feed=feed)
            except IntegrityError:
                # 既に登録されているフィードの場合、エラーメッセージを表示してエラーページにリダイレクトする
                messages.error(request, get_error_message('already_exists_error'))
                return redirect('reader:error_page')
            # フォームの送信とデータの保存が成功した場合、フィードリストのページにリダイレクトする
            return redirect('reader:feed_list')
        else:
            # フォームのバリデーションが失敗した場合、エラーメッセージを表示してエラーページにリダイレクトする
            messages.error(request, get_error_message('invalid_value_error'))
            return redirect('reader:error_page')
    else:
        # GETリクエストの場合(ページが初めて表示された場合)に、新しい（空の）フォームを作成する
        form = AddFeedForm()
    # フォームをテンプレートに渡してレンダリングする
    return render(request, 'reader/add_feed.html', {'form': form})

# フィードの削除
@login_required
def remove_feed(request, feed_id):
    # ログインしているユーザーがフィードを購読しているかを確認し、登録されたフィードが0件だった場合エラーメッセージを表示する
    if Subscription.objects.filter(user=request.user, feed=feed_id).count() == 0:
        messages.error(request, get_error_message('not_exists_error'))
        return redirect('reader:error_page')
    # フィードを削除するときは、remove_feedのページにリダイレクトし、そのフィードの削除確認をする。
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
    entries = Entry.objects.filter(feed=feed).order_by('pub_date')
    # 最新のエントリーを取得
    entry = entries.last() if entries else None
    return render(request, 'reader/detailed_list.html', {'entries': entries, 'entry': entry, 'feed': feed})


# フィードの更新
@login_required
def update_feed(request, feed_id):
    # POSTリクエストがあった場合、非同期タスクでフィードを更新する。
    # フィードの更新を行うと、そのフィードに関連する記事も更新される。
    if request.method == 'POST':
        from reader.tasks import update_feed as update_feed_task
        update_feed_task.delay(feed_id)
        return redirect('reader:feed_list')
    return render(request, 'reader/update_feed.html', {'feed_id': feed_id})
