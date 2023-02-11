from django.urls import path
from . import views

# views.pyとtemplatesフォルダを参照して、URLとビューを紐づける
# remove_feed.htmlは、フィードの削除時に表示する
# feed_list.htmlログイン後に、フィード一覧を表示する
# delete_feed_error.htmlは、フィードの削除時に、購読しているフィードが一件もない場合に表示する
# add_feed.htmlは、フィードの追加時に表示
app_name = 'reader'
urlpatterns = [
    path('', views.index, name='index'),
    path('add_feed/', views.add_feed, name='add_feed'),
    path('update_feed/<int:feed_id>/', views.update_feed, name='update_feed'),
    path('delete_feed/<int:feed_id>/', views.delete_feed, name='delete_feed'),
]
