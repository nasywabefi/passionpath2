from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [


    path('', views.index, name='index'),                    
    path('about/', views.about, name='about'),              
    path('product/', views.product, name='product'),        
    path('contact/', views.contact, name='contact'),        
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'), 
    path('dashboard/', views.dashboard, name='dashboard'), 
    path('login/', views.user_login, name='login'), 
    path('dashboard_siswa/', views.dashboard_siswa, name='dashboard_siswa'),            
    path('register/', views.register, name='register'),     
    path('accounting/', views.accounting, name='accounting'),
    path('bussines/', views.bussines, name='bussines'),
    path('design/', views.design, name='design'),
    path('development/', views.development, name='development'),
    path('language/', views.language, name='language'),
    path('profile/', views.profile_siswa, name='profile_siswa'),
    path('pengaturan/', views.pengaturan, name='pengaturan'),
    path('course_siswa/', views.course_siswa, name='course_siswa'),
     path('belajar/', views.belajar, name='belajar'),

    path("logout/", views.user_logout, name='logout'),
    path("pembayaran/", views.pembayaran, name='pembayaran'),
    path("detail_pembayaran/", views.detail_pembayaran, name='detail_pembayaran'),
    path("program_input/", views.program_input, name='program_input'),

    # admin
    path("video_interaktif/", views.video_iteraktif, name='video_interaktif'),
    path('pengaturan_admin/', views.pengaturan_admin, name='pengaturan_admin'),
    path('pembayaran_admin/', views.pembayaran_admin, name='pembayaran_admin'),


    path('absen/', views.absen, name='absen'),  # Menambahkan endpoint absensi
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)