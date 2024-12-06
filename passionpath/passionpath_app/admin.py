from django.contrib import admin
from .models import Absensi
from .models import Students 
from .models import Contact
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
            return format_html('<img src="{}" width="50" height="50" />'.format(obj.foto_profil.url))
        return "No image"
    foto_profil.short_description = 'Foto Profil'

