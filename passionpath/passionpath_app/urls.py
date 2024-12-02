from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),                    
    path('about/', views.about, name='about'),              
    path('product/', views.product, name='product'),        
    path('contact/', views.contact, name='contact'),        
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'), 
    path('login/', views.user_login, name='login'), 
    path('dashboard_siswa/', views.dashboard_siswa, name='dashboard_siswa'),            
    path('register/', views.register, name='register'),     
    path('accounting/', views.accounting, name='accounting'),
    path('bussines/', views.bussines, name='bussines'),
    path('design/', views.design, name='design'),
    path('development/', views.development, name='development'),
    path('language/', views.language, name='language'),
    path('profile/', views.profile_siswa, name='profile_siswa'),

    path("logout/", views.user_logout, name='logout'),

    path('absen/', views.absen, name='absen'),  # Menambahkan endpoint absensi
]