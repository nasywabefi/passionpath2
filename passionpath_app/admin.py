from traceback import format_tb
from django.utils.html import format_html
from django.contrib import admin
from .models import Absensi
from .models import Students 
from .models import Contact, ProfileAdmin , Kelas , Episode , Pembayaran
# Register your models here.
@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'points')


@admin.register(Contact)
class ContactAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'date_sent', 'message') 
    search_fields = ('name', 'email', 'message')  
    list_filter = ('date_sent',)  
    ordering = ('-date_sent',)  

@admin.register(Students)
class StudentsAdmin(admin.ModelAdmin):
    list_display = ('id_siswa', 'username', 'name', 'email', 'phone', 'name_ortu', 'phone_ortu', 'school', 'date', 'address', 'foto_profil')  # Kolom yang ditampilkan di halaman admin
    
    # Fungsi untuk menampilkan gambar profil di halaman daftar admin
    def foto_profil(self, obj):
        if obj.foto_profil:
            return format_tb('<img src="{}" width="50" height="50" />'.format(obj.foto_profil.url))
        return "No image"
    foto_profil.short_description = 'Foto Profil'


# ProfileAdmin untuk menyesuaikan tampilan model di admin
class ProfileAdminAdmin(admin.ModelAdmin):
    # Menambahkan kolom-kolom yang ingin ditampilkan di halaman admin
    list_display = ('id_admin', 'username_display', 'first_name_display', 'email_display', 'phone', 'date_of_birth', 'address', 'foto_profil_display')
    list_filter = ('date_of_birth',)  # Filter berdasarkan tanggal lahir
    search_fields = ('id_admin', 'username__username', 'username__first_name', 'username__email', 'phone')  # Pencarian data

    # Menampilkan Username
    def username_display(self, obj):
        return obj.username.username
    username_display.short_description = 'Username'

    # Menampilkan Nama
    def first_name_display(self, obj):
        return obj.username.first_name
    first_name_display.short_description = 'Nama'

    # Menampilkan Email
    def email_display(self, obj):
        return obj.username.email
    email_display.short_description = 'Email'

    # Menampilkan Foto Profil
    def foto_profil_display(self, obj):
        if obj.foto_profil:
            return format_html('<img src="{}" width="50" height="50" style="border-radius: 5px;" />', obj.foto_profil.url)
        return "No Image"
    foto_profil_display.short_description = 'Foto Profil'

# Daftarkan Profile_Admin di admin site
admin.site.register(ProfileAdmin, ProfileAdminAdmin)


class KelasAdmin(admin.ModelAdmin):
    list_display = ('id_kelas', 'nama_kelas', 'deskripsi', 'total_modul' ,'harga') 
    list_filter = ('total_modul',)  
    search_fields = ('nama_kelas', 'deskripsi')  

admin.site.register(Kelas, KelasAdmin)

class EpisodeAdmin(admin.ModelAdmin):
    # Menampilkan field di daftar admin
    list_display = ('id', 'judul_episode', 'id_kelas', 'deskripsi_episode', 'is_free', 'upload_video', 'link_video')
    # Tambahkan filter untuk field 'id_kelas' dan 'is_free'
    list_filter = ('id_kelas', 'is_free')
    # Tambahkan kemampuan pencarian berdasarkan judul, deskripsi, dan nama kelas
    search_fields = ('judul_episode', 'deskripsi_episode', 'id_kelas__nama_kelas')
    # Urutkan daftar berdasarkan ID episode
    ordering = ('id',)

# Daftarkan model dan konfigurasinya ke admin site
admin.site.register(Episode, EpisodeAdmin)

@admin.register(Pembayaran)
class PembayaranAdmin(admin.ModelAdmin):
    list_display = (
        'id',  # ID unik untuk setiap pembayaran
        'user',  # Pengguna yang melakukan pembayaran
        'kelas',  # Kelas yang dibayar
        'status_pembayaran',  # Status pembayaran (pending, success, ditolak)
        'nama_pengirim',  # Nama pengirim pembayaran
        'metode_pembayaran',  # Metode pembayaran
        'nomor_rekening_dan_nama',  # Rekening dan nama pengirim
        'total_harga',  # Total harga pembayaran
        'bukti_pembayaran',  # Bukti pembayaran (image)
        'kode_pembayaran',  # Kode pembayaran
        'tanggal_pembayaran',  # Tanggal pembayaran
        'tanggal_approve_tolak',  # Tanggal persetujuan atau penolakan
    )
    list_filter = ('status_pembayaran', 'tanggal_pembayaran', 'tanggal_approve_tolak')  
    search_fields = ('kode_pembayaran', 'user__username', 'kelas__nama_kelas')  
    readonly_fields = ('kode_pembayaran', 'tanggal_pembayaran') 

