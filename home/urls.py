from django.contrib import admin
from django.urls import path
from home import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index, name='index'),
    path('list/', views.get_list, name='list'),
    path('names/', views.store_videos, name='names'),
    path('search/', views.search, name='search'),
    path('title/', views.get_by_title_description, name='title'),
    
]