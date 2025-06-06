# Generated by Django 5.1.7 on 2025-04-27 02:06

import cloudinary.models
import django.db.models.deletion
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('vaccination', '0012_vaccine_stock'),
    ]

    operations = [
        migrations.CreateModel(
            name='VaccineImage',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('image', cloudinary.models.CloudinaryField(max_length=255, verbose_name='image')),
                ('vaccine', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='images', to='vaccination.vaccine')),
            ],
        ),
    ]
