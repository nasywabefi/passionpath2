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
from .models import Students , Kelas ,Pembayaran
from django.core.files.storage import FileSystemStorage
from django.db.models import Q, Exists, OuterRef
from .models import Contact , ProfileAdmin , Episode
from django.conf import settings
from django.core.mail import send_mail
from django.utils import timezone
from django.http import HttpResponseForbidden
from django.utils.safestring import mark_safe
import random
from django.utils.timezone import now
import uuid

kelas = Kelas.objects.get(id_kelas=1)
kelas.episodes.all() 

def coming_soon(request):
    return render(request, 'view/coming_soon.html')

# Kelas
@login_required
def courses(request):
    id_kelas = request.GET.get('id_kelas') 
  
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas) if id_kelas else None
    
    pembayaran_sukses = Pembayaran.objects.filter(
        user=request.user,
        status_pembayaran="success",
        kelas=kelas
    ).exists()

    if pembayaran_sukses:
        kelas.episodes.filter(is_free=False).update(is_free=True)
    else:
        pass 

    # Ambil daftar episode berdasarkan relasi id_kelas
    episode_list = Episode.objects.filter(id_kelas=kelas) if kelas else []

    return render(request, 'view/courses/courses.html', {
        'kelas': kelas,
        'episode_list': episode_list,
        'pembayaran_sukses': pembayaran_sukses,
    })

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
        return redirect('register')  # Arahkan ke halaman login setelah registrasi sukses

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

    total_pengguna = User.objects.count()  # Hitung semua pengguna
    total_kelas = Kelas.objects.count()

    try:
        # Ubah nama kelas menjadi "Bisnis" dan "Web Developer" sesuai data di database
        business_kelas = Kelas.objects.get(nama_kelas='Bisnis')
    except Kelas.DoesNotExist:
        business_kelas = None  

    try:
        development_kelas = Kelas.objects.get(nama_kelas='Pemrograman')
    except Kelas.DoesNotExist:
        development_kelas = None  
    try:
        desain = Kelas.objects.get(nama_kelas='Desain')
    except Kelas.DoesNotExist:
        desain = None  
    try:
        bahasa = Kelas.objects.get(nama_kelas='Bahasa')
    except Kelas.DoesNotExist:
        bahasa = None  
    try:
        akuntansi = Kelas.objects.get(nama_kelas='Akuntansi')
    except Kelas.DoesNotExist:
        akuntansi = None  

    return render(request, 'index.html', {
        'business_kelas': business_kelas,
        'development_kelas': development_kelas,
        'bahasa': bahasa,
        'desain': desain,
        'akuntansi': akuntansi,
        'total_pengguna': total_pengguna,
        'total_kelas': total_kelas,

        
    })
# View untuk halaman about
def about(request):
    return render(request, 'view/about.html')
# View untuk halaman product
def product(request):
    try:
        # Ubah nama kelas menjadi "Bisnis" dan "Web Developer" sesuai data di database
        business_kelas = Kelas.objects.get(nama_kelas='Bisnis')
    except Kelas.DoesNotExist:
        business_kelas = None  

    try:
        development_kelas = Kelas.objects.get(nama_kelas='Pemrograman')
    except Kelas.DoesNotExist:
        development_kelas = None  
    try:
        desain = Kelas.objects.get(nama_kelas='Desain')
    except Kelas.DoesNotExist:
        desain = None  
    try:
        bahasa = Kelas.objects.get(nama_kelas='Bahasa')
    except Kelas.DoesNotExist:
        bahasa = None  
    try:
        akuntansi = Kelas.objects.get(nama_kelas='Akuntansi')
    except Kelas.DoesNotExist:
        akuntansi = None  

    return render(request, 'view/product.html', {
        'business_kelas': business_kelas,
        'development_kelas': development_kelas,
        'bahasa': bahasa,
        'desain': desain,
        'akuntansi': akuntansi,
    })

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

def laporan_admin(request):
    # Ambil profil admin
    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None

    # Ambil semua data pembayaran
    pembayaran_list = Pembayaran.objects.all()

    # Gabungkan data pembayaran dan profil admin dalam konteks
    context = {
        'pembayaran_list': pembayaran_list,  # Data pembayaran
        'profile_admin': profile_admin,  # Data profil admin
    }

    return render(request, 'view/dashboard_admin/laporan_admin.html', context)

def accounting(request):
    return render(request, 'view/courses/accounting.html')

