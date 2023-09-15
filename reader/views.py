from django.contrib.auth.decorators import login_required
from reader.helper import ERROR_MESSAGES, DATE_FORMAT, DATE_FORMAT_STR
from reader.models import Feed, Subscription, Entry
from django.db import IntegrityError, transaction
from reader.tasks import update_all_feeds_task
from django.shortcuts import render, redirect
from reader.forms import AddFeedForm
from django.contrib import messages
import feedparser
import datetime
import re

# エラーメッセージ
def get_error_message(error_code):
    error_message = ERROR_MESSAGES.get(error_code, '予期せぬエラーが発生しました。\n 操作の詳細を管理者に報告してください。')
    return error_message

def add_error_message(request, error_key):
    messages.error(request, get_error_message(error_key))

# エラーハンドリングを一元化するプライベート関数
def handle_error(request, form=None, error_key=None):
    # エラーメッセージを追加し、適切なページにリダイレクトする
    add_error_message(request, error_key)
    if form:
        return render(request, 'reader/add_feed.html', {'form': form})
    return redirect('reader:error_page')

# フィード情報をデータベースに保存するプライベート関数
def save_feed(feed_url, feed_title, feed_description):
    return Feed.objects.create(
        url=feed_url,
        title=feed_title,
        description=feed_description,
    )

# エントリ情報をデータベースに保存するプライベート関数
def save_entries(entries, feed, request):
    for entry in entries:
        try:
            Entry.objects.create(
                feed=feed,
                title=entry.get('title', ''),
                link=entry.get('link', ''),
                summary=entry.get('summary', ''),
                pub_date=custom_parse_datetime(request, entry.get('published', '')),
            )
        except ValueError:
            # 日付のパースに失敗した場合、IntegrityErrorを送出する
            raise IntegrityError(get_error_message('date_parse_error'))

def custom_parse_datetime(date_str):
    for pattern, date_format in DATE_FORMAT_STR.items():
        if re.match(pattern, date_str):
            try:
                return datetime.datetime.strptime(date_str, date_format)
            except ValueError:
                raise ValueError(get_error_message('date_format_error'))
    raise ValueError(get_error_message('date_format_error'))

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
    if request.method == 'POST':
        return get_feed_list(request)
    else:
        return post_feed_list(request)

def get_feed_list(request):
    feeds = Feed.objects.filter(subscription__user=request.user)
    return render(request, 'reader/feed_list.html', {'feeds': feeds})

def post_feed_list(request):
    update_all_feeds_task.delay(
        user_id=request.user.id
    )
    return redirect('reader/feed_list.html')

# 文字列値をdatetimeオブジェクトに変換する。
# この関数は、フィードのパースに失敗した場合に発生するエラーを回避するために使用する。
# 日付のフォーマットを年月日時分に可能な限り統一する
def custom_parse_datetime(value, request):
    # 既にdatetimeオブジェクトが渡されている場合は日付のフォーマットを年月日時分か確認する
    if isinstance(value, datetime.datetime):
        # datetimeオブジェクトに変換して返す
        return value
    # valueがNoneの場合はNoneを返す
    if value is None:
        return None
    # valueがstr型の場合
    if isinstance(value, str):
        # 日付のフォーマットを調整する
        for pattern in [
            DATE_FORMAT,
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
            return redirect('reader/add_feed')

# フィードの追加
@login_required
def add_feed(request):
    if request.method == 'POST':
        return add_feed_post(request)
    else:
        return add_feed_get(request)

def add_feed_get(request):
    # 新しい（空の）フォームを作成する
    try:
        form = AddFeedForm()
    except Exception as e:
        messages.error(request, str(e))
        return redirect('reader:error_page')
    # フォームをテンプレートに渡してレンダリングする
    return render(request, 'reader/add_feed.html', {'form': form})

def add_feed_post(request):
    form = AddFeedForm(request.POST)
    if form.is_valid():
        # フォームからフィードのURLとタイトルを取得する
        feed_url = form.cleaned_data['url']
        feed_title = form.cleaned_data['feed_name']
        # フィードをパースする
        feed = feedparser.parse(feed_url)
        # フィードが存在しない場合、not_found_errorを呼び出す
        if not feed:
            return handle_error(request, form, 'not_found_error')
        # フィードにエントリがない場合、entry_not_found_errorを呼び出す
        if not feed.entries:
            return handle_error(request, form, 'entry_not_found_error')
        # フィードの説明とエントリを取得する
        feed_description = feed.get('feed', {}).get('description')
        entries = list(feed.entries)
        # アトミックブロック内でフィードとエントリを保存する
        try:
            with transaction.atomic():
                feed_obj = save_feed(feed_url, feed_title, feed_description)
                save_entries(entries, feed_obj, request)
        # 既に登録されているフィードの場合、already_exists_errorを呼び出す
        except IntegrityError:
            return handle_error(request, None, 'already_exists_error')
        # ユーザーの購読をデータベースに保存する
        Subscription.objects.create(user=request.user, feed=feed_obj)
        # 成功時にフィードリストへリダイレクトする
        return redirect('reader:feed_list')
    else:
        # フォームのバリデーションが失敗した場合、invalid_value_errorを呼び出す
        print(form.errors)
        return handle_error(request, form, 'invalid_value_error')

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
        update_feed.delay(feed_id)
        return redirect('reader:feed_list')
    return render(request, 'reader/update_feed.html', {'feed_id': feed_id})