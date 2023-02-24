from django.urls import path
from . import views

app_name = 'reader'
urlpatterns = [
    # 未ログイン時のリダイレクト先
    path('', views.index, name='index'),
    path('site_manager/', views.site_manager, name='site_manager'),
    # ログイン後のリダイレクト先
    path('feed_list/', views.feed_list, name='feed_list'),
    path('add_feed/', views.add_feed, name='add_feed'),
    path('remove_feed/<int:feed_id>/', views.remove_feed, name='remove_feed'),
    path('duplicate_error/', views.duplicate_error, name='duplicate_error'),
    path('feed_list/remove/<int:feed_id>/', views.remove_feed, name='remove_feed'),
    path('detailed_list/<int:pk>/', views.detailed_list, name='detailed_list'),
]