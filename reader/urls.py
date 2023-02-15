from django.urls import path
from . import views

app_name = 'reader'
urlpatterns = [
    path('', views.index, name='index'),
    path('feed_list/', views.feed_list, name='feed_list'),
    path('add_feed/', views.add_feed, name='add_feed'),
    path('remove_feed/', views.delete_feed, name='remove_feed'),
    # path('update_feed/<int:feed_id>/', views.update_feed, name='update_feed'),
    # path('delete_feed/<int:feed_id>/', views.delete_feed, name='delete_feed'),
]
