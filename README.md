# 本プロジェクト概要

サービス名 : `RSS News`

-   RSS リーダー
-   ログイン機能付き
-   web サイトのデザインに[Bootstrap](https://getbootstrap.com/)を使用しています。

## 作成理由
-   今自分が使っているRSSリーダーが異なるOS間で連携が取れないので不便だった
-   クロスプラットフォームで使えるものを作成する必要があった

この２つを考慮し、ブラウザ上で動作するRSSリーダーを作成するのが最適だと考えた為、Djangoで作成しました。


---

## 使用しているパッケージ

-   [Django-Allauth](https://pypi.org/project/django-allauth/)<br>
-   [feedparser](https://pypi.org/project/feedparser/)<br>
-   [django_feedparser](https://pypi.org/project/django-feedparser/)<br>
-   [django-crispy-forms](https://pypi.org/project/django-crispy-forms/)<br>
-   [django-bootstrap5](https://pypi.org/project/django-bootstrap5/)<br>
-   [django-environ](https://pypi.org/project/django-environ/)<br>
-   [django-celery-beat](https://pypi.org/project/django-celery-beat/)<br>
-   [django-celery-results](https://pypi.org/project/django-celery-results/)<br>
-   [python-dotenv](https://pypi.org/project/python-dotenv/)<br>

リンク先は[PyPI](https://pypi.org/)のURLです。

---

## DB 設計

このアプリは、`Feed`、`Entry`、`UserFeed`の 3 つの DB テーブルを使用しています。<br>
ログイン機能は、Django Allauthを利用している為、Userテーブルは無いです。<br>

<details><summary>詳細はこちらに記載しています。</summary>

### Feed モデル

RSS フィードの情報を保存する為のモデルです。以下の属性が定義されています。

-   `url`: フィードの URL。URLField 型で、一意性が強制されます。
-   `title`: フィードのタイトル。CharField 型で、最大長は 100 文字です。
-   `description`: フィードの説明。TextField 型で、空白または null 値が許可されます。

### Entry モデル

フィード内のエントリを表すモデルです。以下の属性が定義されています。

-   `feed`: フィード。ForeignKey 型で、Feed モデルと関連付けられます。
-   `title`: エントリのタイトル。CharField 型で、最大長は 50 文字です。
-   `link`: エントリのリンク。URLField 型です。
-   `summary`: エントリの要約。TextField 型です。
-   `pub_date`: エントリの公開日時。DateTimeField 型です。

### Subscription モデル

ユーザーが購読しているフィードを表すモデルです。以下の属性が定義されています。

-   `user`: ユーザー。ForeignKey 型で、django.contrib.auth.models.User モデルと関連付けられます。
-   `feed`: フィード。ForeignKey 型で、Feed モデルと関連付けられます。
</details>

---

<details><summary>今後修正する問題</summary>

-   フィードが自動更新されない(動作未検証)
-   detailed_list.htmlの更新ボタンが機能しない
-   settings.pyとdocker-compose.ymlに書かれている DB の設定を環境変数に変更する
-   アカウントの削除機能を追加する
-   アカウントの削除ページを作成する
-   デザインを統一する
-   アカウントの管理ページを作成する
</details>

<details><summary>解決中の問題</summary>

-   フィードの更新に関する問題を最優先で解決します
</details>

---

## 使い方

### 1. リポジトリをクローンする

```Shell
git clone https://github.com/Neuron-Grid/RSS_News.git
```
### 2. 必要なパッケージをインストールする
```Shell
pip install celery django-allauth feedparser django-crispy-forms \
django-celery-results django_feedparser redis django django-celery-beat \
django-redis django-bootstrap5 mysqlclient django-environ python-dotenv
```
### パッケージが古い場合は更新してください
```Shell
pip list --outdated | tail -n +3 | awk '{print $1}' | xargs pip install -U 
```

### 3. local.env を作成し、環境変数を設定する
```Shell
touch local.env
```

### local.envの設定例です。
```local.env
#メールの設定
EMAIL_HOST=smtp.googlemail.com
EMAIL_PORT=587
EMAIL_HOST_USER=google_account@gmail.com
EMAIL_HOST_PASSWORD=アプリパスワード

#settings.py
SECRET_KEY=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
DEBUG=False
```

### 4. 実行する

```Shell
docker-compose up -d && \
sleep 5; python manage.py makemigrations && \
python manage.py migrate && \
python manage.py runserver
```
