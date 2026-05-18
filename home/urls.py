"""
URL configuration for VZN project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path,include
from . import views

urlpatterns = [
    path("",views.index,name="home"),
    path("News",views.news,name="news"),
    path("List",views.list,name="list"),
    path("Gaming",views.gaming,name="gaming"),
    path("Tech",views.tech,name="tech"),
    path("Anime and Manga",views.animng,name="animng"),
    path("Science",views.science,name="science"),
    path("Comics",views.comic,name="comic"),
    path("Cinema",views.cinema,name="cinema"),
    path("detail/<int:nid>/",views.detail,name="detail"),
    path("Topic",views.topic,name="topic"),
    path("Search",views.search,name="search"),
]
