from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                    # Halaman utama
    path('about/', views.about, name='about'),              # Halaman about
    path('product/', views.product, name='product'),        # Halaman product
    path('contact/', views.contact, name='contact'),        # Halaman contact
    path('dashboard/', views.dashboard, name='dashboard'),  # Halaman dashboard
    path('login/', views.login, name='login'),              # Halaman login
    path('register/', views.register, name='register'),     # Halaman register

]