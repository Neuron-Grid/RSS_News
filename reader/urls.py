from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('add_feed/', views.add_feed, name='add_feed'),
]
