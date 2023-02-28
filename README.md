# 本プロジェクト概要
サービス名 : `RSS News`
- RSSリーダー
- djangoで作成中
- ログイン機能つき
- webサイトのデザインには、[Bootstrap](https://getbootstrap.com/)を使用しています。
- 無料で利用できる

## 作成理由
- 今自分が使っているRSSリーダーが不便だった
- クロスプラットフォームで使えるものを作成する必要があった

上記の2つを考慮した場合、ブラウザ上で動作するRSSリーダーを作成するのが最適だと考えたため、本プロジェクトを作成することにしました。

***
## DB設計
このアプリは、`Feed`、`Entry`、`UserFeed`の3つのDBテーブルを使用しています。<br>
ログイン機能は、Django Allauthで作成している為、Userテーブルは使用していません。<br>
<details><summary>詳細はこちらに記載しています。</summary>

### Feedモデル
RSSフィードの情報を保存する為のモデルです。以下の属性が定義されています。
- `url`: フィードのURL。URLField型で、一意性が強制されます。
- `title`: フィードのタイトル。CharField型で、最大長は100文字です。
- `description`: フィードの説明。TextField型で、空白またはnull値が許可されます。

### Entryモデル
フィード内のエントリを表すモデルです。以下の属性が定義されています。
- `feed`: フィード。ForeignKey型で、Feedモデルと関連付けられます。
- `title`: エントリのタイトル。CharField型で、最大長は50文字です。
- `link`: エントリのリンク。URLField型です。
- `summary`: エントリの要約。TextField型です。
- `pub_date`: エントリの公開日時。DateTimeField型です。

### Subscriptionモデル
ユーザーが購読しているフィードを表すモデルです。以下の属性が定義されています。
- `user`: ユーザー。ForeignKey型で、django.contrib.auth.models.Userモデルと関連付けられます。
- `feed`: フィード。ForeignKey型で、Feedモデルと関連付けられます。
</details>

***

<details><summary>使用しているパッケージ</summary>

- [Django-Allauth](https://pypi.org/project/django-allauth/)<br>
- [feedparser](https://pypi.org/project/feedparser/)<br>
- [django_feedparser](https://pypi.org/project/django-feedparser/)<br>
- [django-crispy-forms](https://pypi.org/project/django-crispy-forms/)<br>
- [django-bootstrap5](https://pypi.org/project/django-bootstrap5/)<br>
- [django-environ](https://pypi.org/project/django-environ/)<br>
- [django-celery-beat](https://pypi.org/project/django-celery-beat/)<br>
- [django-celery-results](https://pypi.org/project/django-celery-results/)<br>

リンク先は[PyPI](https://pypi.org/)のURLとなっています。
</details>

***

<details><summary>今後修正する問題</summary>

- フィードが更新されない
- settings.pyとdocker-compose.ymlに書かれているDBの設定を環境変数に変更する
- アカウントの削除機能を追加する
- アカウントを削除するページを作成する
- webサイトのデザインを統一する
- アカウントの管理ページを作成する
</details>

<details><summary>現在解決中の問題</summary>

- フィードの更新に関する問題を最優先で解決します
- その後、アカウントの削除や管理するページを作成します
</details>

***

## ローカル環境での実行方法
### 1. リポジトリをクローンする

``` Shell
git clone https://github.com/Neuron-Grid/RSS_News && \
pip install celery django-allauth feedparser django-crispy-forms \
django-celery-results django_feedparser redis django django-celery-beat \
django-redis django-bootstrap5 mysqlclient django-environ && \
pip list --outdated | tail -n +3 | awk '{print $1}' | xargs pip install -U && \
cd RSS_News
```
### 2. local.envを作成し、データベースやメールの環境変数を設定する
``` Shell
touch local.env
```
### 3. 実行する
``` Shell
docker-compose up -d && \
sleep 7; python manage.py makemigrations && \
python manage.py migrate && \
python manage.py runserver
```