def bussines(request, id_kelas=None, id_episode=None):
    # Ambil objek Kelas berdasarkan id_kelas
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)  # Mengambil kelas berdasarkan ID
    
    # Ambil semua episode yang berkaitan dengan kelas bisnis
    episode_list = Episode.objects.filter(id_kelas=kelas)  # Menampilkan episode berdasarkan kelas
    
    # Kirimkan kelas dan episode_list ke template
    return render(request, 'view/courses/bussines.html', {
        'kelas': kelas,  # Mengirim objek kelas
        'episode_list': episode_list,  # Mengirim daftar episode
    })

def design(request):
    return render(request, 'view/courses/design.html')
def development(request, id_kelas=None):
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)  # Ambil kelas berdasarkan id_kelas
    episode_list = Episode.objects.filter(id_kelas=kelas)  # Ambil episode terkait kelas ini
    
    return render(request, 'view/courses/development.html', {
        'kelas': kelas,
        'episode_list': episode_list,
    })
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
        return redirect('dashboard_siswa')  # Redirect jika bukan admin

    # Mengambil profil admin berdasarkan user yang sedang login
    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None  # Jika tidak ada, set ke None

    # Hitung total data
    total_pengguna = User.objects.count()  # Hitung semua pengguna
    total_kelas = Kelas.objects.count()  # Hitung semua kelas
    total_episode = Episode.objects.count()  # Hitung semua episode

    # Kirim data ke template
    context = {
        'total_pengguna': total_pengguna,
        'total_kelas': total_kelas,
        'total_episode': total_episode,
        'profile_admin': profile_admin,  # Kirim profil admin ke template
    }
    return render(request, 'view/dashboard_admin/dashboard_admin.html', context)

# pembayaran admin
def pembayaran_admin(request):

    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None
    # Ambil filter status dari query string, jika tidak ada gunakan 'all'
    status_filter = request.GET.get('status-filter', 'all')

    # Filter berdasarkan status
    if status_filter == 'approved':
        pembayaran_history_list = Pembayaran.objects.filter(status_pembayaran='success')
    elif status_filter == 'rejected':
        pembayaran_history_list = Pembayaran.objects.filter(status_pembayaran='ditolak')
    else:
        pembayaran_history_list = Pembayaran.objects.all()

    return render(request, 'view/dashboard_admin/pembayaran_admin.html', {
        'pembayaran_history_list': pembayaran_history_list,
        'profile_admin': profile_admin,
    })


# program admin
def program_admin(request):

    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None

    context = {
        'profile_admin': profile_admin,  # Kirim profil admin ke template
    }

    return render(request, 'view/dashboard_admin/program_admin.html', context)

#  program interaktif
def program_interaktif(request):

    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None

    programs = Kelas.objects.all()  
    context = {
        'programs': programs,  
        'profile_admin': profile_admin, 
    }
    return render(request, 'view/dashboard_admin/program_interaktif.html', context)
    

