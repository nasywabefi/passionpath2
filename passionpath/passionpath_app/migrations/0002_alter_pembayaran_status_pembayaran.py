# Generated by Django 5.1.4 on 2024-12-10 12:49

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passionpath_app', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='pembayaran',
            name='status_pembayaran',
            field=models.CharField(choices=[('pending', 'Pending'), ('success', 'Success'), ('ditolak', 'Ditolak')], default='pending', max_length=10),
        ),
    ]