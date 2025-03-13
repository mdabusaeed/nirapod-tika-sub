from django.contrib.auth.models import AbstractUser
from django.db import models
from users.managers import CustomUserManager
from django.contrib.auth.models import Group


class User(AbstractUser):
    ROLE_CHOICES = (
        ('patient', 'Patient'),
        ('doctor', 'Doctor'),
        ('admin', 'Admin'),
    )
    phone_number = models.CharField(max_length=15, unique=True)
    nid = models.CharField(max_length=20, unique=True)
    email = models.EmailField(unique=True)
    address = models.TextField(blank=True, null=True)
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='patient')
    medical_details = models.TextField(blank=True,null=True)
    username = None 
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)  
    specialization = models.CharField(max_length=255, blank=True, null=True)

    objects = CustomUserManager()

    USERNAME_FIELD = 'phone_number'
    REQUIRED_FIELDS = ['nid']

    def __str__(self):
        return self.phone_number

