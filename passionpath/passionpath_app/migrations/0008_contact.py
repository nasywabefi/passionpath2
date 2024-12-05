# Generated by Django 5.1.3 on 2024-12-04 07:52

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('passionpath_app', '0007_students_foto_profil_alter_students_phone_and_more'),
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
    ]
