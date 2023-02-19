from django.urls import path
from . import views

app_name = 'reader'
urlpatterns = [
    path('', views.index, name='index'),
    path('feed_list/', views.feed_list, name='feed_list'),
    path('add_feed/', views.add_feed, name='add_feed'),
    path('remove_feed/', views.remove_feed, name='remove_feed'),
    path('duplicate_error/', views.duplicate_error, name='duplicate_error'),
    path('feed_list/remove/<int:feed_id>/', views.remove_feed, name='remove_feed'),
    path('detailed_list/<int:pk>/', views.DetailedListView.as_view(), name='detailed_list'),
]