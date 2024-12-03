from urllib import request
from django.contrib.auth import authenticate, login as auth_login , logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate
from django.db import models
from django.db.models import Sum

from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Absensi
import json
from datetime import datetime

# View untuk halaman utama (index)
def index(request):
    return render(request, 'index.html')
# View untuk halaman about
def about(request):
    return render(request, 'view/about.html')
# View untuk halaman product
def product(request):
    return render(request, 'view/product.html')
# View untuk halaman contact
def contact(request):
    return render(request, 'view/contact.html')
# View untuk halaman dashboard
def dashboard(request):
    return render(request, 'view/dashboard.html')
def dashboard_siswa(request):
    return render(request, 'view/dashboard_siswa/dashboard_siswa.html')
# View untuk halaman login
def login(request):
    return render(request, 'view/login.html')
# View untuk halaman contact
def register(request):
    return render(request, 'view/register.html')
def accounting(request):
    return render(request, 'view/courses/accounting.html')
def bussines(request):
    return render(request, 'view/courses/bussines.html')
def design(request):
    return render(request, 'view/courses/design.html')
def development(request):
    return render(request, 'view/courses/development.html')
def language(request):
    return render(request, 'view/courses/language.html')

# dashboard siswa
def profile_siswa(request):
    return render(request, 'view/dashboard_siswa/profile_siswa.html')
def pengaturan(request):
    return render(request, 'view/dashboard_siswa/pengaturan.html')

# Absesnsi
@csrf_exempt
@login_required
def absen(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        user = request.user
        day = data.get('day')
        points = data.get('points')
        
        # Pastikan user belum absen hari ini
        if not Absensi.objects.filter(user=user, date=datetime.today().date()).exists():
            # Simpan absensi dan poin
            absensi = Absensi(user=user, points=points, date=datetime.today().date())
            absensi.save()
            
            # Ambil total poin terbaru
            total_points = Absensi.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0
            
            return JsonResponse({'success': True, 'total_points': total_points})
        else:
            return JsonResponse({'success': False, 'message': 'Sudah absen hari ini'})

# register
def register(request):

    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/')) 

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

      
        if not first_name or not last_name or not email or not password:
            messages.error(request, 'Semua bidang wajib diisi.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email sudah terdaftar.')
            return redirect('register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username sudah digunakan.')
            return redirect('register')
        
         # Validasi username harus mengandung angka
        if not any(char.isdigit() for char in username):
            messages.error(request, 'Username harus mengandung angka.')
            return redirect('register')

        # Validasi password minimal 8 karakter
        if len(password) < 8:
            messages.error(request, 'Password harus terdiri dari minimal 8 karakter.')
            return redirect('register')

        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        user.save()

        messages.success(request, 'Registrasi berhasil! Silakan login.')
        return redirect('register')  

    return render(request, 'view/register.html')

# login
def user_login(request):
   
    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/')) 

   
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        next_url = request.GET.get('next')  
        
        # Autentikasi pengguna
        user = authenticate(request, username=username, password=password)
        
        if user is not None:
            auth_login(request, user)  
            if user.is_superuser:
                return redirect('dashboard_admin')  
            else:  
                return redirect(next_url if next_url else 'index')
        else:
            messages.error(request, 'Username atau Password Anda Salah!!!')  
            return redirect('login')  
        
    return render(request, 'view/login.html')

# logout
def user_logout(request):
    logout(request)
    return redirect('index')


# dahsboard siswa/pengguna

@login_required
def dashboard_siswa(request):
    if request.user.is_superuser:
        return redirect('dashboard_admin')

    # Tentukan hari-hari dalam seminggu dengan nama lengkap dalam bahasa Indonesia
    days = [
        {"name": "S", "day": "Monday"},    # Senin
        {"name": "S", "day": "Tuesday"},  # Selasa
        {"name": "R", "day": "Wednesday"},  # Rabu
        {"name": "K", "day": "Thursday"},  # Kamis
        {"name": "J", "day": "Friday"},    # Jumat
        {"name": "S", "day": "Saturday"},  # Sabtu
        {"name": "M", "day": "Sunday"},   # Minggu
    ]

    # Ambil hari ini
    today_name = datetime.today().strftime("%A")

    # Cek apakah user sudah absen hari ini
    user = request.user
    total_points = Absensi.objects.filter(user=user).aggregate(total=Sum('points'))['total'] or 0

    # Cek apakah user sudah absen hari ini
    attendance_today = Absensi.objects.filter(user=user, date=datetime.today().date()).first()
    if attendance_today:
        absen_status = "Sudah absen"
    else:
        absen_status = "Belum absen"

    return render(request, 'view/dashboard_siswa/dashboard_siswa.html', {
        'days': days,
        'today_name': today_name,
        'total_points': total_points,
        'absen_status': absen_status,
    })


@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'view/dashboard_admin.html', {'user': request.user})
    else:
        return render(request, 'view/dashboard_siswa/dashboard_siswa.html', {'user': request.user})
    
# dashboard admin
@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('dashboard_siswa') 
    return render(request, 'view/dashboard_admin/dashboard_admin.html')