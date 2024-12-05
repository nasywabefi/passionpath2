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
        # Jika username berubah atau ada perubahan di first_name/last_name
        user = User.objects.get(username=self.username)
        self.name = f"{user.first_name} {user.last_name}"
        super(Students, self).save(*args, **kwargs)

    def __str__(self):
        return self.username




