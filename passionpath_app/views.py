from urllib import request
from django.contrib.auth import authenticate, login as auth_login , logout
from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required



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
    return render(request, 'view/dashboard_siswa.html')

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


# register
def register(request):
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

      
        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  
          
            if user.is_superuser:
                return redirect('dashboard_admin') 
            else:
                return redirect('index') 
        else:
            messages.error(request, 'Password atau Username Anda Salah!!!')
            return redirect('login') 
    return render(request, 'view/login.html')  

def user_logout(request):
    logout(request)
    return redirect('index')



@login_required
def dashboard_siswa(request):
    if request.user.is_superuser:
        return redirect('dashboard_admin')
    return render(request, 'view/dashboard_siswa.html')

@login_required
def dashboard(request):
    if request.user.is_superuser:
        return render(request, 'view/dashboard_admin.html', {'user': request.user})
    else:
        return render(request, 'view/dashboard_siswa.html', {'user': request.user})

@login_required
def dashboard_admin(request):
    if not request.user.is_superuser:
        return redirect('dashboard_siswa') 
    return render(request, 'view/dashboard_admin.html')