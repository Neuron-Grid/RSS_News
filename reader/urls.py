from django.urls import path
from . import views

app_name = 'reader'
urlpatterns = [
    # 未ログイン時のリダイレクト先
    path('', views.index, name='index'),
    # ログイン後のリダイレクト先
    path('feed_list/', views.feed_list, name='feed_list'),
    path('add_feed/', views.add_feed, name='add_feed'),
    path('remove_feed/<int:feed_id>/', views.remove_feed, name='remove_feed'),
    path('detailed_list/<int:pk>/', views.detailed_list, name='detailed_list'),
    path('update_feed/<int:feed_id>/', views.update_feed, name='update_feed'),
    # エラーページ
    path('error_page/', views.update_feed, name='error'),
]