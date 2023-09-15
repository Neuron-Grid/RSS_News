from reader import views
from reader.views import feed_list, add_feed
from django.urls import path


app_name = 'reader'
urlpatterns = [
    # 未ログイン時のリダイレクト先
    path('', views.index, name='index'),
    # ログイン後のリダイレクト先
    path('feed_list/', feed_list, name='feed_list'),
    # フィードの追加
    path('add_feed/', add_feed, name='add_feed'),
    # path('add_feed/', add_feed_get, name='add_feed_get'),
    # path('add_feed/', add_feed_post, name='add_feed_post'),
    path('remove_feed/<int:feed_id>/', views.remove_feed, name='remove_feed'),
    path('detailed_list/<int:pk>/', views.detailed_list, name='detailed_list'),
    path('update_feed/<int:feed_id>/', views.update_feed, name='update_feed'),
    # エラーページ
    path('error_page/', views.error_page, name='error_page'),
]