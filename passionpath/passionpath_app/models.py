from django.db import models
from django.contrib.auth.models import User


class Contact(models.Model):
    name = models.CharField(max_length=255)
    email = models.EmailField()
    message = models.TextField()
    date_sent = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} on {self.date_sent}"

class Absensi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.points} poin"



class Students(models.Model):
    id_siswa = models.CharField(max_length=10, unique=True, editable=False)
    username = models.CharField(max_length=150, unique=True)
    name = models.CharField(max_length=255)
    email = models.EmailField()
    phone = models.CharField(max_length=20, null=True, blank=True)
    name_ortu = models.CharField(max_length=255, null=True, blank=True)
    phone_ortu = models.CharField(max_length=20, null=True, blank=True)
    date = models.DateField(null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    school = models.CharField(max_length=255, null=True, blank=True)
    foto_profil = models.ImageField(upload_to='profile_pics/', null=True, blank=True)

    def save(self, *args, **kwargs):
        # Generate id_siswa secara otomatis hanya saat pertama kali dibuat
        if not self.id_siswa:
            last_student = Students.objects.order_by('-id_siswa').first()
            if last_student:
                # Ambil angka dari ID terakhir, tambahkan 1, lalu format ulang
                last_number = int(last_student.id_siswa[1:])
                new_number = last_number + 1
            else:
                # Jika belum ada siswa, mulai dari 1
                new_number = 1

            self.id_siswa = f"S{new_number:05d}"  # Format menjadi S00001, S00002, dst.

        # Update nama berdasarkan User terkait
        if self.username:
            user = User.objects.filter(username=self.username).first()
            if user:
                self.name = f"{user.first_name} {user.last_name}"
        super(Students, self).save(*args, **kwargs)

    def __str__(self):
        return self.id_siswa

class ProfileAdmin(models.Model):
    username = models.OneToOneField(User, on_delete=models.CASCADE, related_name="profile_admin")
    id_admin = models.CharField(max_length=10, unique=True, editable=False)  
    phone = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    address = models.TextField(blank=True, null=True)
    foto_profil = models.ImageField(upload_to='profile_pics/', blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.id_admin:
            # Generate ID otomatis
            last_profile = ProfileAdmin.objects.filter(id_admin__startswith="A").order_by('-id_admin').first()
            if last_profile:
                last_number = int(last_profile.id_admin[1:]) 
                new_number = last_number + 1
            else:
                new_number = 1  
            self.id_admin = f"A{new_number:05d}" 
        super(ProfileAdmin, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.username.username} - {self.id_admin}"


class Kelas(models.Model):
    id_kelas = models.AutoField(primary_key=True)
    nama_kelas = models.CharField(max_length=100)
    deskripsi = models.TextField(blank=True, null=True)
    total_modul = models.IntegerField(default=0)

    def __str__(self):
        return self.nama_kelas



class Episode(models.Model):
    id = models.AutoField(primary_key=True)
    id_kelas = models.ForeignKey('Kelas', on_delete=models.CASCADE, related_name='episodes')
    judul_episode = models.CharField(max_length=100)
    deskripsi_episode = models.TextField(blank=True, null=True)
    upload_video = models.FileField(upload_to='uploads/videos/', blank=True, null=True)
    link_video = models.URLField(max_length=200, blank=True, null=True)

    def __str__(self):
        return f"{self.judul_episode} ({self.id_kelas.nama_kelas})"