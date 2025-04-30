from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
from users.serializers import UserCreateSerializer 
from .models import User
from .serializers import UserSerializer,DoctorSerializer
from vaccination.models import VaccinationSchedule  
from vaccination.serializers import VaccinationScheduleSerializer


class UserProfileView(ModelViewSet):
    serializer_class = UserSerializer

    def get_queryset(self):
        if self.request.user.is_staff:  
            return User.objects.filter(role='patient')  
        else:
            return User.objects.filter(id=self.request.user.id)  
    
    def get_object(self):
        return self.request.user
    
    def retrieve(self, request, *args, **kwargs):
        user = self.get_object()
        
        vaccinations = VaccinationSchedule.objects.filter(patient=request.user)
        vaccination_serializer = VaccinationScheduleSerializer(vaccinations, many=True)
        
        data = {
            "user_info": UserSerializer(user).data,
            "medical_details": user.medical_details,  
            "vaccination_history": vaccination_serializer.data
        }
        return Response(data)
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        for field, value in serializer.validated_data.items():
            if value == "":
               
                continue
            setattr(user, field, value)
        
        user.save()  

        return Response(serializer.data)
    

class DoctorProfileView(ModelViewSet):
    serializer_class = DoctorSerializer
    parser_classes = (MultiPartParser, FormParser)


    def get_queryset(self):
        if self.request.user.is_staff:  
            return User.objects.filter(role='doctor') 
        else:
            return User.objects.filter(id=self.request.user.id)  

    def get_object(self):
        return self.request.user 
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()

        serializer = self.get_serializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data)


class EmailExistsView(APIView):
    permission_classes = [AllowAny]
    
    def post(self, request):
        email = request.data.get('email')
        
        if not email:
            return Response(
                {"error": "Email is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        exists = User.objects.filter(email=email).exists()
        
        return Response(
            {"exists": exists},
            status=status.HTTP_200_OK
        )
    
    def get(self, request):
        email = request.query_params.get('email')
        
        if not email:
            return Response(
                {"error": "Email parameter is required"}, 
                status=status.HTTP_400_BAD_REQUEST
            )
            
        exists = User.objects.filter(email=email).exists()
        
        return Response(
            {"exists": exists},
            status=status.HTTP_200_OK
        )
    
