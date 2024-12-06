from urllib import request
from django.contrib.auth import authenticate, login as auth_login , logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.utils.timezone import localdate
from django.db import models
from django.db.models import Sum
import requests
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from .models import Absensi
import json
from datetime import datetime
from .models import Students
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import check_password

from .models import Contact
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone



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
    if request.method == "POST":
        name = request.POST.get("name")
        email = request.POST.get("email")
        message = request.POST.get("message")
        recaptcha_response = request.POST.get("g-recaptcha-response")
        
        # Verifikasi reCAPTCHA
        data = {
            'secret': settings.RECAPTCHA_PRIVATE_KEY, 
            'response': recaptcha_response,
        }
        
        # Kirim permintaan POST ke Google untuk verifikasi
        verification_response = requests.post('https://www.google.com/recaptcha/api/siteverify', data=data)
        result = verification_response.json()
        
        if not result.get('success'):
            messages.error(request, "Harap verifikasi bahwa Anda bukan robot.",extra_tags='warning')
            return redirect('contact') 
        
       
        contact = Contact.objects.create(name=name, email=email, message=message)

        # Kirim email ke admin atau email tujuan
        send_mail(
            subject=f"New Contact Message from {name}",
            message=message,
            from_email=email,
            recipient_list=[settings.CONTACT_EMAIL],  
            fail_silently=False,
        )

        # Tampilkan pesan sukses
        messages.success(request, "Terima Kasih Pesan Anda Sudah DiTerima.",extra_tags='success')
        return redirect('contact')  

    return render(request, 'view/contact.html', {
        'RECAPTCHA_PUBLIC_KEY': settings.RECAPTCHA_PUBLIC_KEY,
    })



# View untuk halaman login
def login(request):
    return render(request, 'view/login.html')
# course
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

def pembayaran(request):
    return render(request, 'view/dashboard_siswa/pembayaran.html')

def detail_pembayaran(request):
    return render(request, 'view/dashboard_siswa/detail_pembayaran.html')



# pengaturan siswa
@login_required
def pengaturan(request):

    return render(request, 'view/dashboard_siswa/pengaturan.html')
def course_siswa(request):
    return render(request, 'view/dashboard_siswa/course_siswa.html')

    user = request.user 
   
    # untuk foto profile
    try:
        profile = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        profile = None 

    context = {
        'profile': profile
    }

    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password lama
        if not user.check_password(old_password):
            messages.error(request, "Password lama salah.")
            return redirect('pengaturan')

        # Validasi panjang password baru
        if len(new_password) < 8:
            messages.error(request, "Password baru harus memiliki minimal 8 karakter.")
            return redirect('pengaturan')

        # Validasi konfirmasi password
        if new_password != confirm_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect('pengaturan')

        # Update password
        user.set_password(new_password)
        user.save()

        # Autentikasi ulang dengan password baru
        user = authenticate(username=user.username, password=new_password)
        if user is not None:
           
            auth_login(request, user)
            messages.success(request, "Password berhasil diubah.")
        else:
            messages.error(request, "Gagal login setelah perubahan password.")
            return redirect('pengaturan')

        return redirect('pengaturan')  

    return render(request, "view/dashboard_siswa/pengaturan.html",context)

# profile siswa
@login_required
def profile_siswa(request):
    user = request.user

    # Ambil profil pengguna
    try:
        profile = Students.objects.get(username=user.username)
    except Students.DoesNotExist:
        profile = Students.objects.create(
            username=user.username,
            name=f"{user.first_name} {user.last_name}",
            email=user.email
        )

    if request.method == "POST":
        # Update data profil (semua kecuali username)
        profile.phone = request.POST.get('phone')
        profile.name_ortu = request.POST.get('name_ortu')
        profile.phone_ortu = request.POST.get('phone_ortu')
        
        # Periksa dan tangani input date
        date_input = request.POST.get('date')
        if date_input:
            profile.date = date_input  
        else:
            profile.date = None  

        profile.address = request.POST.get('address')
        profile.school = request.POST.get('school')

        # Update foto profil jika ada
        if 'foto_profil' in request.FILES:
            foto_profil = request.FILES['foto_profil']
            fs = FileSystemStorage(location='static/img/profile')
            filename = fs.save(foto_profil.name, foto_profil)
            profile.foto_profil = f'img/profile/{filename}'

        # Update nama berdasarkan first_name dan last_name
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        profile.name = f"{user.first_name} {user.last_name}"

        # Simpan perubahan di model User dan Students
        user.save()
        profile.save()

        return redirect('profile_siswa')

    context = {
        'profile': profile,
        'user': user
    }
    return render(request, 'view/dashboard_siswa/profile_siswa.html', context)


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

    try:
        profile = Students.objects.get(username=user.username)
    except Students.DoesNotExist:
        profile = None 

    return render(request, 'view/dashboard_siswa/dashboard_siswa.html', {
        'days': days,
        'today_name': today_name,
        'total_points': total_points,
        'absen_status': absen_status,
        'profile': profile,
    })

# validasi login
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

