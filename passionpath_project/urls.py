from django.contrib import admin
from django.urls import path, include
from passionpath_app import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('passionpath_app.urls')),  # Mengarahkan semua URL ke aplikasi passionpath_app
    
]