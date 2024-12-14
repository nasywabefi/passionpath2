from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static


urlpatterns = [
    # redirect profile 
    path('profile/', views.profile_redirect, name='profile_redirect'),
    # redirect logout
    path("logout/", views.user_logout, name='logout'),  
    # redirect dashboard admin/siswa
    path('dashboard/', views.dashboard, name='dashboard'), 
    # update deskripsi kelas
    path('kelas/<int:id_kelas>/edit/', views.update_kelas, name='update_kelas'),
    # input episode kelas
    path('kelas/<int:id_kelas>/add_episode/', views.add_episode, name='add_episode'), 
    path('program/<int:id_kelas>/add_episode/', views.program_input, name='add_episode'),
    path('program/<int:id_kelas>/edit_episode/<int:id_episode>/', views.edit_episode, name='edit_episode'),
    path('program/<int:id_kelas>/delete_episode/<int:id_episode>/', views.delete_episode, name='delete_episode'),

    # homepage
    path('', views.index, name='index'),                    
    path('about/', views.about, name='about'),              
    path('product/', views.product, name='product'),        
    path('contact/', views.contact, name='contact'),        
 
    # Login Register
    path('login/', views.user_login, name='login'), 
    path('register/', views.register, name='register'),     

    # Course HomePage
    path('courses/', views.courses, name='courses'),
    path('accounting/', views.accounting, name='accounting'),
    path('bussines/<int:id_kelas>/', views.bussines, name='bussines'), 
    path('development/<int:id_kelas>/', views.development, name='development'),

    path('laporan_admin/', views.laporan_admin, name='laporan_admin'),
    path('design/', views.design, name='design'),
    path('language/', views.language, name='language'),


    # dashboard siswa
    path('checkout/<int:kelas_id>/', views.checkout, name='checkout'),
    path('pembayaran/<int:kelas_id>/', views.pembayaran, name='pembayaran'),
    path('detail_pembayaran/<int:pembayaran_id>/', views.detail_pembayaran, name='detail_pembayaran'),
    path("dashboard_siswa/", views.dashboard_siswa, name='dashboard_siswa'),
    path("program_input/", views.program_input, name='program_input'),
    path("profile_siswa/", views.profile_siswa, name='profile_siswa'),
    path("belajar/", views.belajar, name='belajar'),
    path("riwayat_bayar/", views.riwayat_bayar, name='riwayat_bayar'),
    path("pengaturan_siswa/", views.pengaturan_siswa, name='pengaturan_siswa'),
    path('course_siswa/<int:kelas_id>/', views.course_siswa, name='course_siswa'),

    # admin
    path("program/<int:id_kelas>/detail/", views.program_input, name='program_input'),
    path("programs/<int:id_kelas>/", views.program_detail, name='program_detail'),
    path("program_interaktif/", views.program_interaktif, name='program_interaktif'),
    path("program_admin/", views.program_admin, name='program_admin'),
    path('profile_admin/', views.pengaturan_admin, name='pengaturan_admin'),
    path('dashboard_admin/', views.dashboard_admin, name='dashboard_admin'), 
    path('pembayaran_admin/', views.pembayaran_admin, name='pembayaran_admin'),

    # Menambahkan endpoint absensi
    path('absen/', views.absen, name='absen'), 
]

if settings.DEBUG:  
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)