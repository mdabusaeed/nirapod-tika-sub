from djoser.serializers import UserCreateSerializer as BaseUserRegistrationSerializer, UserSerializer as BaseUserSerializer
from rest_framework import serializers
from django.contrib.auth.hashers import check_password
from rest_framework.validators import UniqueValidator
from users.models import User

class UserCreateSerializer(BaseUserRegistrationSerializer):
    nid = serializers.CharField(max_length=20, validators=[UniqueValidator(queryset=User.objects.all())])
    class Meta(BaseUserRegistrationSerializer.Meta):
        fields = ('id', 'phone_number','nid', 'password', 'first_name', 'last_name', 'address', 'email')
        extra_kwargs = {'password': {'write_only': True}}

class UserSerializer(BaseUserSerializer):
    
    class Meta(BaseUserSerializer.Meta):
        ref_name = "CustomUserSerializer"
        fields = ('id', 'phone_number','nid', 'first_name', 'last_name', 'address', 'email','medical_details')


class DoctorSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'phone_number', 'nid', 'first_name', 'last_name', 'address', 'email', 'specialization', 'profile_picture', 'medical_details')

    profile_picture = serializers.ImageField(required=False)

    
