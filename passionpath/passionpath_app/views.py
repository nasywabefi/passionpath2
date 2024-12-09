from urllib import request
from django.contrib.auth import authenticate, login as auth_login , logout
from django.shortcuts import render, redirect,get_object_or_404
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
from .models import Students, Kelas
from django.core.files.storage import FileSystemStorage
from django.contrib.auth.hashers import check_password

from .models import Contact , ProfileAdmin , Episode
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponseForbidden

kelas = Kelas.objects.get(id_kelas=1)
kelas.episodes.all() 

# Redirect Ke Profile Siswa/admin
@login_required
def profile_redirect(request):
    user = request.user
    if user.is_superuser:
        return redirect('pengaturan_admin') 
    else:
        return redirect('profile_siswa')
    
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


# validasi login
@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'view/dashboard_admin.html', {'user': request.user})
    else:
        return render(request, 'view/dashboard_siswa/dashboard_siswa.html', {'user': request.user})
    
# register
def register(request):
    # Cek jika user sudah terautentikasi
    if request.user.is_authenticated:
        return redirect(request.META.get('HTTP_REFERER', '/')) 

    if request.method == 'POST':
        first_name = request.POST.get('first_name')
        last_name = request.POST.get('last_name')
        email = request.POST.get('email')
        username = request.POST.get('username')
        password = request.POST.get('password')

        # Validasi input
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

        # Membuat User baru
        user = User.objects.create_user(
            first_name=first_name,
            last_name=last_name,
            username=username,
            email=email,
            password=password
        )
        user.save()

        # Membuat entri di model Students
        id_siswa = f"S{Students.objects.count() + 1:05d}"  # ID otomatis
        student = Students.objects.create(
            username=user.username,
            email=user.email,
            name=f"{user.first_name} {user.last_name}",
            id_siswa=id_siswa  # Menggunakan ID yang terurut
        )
        student.save()

        messages.success(request, 'Registrasi berhasil! Silakan login.')
        return redirect('login')  # Arahkan ke halaman login setelah registrasi sukses

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
# HALAMAN lOGIN
def login(request):
    return render(request, 'view/login.html')


# ===== HOME PAGE ===== 
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


# COURSE HOME PAGE
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
    


# ====== HALAMAN DASHBOARD ADMIN =====
# VIEW HALAMAN VIDIEO INTERAKTIF
def video_iteraktif(request):
    return render(request, 'view/dashboard_admin/video_interaktif.html')

# PROFILE ADMIN 
@login_required
def pengaturan_admin(request):
    user = request.user

    # Pastikan user adalah admin
    if not user.is_superuser:
        return redirect('profile_siswa')  
    # Mengambil atau membuat profil admin
    try:
        profile_admin = ProfileAdmin.objects.get(username=user)
    except ProfileAdmin.DoesNotExist:
        # Jika tidak ada, buat profil admin baru
        profile_admin = ProfileAdmin(username=user)
        profile_admin.save()

    # Menggunakan form POST untuk memperbarui profil admin
    if request.method == 'POST':
        # Perbarui data User
        user.first_name = request.POST.get('first_name', user.first_name)
        user.save()

        # Perbarui data profil admin
        profile_admin.phone = request.POST.get('phone', profile_admin.phone)
        profile_admin.address = request.POST.get('address', profile_admin.address)

        # Tangani tanggal lahir
        date_of_birth = request.POST.get('date', None)
        if date_of_birth:
            profile_admin.date_of_birth = date_of_birth

        # Tangani foto profil
        if 'foto_profil' in request.FILES:
            foto_profil = request.FILES['foto_profil']
            fs = FileSystemStorage(location='static/img/profile')
            filename = fs.save(foto_profil.name, foto_profil)
            profile_admin.foto_profil = f'img/profile/{filename}'

        # Simpan perubahan
        profile_admin.save()

        messages.success(request, "Profil berhasil diperbarui.")
        return redirect('pengaturan_admin')

    return render(request, 'view/dashboard_admin/pengaturan_admin.html', {'profile_admin': profile_admin})