#  program detail
def program_detail(request, id_kelas):
    # Ambil data profil admin
    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None

    # Ambil kelas berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)

    # Gabungkan context untuk dikirim ke template
    context = {
        'profile_admin': profile_admin,
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

        # Perbarui total_modul pada kelas
        kelas.total_modul = kelas.episodes.count()  
        kelas.save()

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
        episode.is_free = request.POST.get('is_free') == 'True'  # Konversi dari string ke boolean

        # Mengupdate file video jika ada file baru yang diunggah
        if 'upload_video' in request.FILES:
            episode.upload_video = request.FILES['upload_video']

        episode.save()

        # Perbarui total_modul pada kelas setelah perubahan
        kelas.total_modul = kelas.episodes.count()
        kelas.save()

        return redirect('program_detail', id_kelas=kelas.id_kelas)

    # Jika metode GET, tampilkan form edit dengan data yang ada
    return render(request, 'view/dashboard_admin/program_input.html', {
        'kelas': kelas,
        'episode': episode,
    })


def delete_episode(request, id_kelas, id_episode):
    # Ambil kelas dan episode berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)
    episode = get_object_or_404(Episode, id=id_episode)

    # Hapus episode
    episode.delete()

    # Perbarui total_modul pada kelas setelah penghapusan
    kelas.total_modul = kelas.episodes.count() 
    kelas.save()

    return redirect('program_detail', id_kelas=kelas.id_kelas)


def program_input(request, id_kelas):
    # Ambil kelas berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=id_kelas)

    # Ambil profil admin jika user adalah admin
    try:
        profile_admin = ProfileAdmin.objects.get(username=request.user)
    except ProfileAdmin.DoesNotExist:
        profile_admin = None

    if request.method == 'POST':
        # Mengambil data dari form
        judul_episode = request.POST.get('judul_episode')
        deskripsi_episode = request.POST.get('deskripsi_episode')
        link_video = request.POST.get('link_video')
        is_free = request.POST.get('is_free') == 'True'  # Konversi dari string ke boolean

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
            link_video=link_video,
            is_free=is_free,
        )

        # Perbarui total_modul pada kelas
        kelas.total_modul = kelas.episodes.count()
        kelas.save()

        # Redirect ke halaman detail program
        return redirect('program_detail', id_kelas=kelas.id_kelas)

    # Gabungkan data profil admin dan kelas dalam konteks
    context = {
        'kelas': kelas,  # Data kelas
        'profile_admin': profile_admin,  # Data profil admin
    }

    return render(request, 'view/dashboard_admin/program_input.html', context)


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

    try:
        bahasa = Kelas.objects.get(nama_kelas='Bahasa')
    except Kelas.DoesNotExist:
        bahasa = None  
    try:
        akuntansi = Kelas.objects.get(nama_kelas='Akuntansi')
    except Kelas.DoesNotExist:
        akuntansi = None 
    try:
        desain = Kelas.objects.get(nama_kelas='Desain')
    except Kelas.DoesNotExist:
        desain = None 

    return render(request, 'view/dashboard_siswa/dashboard_siswa.html', {
        'days': days,
        'today_name': today_name,
        'total_points': total_points,
        'absen_status': absen_status,
        'profile': profile,
        'bahasa': bahasa,
        'akuntansi': akuntansi,
        'desain': desain,
    })

# PEMBAYARAN SISWA
def tambah_ke_keranjang(request, kelas_id):
    kelas = get_object_or_404(Kelas, id_kelas=kelas_id)
    
    # Ambil keranjang dari session atau buat baru
    keranjang = request.session.get('keranjang', [])
    
    # Periksa apakah kelas sudah ada di keranjang
    if kelas_id not in keranjang:
        keranjang.append(kelas_id)
        request.session['keranjang'] = keranjang
        request.session.modified = True
        messages.success(request, mark_safe(f"Kelas <strong>{kelas.nama_kelas}</strong> berhasil ditambahkan ke keranjang."))
    else:
        messages.warning(request, mark_safe(f"Kelas <strong>{kelas.nama_kelas}</strong> sudah ada di keranjang."))

    return redirect('pembayaran')  # Arahkan ke halaman pembayaran


def generate_unique_code():
    # Menghasilkan kode unik berupa angka 3 digit
    return random.randint(100, 999) 

def checkout(request, kelas_id):
    # Ambil kelas berdasarkan kelas_id
    kelas = get_object_or_404(Kelas, id_kelas=kelas_id)

    # Hanya buat entri pembayaran sementara tanpa menyimpan ke database
    pembayaran = Pembayaran.objects.create(
        user=request.user,
        kelas=kelas,
        total_harga=kelas.harga,
        status_pembayaran='pending',  # Status 'pending'
    )

    # Arahkan ke halaman detail pembayaran
    return redirect('detail_pembayaran', pembayaran_id=pembayaran.id)


