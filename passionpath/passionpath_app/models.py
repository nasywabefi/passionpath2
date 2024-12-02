from django.db import models
from django.contrib.auth.models import User

class Absensi(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    date = models.DateField()
    points = models.IntegerField(default=0)
    
    def __str__(self):
        return f"{self.user.username} - {self.date} - {self.points} poin"
