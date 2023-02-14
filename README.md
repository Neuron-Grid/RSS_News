# 本プロジェクト概要
サービス名 : RSS News<br>
- RSSリーダー
- djangoで作成中
- ログイン機能つき
- シンプルで使いやすい(多分)
- ユーザーの追跡はしない(予定)
- 無料で利用できる

## 作成理由
- 今自分が使っているRSSリーダーが不便だった
- クロスプラットフォームで使えるものを作成する必要があった

上記の2つを考慮した場合、ブラウザ上で動作するRSSリーダーを作成するのが最適だと考えたため、本プロジェクトを作成することにしました。

***
## DB設計
このアプリは、Feed、Entry、UserFeedの3つのDBテーブルを使用しています。<br>
ログイン機能は、Django Allauthで作成している為、Userテーブルは使用していません。<br>
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

<details><summary>使用しているパッケージ</summary>

[Allauth](https://pypi.org/project/django-allauth/)<br>
[feedparser](https://pypi.org/project/feedparser/)<br>
[django-crispy-forms](https://pypi.org/project/django-crispy-forms/)<br>
[django-bootstrap5](https://pypi.org/project/django-bootstrap5/)<br>

リンク先は[PyPI](https://pypi.org/)のURLとなっています。
</details>

***

<details><summary>現在確認されている問題</summary>

- フィードが更新されない
- アカウントの削除ができない
- ログイン後にエラーが発生する
```
コンソールには以下のようなエラーが表示される
GET /feed_list/ HTTP/1.1" 500 176778
```
```
ブラウザでは以下のようなエラーが表示される
NoReverseMatch at /feed_list/
'reader' is not a registered namespace
```
</details>

<details><summary>今後追加する機能</summary>

> フィードを更新するボタンを追加する<br>
> > Feed_list.htmlにボタンを追加する<br>

> アカウントの削除機能を追加する<br>
> アカウントを削除するページを作成する<br>
</details>


<details><summary>現在解決中の問題</summary>

- フィードの更新されない
</details>