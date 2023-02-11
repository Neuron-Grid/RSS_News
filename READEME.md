# 本プロジェクト概要
サービス名 : RSS News
ログイン機能は、Django Allauthで作成
- RSSリーダー
- djangoで作成中
- ログイン機能つき
- シンプルで使いやすい(多分)
- ユーザーの追跡はしない(予定)
- 無料で利用できる

## 作成理由
- 今自分が使っているRSSリーダーが不便だった為、自作しようと思った
- クロスプラットフォームで使えるものを作成する必要があった

上記の2つを考慮し、ブラウザ上で動作するRSSリーダーを作成する

***
## DB設計
このアプリは、Feed、Entry、UserFeedの3つのDBテーブルを使用しています。
詳細は下記に記載しています。

### Feedモデル
RSSフィードの情報を保存するためのモデルです。以下の属性が定義されています：
- `url`: フィードのURL。URLField型で、一意性が強制されます。
- `title`: フィードのタイトル。CharField型で、最大長は50文字です。
- `description`: フィードの説明。TextField型で、空白またはnull値が許可されます。

### Entryモデル
フィード内のエントリを表すモデルです。以下の属性が定義されています：
- `feed`: フィード。ForeignKey型で、Feedモデルと関連付けられます。
- `title`: エントリのタイトル。CharField型で、最大長は50文字です。
- `link`: エントリのリンク。URLField型です。
- `summary`: エントリの要約。TextField型です。
- `pub_date`: エントリの公開日時。DateTimeField型です。

### Subscriptionモデル
ユーザーが購読しているフィードを表すモデルです。以下の属性が定義されています：
- `user`: ユーザー。ForeignKey型で、django.contrib.auth.models.Userモデルと関連付けられます。
- `feed`: フィード。ForeignKey型で、Feedモデルと関連付けられます。

***

- 現時点で、使用しているパッケージ<br>
    [Allauth](https://pypi.org/project/django-allauth/)<br>
    [django_bootstrap5](https://pypi.org/project/django-bootstrap5/)<br>
    [feedparser](https://pypi.org/project/feedparser/)<br>