@login_required
def pembayaran(request, kelas_id):
    # Ambil kelas berdasarkan kelas_id
    kelas = get_object_or_404(Kelas, id_kelas=kelas_id)

    # Periksa apakah user sudah pernah membeli kelas ini dan statusnya "Ditolak"
    if Pembayaran.objects.filter(user=request.user, kelas=kelas).exclude(status_pembayaran='ditolak').exists():
        error_message = "Anda sudah melakukan pembayaran untuk kelas ini. Anda hanya bisa membeli kelas lagi jika status pembayaran sebelumnya 'Ditolak'."
        return render(request, 'view/dashboard_siswa/pembayaran.html', {
            'kelas': kelas,
            'error_message': error_message,
        })

    # Reset keranjang menjadi hanya kelas yang dipilih
    keranjang = [kelas_id]
    request.session['keranjang'] = keranjang
    request.session.modified = True

    # Ambil kelas yang ada di keranjang
    kelas_list = Kelas.objects.filter(id_kelas__in=keranjang)
    total_harga = sum(k.harga for k in kelas_list)

    try:
        siswa = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        siswa = None

    # Cek apakah profil siswa lengkap
    if not all([siswa.name, siswa.email, siswa.phone, siswa.name_ortu, siswa.phone_ortu, siswa.address]):
        return render(request, 'view/dashboard_siswa/pembayaran.html', {
            'kelas': kelas,
            'kelas_list': kelas_list,
            'total_harga': total_harga,
            'error_message': 'Profil Anda belum lengkap. Silakan lengkapi profil untuk melanjutkan pembayaran.',
            'show_profile_alert': True,  # Flag untuk menampilkan SweetAlert
        })

    if request.method == 'POST':
        # Ambil data dari request POST
        nama_pengirim = request.POST.get('nama-pengirim')
        metode_pembayaran = request.POST.get('metode_pembayaran')
        bukti_pembayaran = request.FILES.get('bukti-pembayaran')
        nomor_rekening_dan_nama = request.POST.get('nomor_rekening_dan_nama')  

        if metode_pembayaran == 'Mandiri':
            nomor_rekening_dan_nama = nomor_rekening_dan_nama or '123-456-7890 Mandiri Admin'
        elif metode_pembayaran == 'Dana':
            nomor_rekening_dan_nama = nomor_rekening_dan_nama or '098-765-4321 Dana Admin'
        else:
            nomor_rekening_dan_nama = nomor_rekening_dan_nama or '' 

        # Validasi input
        if not all([nama_pengirim, metode_pembayaran, bukti_pembayaran, nomor_rekening_dan_nama]):
            error_message = "Semua data harus diisi!"
            return render(request, 'view/dashboard_siswa/pembayaran.html', {
                'kelas': kelas,
                'kelas_list': kelas_list,
                'total_harga': total_harga,
                'error_message': error_message,
            })

        total_harga = sum(k.harga for k in kelas_list)

        # Membuat instance Pembayaran baru
        pembayaran = Pembayaran(
            user=request.user, 
            kelas=kelas, 
            nama_pengirim=nama_pengirim,
            metode_pembayaran=metode_pembayaran,
            nomor_rekening_dan_nama=nomor_rekening_dan_nama, 
            total_harga=total_harga,
            bukti_pembayaran=bukti_pembayaran,
            # Generate kode pembayaran otomatis
            kode_pembayaran=f"INV-{now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}",
        )

        # Simpan pembayaran ke database
        pembayaran.save()

        # Redirect setelah pembayaran berhasil
        return redirect('riwayat_bayar')  

    return render(request, 'view/dashboard_siswa/pembayaran.html', {
        'kelas': kelas,
        'kelas_list': kelas_list,
        'total_harga': total_harga,
        'siswa': siswa,
    })


def riwayat_bayar(request):
    try:
        profile = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        profile = None

    # Ambil daftar pembayaran user yang sedang login
    riwayat_pembayaran = Pembayaran.objects.filter(user=request.user)

    return render(request, 'view/dashboard_siswa/riwayat_bayar.html', {
        'riwayat_pembayaran': riwayat_pembayaran,
        'profile': profile,  # Kirimkan data profil ke template
    })




def detail_pembayaran(request, pembayaran_id):
    pembayaran = get_object_or_404(Pembayaran, id=pembayaran_id, user=request.user)

    try:
        siswa = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        siswa = None

    if request.method == 'POST':
        nama_pengirim = request.POST.get('nama-pengirim')
        metode_pembayaran = request.POST.get('metode_pembayaran')
        bukti_pembayaran = request.FILES.get('bukti-pembayaran')

        if not nama_pengirim or not metode_pembayaran or not bukti_pembayaran:
            messages.error(request, "Harap mengisi semua bidang wajib.")
        else:
            pembayaran.nama_pengirim = nama_pengirim
            pembayaran.metode_pembayaran = metode_pembayaran
            pembayaran.bukti_pembayaran = bukti_pembayaran
            pembayaran.status_pembayaran = 'pending'  # Set ulang status pembayaran
            pembayaran.save()
            messages.success(request, "Pembayaran berhasil diperbarui.")
            return redirect('dashboard_siswa')  # Ganti dengan URL dashboard siswa Anda

    context = {
        'pembayaran': pembayaran,
        'siswa': siswa,
    }

    return render(request, 'view/dashboard_siswa/detail_pembayaran.html', context)



def approve_pembayaran(request, pembayaran_id):
    pembayaran = Pembayaran.objects.get(id=pembayaran_id)
    pembayaran.status_pembayaran = 'success'  # Mengubah status menjadi success
    pembayaran.tanggal_approve_tolak = timezone.now()  # Menambahkan waktu approve
    pembayaran.save()
    
    return redirect('pembayaran_admin')  # Kembali ke halaman admin pembayaran

