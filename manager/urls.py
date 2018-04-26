from django.urls import re_path
from . import views
urlpatterns = [
    re_path(r'^$', views.home, name='home'),
    re_path(r'^setdatabase/$', views.set_database, name='set_database'),
    re_path(r'^table/$', views.table, name='table'),
    re_path(r'^view/$', views.view, name='view'),
    re_path(r'query/$', views.query_execute, name='query'),

]