# dashboard admin
@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('dashboard_siswa') 
    return render(request, 'view/dashboard_admin/dashboard_admin.html')

# pembayaran admin
def pembayaran_admin(request):
    return render(request, 'view/dashboard_admin/pembayaran_admin.html')

# program admin
def program_admin(request):
    return render(request, 'view/dashboard_admin/program_admin.html')

#  program interaktif
def program_interaktif(request):
    programs = Kelas.objects.all()  
    context = {
        'programs': programs,  
    }
    return render(request, 'view/dashboard_admin/program_interaktif.html', context)
    

#  program detail
def program_detail(request, id_kelas):
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)  
    context = {
        'kelas': kelas,
    }
    return render(request, 'view/dashboard_admin/program_detail.html', context)

# update deskripsi kelas
def update_kelas(request, id_kelas):
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)
    if request.method == 'POST':
        deskripsi = request.POST.get('deskripsi')
        if deskripsi:
            kelas.deskripsi = deskripsi
            kelas.save()
            return redirect('program_detail', id_kelas=kelas.id_kelas)
    return HttpResponseForbidden("You do not have permission to edit this class.")

# input episode
def add_episode(request, id_kelas):
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)
    
    if request.method == 'POST':
        # Mengambil data dari form dan file upload
        judul_episode = request.POST.get('judul_episode')
        deskripsi_episode = request.POST.get('deskripsi_episode')
        upload_video = request.FILES.get('upload_video')
        link_video = request.POST.get('link_video')

        # Membuat objek Episode baru
        episode = Episode(
            kelas=kelas,
            judul_episode=judul_episode,
            deskripsi_episode=deskripsi_episode,
            upload_video=upload_video,
            link_video=link_video
        )
        episode.save()

        # Redirect setelah episode ditambahkan
        return redirect('program_detail', id_kelas=kelas.id_kelas)

    return render(request, 'view/add_episode.html', {'kelas': kelas})

def edit_episode(request, id_kelas, id_episode):
    # Mendapatkan objek Kelas dan Episode berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)
    episode = get_object_or_404(Episode, id=id_episode)

    # Mengupdate episode jika form disubmit
    if request.method == 'POST':
        episode.judul_episode = request.POST.get('judul_episode')
        episode.deskripsi_episode = request.POST.get('deskripsi_episode')
        episode.link_video = request.POST.get('link_video')

        if 'upload_video' in request.FILES:
            episode.upload_video = request.FILES['upload_video']

        episode.save()  # Menyimpan perubahan ke database
        return redirect('program_detail', id_kelas=kelas.id_kelas)  # Redirect ke halaman detail program

    # Jika metode GET, tampilkan form edit dengan data yang ada
    return render(request, 'view/dashboard_admin/program_input.html', {
        'kelas': kelas,
        'episode': episode,  # Mengirim data episode ke template
    })

def delete_episode(request, id_kelas, id_episode):
    # Ambil kelas dan episode berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)
    episode = get_object_or_404(Episode, id=id_episode)

    # Hapus episode
    episode.delete()
    return redirect('program_detail', id_kelas=kelas.id_kelas)

def program_input(request, id_kelas):
    kelas = Kelas.objects.get(id_kelas=id_kelas)
    
    if request.method == 'POST':
        judul_episode = request.POST.get('judul_episode')
        deskripsi_episode = request.POST.get('deskripsi_episode')
        link_video = request.POST.get('link_video')
        
        # Menangani upload file video
        upload_video = request.FILES.get('upload_video')
        video_url = None
        
        if upload_video:
            fs = FileSystemStorage()
            video_url = fs.save(upload_video.name, upload_video)
        
        # Menambahkan episode ke dalam database
        Episode.objects.create(
            id_kelas=kelas,
            judul_episode=judul_episode,
            deskripsi_episode=deskripsi_episode,
            upload_video=video_url,
            link_video=link_video
        )
        
        # Redirect ke halaman detail program
        return redirect('program_detail', id_kelas=kelas.id_kelas)
    
    return render(request, 'view/dashboard_admin/program_input.html', {'kelas': kelas})


