from django.contrib import admin
from django.urls import include, path
from passionpath_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('about/',views.about )
]
