from traceback import format_tb
from django.utils.html import format_html
from django.contrib import admin
from .models import Absensi
from .models import Students 
from .models import Contact, ProfileAdmin , Kelas , Episode
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
    list_display = ('id_kelas', 'nama_kelas', 'deskripsi', 'total_modul') 
    list_filter = ('total_modul',)  
    search_fields = ('nama_kelas', 'deskripsi')  

admin.site.register(Kelas, KelasAdmin)

class EpisodeAdmin(admin.ModelAdmin):
    list_display = ('id', 'judul_episode', 'id_kelas', 'deskripsi_episode', 'upload_video', 'link_video')
    list_filter = ('id_kelas',)
    search_fields = ('judul_episode', 'deskripsi_episode', 'id_kelas__nama_kelas')
    ordering = ('id',)

admin.site.register(Episode, EpisodeAdmin)