def reject_pembayaran(request, pembayaran_id):
    pembayaran = Pembayaran.objects.get(id=pembayaran_id)
    pembayaran.status_pembayaran = 'ditolak'  # Mengubah status menjadi ditolak
    pembayaran.tanggal_approve_tolak = timezone.now()  # Menambahkan waktu tolak
    pembayaran.save()
    
    return redirect('pembayaran_admin')  # Kembali ke halaman admin pembayaran


@login_required
def pembayaran_admin(request):
   
    pembayaran_history_list = Pembayaran.objects.all().select_related('user')  

    return render(request, 'view/dashboard_admin/pembayaran_admin.html', {
        'pembayaran_history_list': pembayaran_history_list,
    })


# View untuk halaman belajar
def belajar(request):

    try:
        profile = Students.objects.get(username=request.user.username)
    except Students.DoesNotExist:
        profile = None

    if not request.user.is_authenticated:
        return redirect('login')  # Pastikan pengguna sudah login

    try:
        # Ambil kelas yang sudah dibeli dengan status pembayaran "Success"
        purchased_classes = Kelas.objects.filter(
            Exists(
                Pembayaran.objects.filter(
                    user=request.user,
                    status_pembayaran="Success",
                    kelas=OuterRef('pk')  # Relasi ke kelas
                )
            )
        )

        # Ambil kelas yang gratis
        free_classes = Kelas.objects.filter(episodes__is_free=True)

        # Gabungkan hasil kedua query
        available_classes = list(purchased_classes) + list(free_classes)  # Gabungkan hasil query

        # Pastikan tidak ada duplikasi kelas
        available_classes = list({kelas.id_kelas: kelas for kelas in available_classes}.values())

        # Debugging: Log kelas yang tersedia
        for kelas in available_classes:
            print(f"Kelas tersedia: {kelas.nama_kelas}")

    except Exception as e:
        print(f"Error: {e}")

    return render(request, 'view/dashboard_siswa/belajar.html', {
        'available_classes': available_classes,
        'profile': profile, 
    })

    
def course_siswa(request, kelas_id):
    # Ambil data kelas berdasarkan ID
    kelas = get_object_or_404(Kelas, id_kelas=kelas_id)

    # Ambil semua episode dari kelas ini
    episodes = Episode.objects.filter(id_kelas=kelas).order_by('id')

    # Ambil episode pertama atau berdasarkan parameter 'episode_id'
    episode_id = request.GET.get('episode_id')
    if episode_id:
        current_episode = get_object_or_404(Episode, id=episode_id, id_kelas=kelas)
    else:
        current_episode = episodes.first()

    # Cek apakah episode yang diminta berbayar dan apakah pengguna sudah membeli kelas ini
    pembayaran_sukses = Pembayaran.objects.filter(
        user=request.user,
        status_pembayaran="success",
        kelas=kelas
    ).exists()

    # Jika episode berbayar dan pengguna belum membeli kelas
    if current_episode.is_free == False and not pembayaran_sukses:
        # Temukan episode sebelumnya
        current_index = list(episodes).index(current_episode)
        previous_episode = episodes[current_index - 1] if current_index > 0 else None

        # Tampilkan SweetAlert untuk mengarahkan ke halaman pembayaran
        return render(request, 'view/dashboard_siswa/course_siswa.html', {
            'kelas': kelas,
            'episodes': episodes,
            'current_episode': previous_episode,  # Kembalikan ke episode sebelumnya
            'error_message': 'Episode ini berbayar. Silakan lakukan pembayaran untuk mengaksesnya.',
            'show_payment_alert': True  # Flag untuk menampilkan SweetAlert
        })

    # Temukan previous dan next episode berdasarkan urutan
    current_index = list(episodes).index(current_episode)
    previous_episode = episodes[current_index - 1] if current_index > 0 else None
    next_episode = episodes[current_index + 1] if current_index < len(episodes) - 1 else None

    return render(request, 'view/dashboard_siswa/course_siswa.html', {
        'kelas': kelas,
        'episodes': episodes,
        'current_episode': current_episode,
        'previous_episode': previous_episode,
        'next_episode': next_episode,
        'error_message': None,  # Reset error message
        'show_payment_alert': False  # Flag untuk menampilkan SweetAlert
    })

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


