from urllib import request
from django.shortcuts import render

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

# View untuk halaman login
def login(request):
    return render(request, 'view/login.html')

# View untuk halaman contact
def register(request):
    return render(request, 'view/register.html')