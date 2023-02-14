# -*- encoding: utf-8 -*-
"""
Copyright (c) 2019 - present AppSeed.us
"""
from django.urls import path, re_path
from apps.home import views


urlpatterns = [
    # The home page
    path('', views.index, name='home'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('dashboard/', views.dashboard, name='dashboard'),
    path('channels/', views.channels, name='channels'),
    path('channel-group/', views.channel_group, name='channels'),
    path('outputs/', views.outputs, name='outputs'),
    path('settings/', views.settings, name='settings'),

    path('channels-list/', views.ItemListView.as_view()),
    path('data/', views.data, name="video_feed"),
    path('video_feed/', views.stream, name="video_feed"),

    # Matches any html file
    re_path(r'^.*\.html', views.pages, name='pages'),

]
