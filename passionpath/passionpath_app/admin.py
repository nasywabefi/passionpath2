from django.contrib import admin
from .models import Absensi

# Register your models here.
@admin.register(Absensi)
class AbsensiAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'points')