# ==== DASHBOARD SISWA ====
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

# PEMBAYARAN SISWA
def pembayaran(request):
    return render(request, 'view/dashboard_siswa/pembayaran.html')
# DETAIL PEMBAYARAN SISWA
def detail_pembayaran(request):
    return render(request, 'view/dashboard_siswa/detail_pembayaran.html')

# View untuk halaman belajar
def belajar(request):
    return render(request, 'view/dashboard_siswa/belajar.html')


    
# course untuk siswa
def course_siswa(request):
    return render(request, 'view/dashboard_siswa/course_siswa.html')

# pengaturan siswa / reset password
@login_required
def pengaturan_siswa(request):
    user = request.user 

    # Cek jika user adalah admin atau superuser
    if user.is_superuser or user.is_staff:
        messages.error(request, "Anda tidak diizinkan mengakses halaman ini.")
        return redirect('index') 
    
   
    try:
        profile = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        profile = None

    # Jika bukan siswa, redirect ke halaman lain
    if not profile:
        messages.error(request, "Hanya siswa yang dapat mengakses halaman ini.")
        return redirect('index')  

    context = {
        'profile': profile
    }

    # Proses perubahan password jika method POST
    if request.method == "POST":
        old_password = request.POST.get("old_password")
        new_password = request.POST.get("new_password")
        confirm_password = request.POST.get("confirm_password")

        # Validasi password lama
        if not user.check_password(old_password):
            messages.error(request, "Password lama salah.")
            return redirect('pengaturan_siswa')

        # Validasi panjang password baru
        if len(new_password) < 8:
            messages.error(request, "Password baru harus memiliki minimal 8 karakter.")
            return redirect('pengaturan_siswa')

        # Validasi konfirmasi password
        if new_password != confirm_password:
            messages.error(request, "Konfirmasi password tidak cocok.")
            return redirect('pengaturan_siswa')

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
            return redirect('pengaturan_siswa')

        return redirect('pengaturan_siswa')  

    return render(request, "view/dashboard_siswa/pengaturan.html", context)


# profile siswa
@login_required
def profile_siswa(request):
    user = request.user


    if user.is_superuser or user.is_staff:
    
        messages.error(request, "Anda tidak diizinkan mengakses halaman ini.")
        return redirect('index')

    # Ambil atau buat profil siswa
    profile, created = Students.objects.get_or_create(
        username=user.username,
        defaults={
            'email': user.email,
            'name': f"{user.first_name} {user.last_name}"
        }
    )

    if request.method == "POST":
        profile.phone = request.POST.get('phone')
        profile.name_ortu = request.POST.get('name_ortu')
        profile.phone_ortu = request.POST.get('phone_ortu')
        profile.date = request.POST.get('date') or None
        profile.address = request.POST.get('address')
        profile.school = request.POST.get('school')

        # Update foto profil jika ada
        if 'foto_profil' in request.FILES:
            foto_profil = request.FILES['foto_profil']
            fs = FileSystemStorage(location='static/img/profile')
            filename = fs.save(foto_profil.name, foto_profil)
            profile.foto_profil = f'img/profile/{filename}'

        # Update nama pengguna
        user.first_name = request.POST.get('first_name')
        user.last_name = request.POST.get('last_name')
        profile.name = f"{user.first_name} {user.last_name}"

        user.save()
        profile.save()

        return redirect('profile_siswa')

    return render(request, 'view/dashboard_siswa/profile_siswa.html', {
        'profile': profile,
        'user': user,
    })


