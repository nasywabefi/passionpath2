# Generated by Django 5.1.4 on 2024-12-10 08:58

import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Contact',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('message', models.TextField()),
                ('date_sent', models.DateTimeField(auto_now_add=True)),
            ],
        ),
        migrations.CreateModel(
            name='Kelas',
            fields=[
                ('id_kelas', models.AutoField(primary_key=True, serialize=False)),
                ('nama_kelas', models.CharField(max_length=100)),
                ('deskripsi', models.TextField(blank=True, null=True)),
                ('total_modul', models.IntegerField(default=0)),
                ('harga', models.DecimalField(decimal_places=2, default=0.0, max_digits=10)),
            ],
        ),
        migrations.CreateModel(
            name='Students',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_siswa', models.CharField(editable=False, max_length=10, unique=True)),
                ('username', models.CharField(max_length=150, unique=True)),
                ('name', models.CharField(max_length=255)),
                ('email', models.EmailField(max_length=254)),
                ('phone', models.CharField(blank=True, max_length=20, null=True)),
                ('name_ortu', models.CharField(blank=True, max_length=255, null=True)),
                ('phone_ortu', models.CharField(blank=True, max_length=20, null=True)),
                ('date', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('school', models.CharField(blank=True, max_length=255, null=True)),
                ('foto_profil', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
            ],
        ),
        migrations.CreateModel(
            name='Absensi',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateField()),
                ('points', models.IntegerField(default=0)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='Episode',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('judul_episode', models.CharField(max_length=100)),
                ('deskripsi_episode', models.TextField(blank=True, null=True)),
                ('upload_video', models.FileField(blank=True, null=True, upload_to='videos/')),
                ('link_video', models.URLField(blank=True, null=True)),
                ('is_free', models.BooleanField(default=False)),
                ('id_kelas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='episodes', to='passionpath_app.kelas')),
            ],
        ),
        migrations.CreateModel(
            name='Pembayaran',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('status_pembayaran', models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('ditolak', 'Ditolak')], default='ditolak', max_length=10)),
                ('nama_pengirim', models.CharField(max_length=100)),
                ('metode_pembayaran', models.CharField(max_length=50)),
                ('nomor_rekening_pengirim', models.CharField(max_length=50)),
                ('bukti_pembayaran', models.ImageField(blank=True, null=True, upload_to='bukti_pembayaran/')),
                ('kode_pembayaran', models.CharField(max_length=20, unique=True)),
                ('total_harga', models.DecimalField(decimal_places=2, max_digits=10)),
                ('tanggal_pembayaran', models.DateTimeField(auto_now_add=True)),
                ('kelas', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pembayaran', to='passionpath_app.kelas')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='pembayaran', to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='ProfileAdmin',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('id_admin', models.CharField(editable=False, max_length=10, unique=True)),
                ('phone', models.CharField(blank=True, max_length=15, null=True)),
                ('date_of_birth', models.DateField(blank=True, null=True)),
                ('address', models.TextField(blank=True, null=True)),
                ('foto_profil', models.ImageField(blank=True, null=True, upload_to='profile_pics/')),
                ('username', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, related_name='profile_admin', to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]
