from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.generics import RetrieveUpdateAPIView,CreateAPIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.response import Response
from rest_framework import serializers
from rest_framework import status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.views import APIView
# from users.serializers import UserCreateSerializer 
from .models import User
from .serializers import UserSerializer,DoctorSerializer
from vaccination.models import VaccinationSchedule  
from vaccination.serializers import VaccinationScheduleSerializer
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


from django.contrib.auth import get_user_model
from django.utils.http import urlsafe_base64_decode
from django.utils.encoding import force_str
from rest_framework.decorators import api_view
from users.utils import email_verification_token
from django.contrib.sites.shortcuts import get_current_site
from users.utils import send_activation_email


class UserProfileView(ModelViewSet):
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]

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
        
        # Debug info
        print(f"User ID: {user.id}, Role: {user.role}")
        print(f"Request data: {request.data}")
        
        try:
            # Convert request.data to mutable dict if it's a QueryDict
            if hasattr(request.data, 'copy'):
                data = request.data.copy()  # For QueryDict
            else:
                data = dict(request.data)   # For regular dict
            
            # Prevent unique validation errors by removing fields with same values
            # Handle both string and list values (QueryDict can have different formats)
            
            # Email check
            email_value = data.get('email')
            if email_value:
                # Handle list format from QueryDict
                if isinstance(email_value, list) and email_value[0] == user.email:
                    data.pop('email')
                # Handle string format
                elif email_value == user.email:
                    data.pop('email')
                
            # Phone number check
            phone_value = data.get('phone_number')
            if phone_value:
                if isinstance(phone_value, list) and phone_value[0] == user.phone_number:
                    data.pop('phone_number')
                elif phone_value == user.phone_number:
                    data.pop('phone_number')
                
            # NID check
            nid_value = data.get('nid')
            if nid_value:
                if isinstance(nid_value, list) and nid_value[0] == user.nid:
                    data.pop('nid')
                elif nid_value == user.nid:
                    data.pop('nid')
            
            # Only update fields that are explicitly provided in request.data
            serializer = self.get_serializer(user, data=data, partial=True)
            
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            # Get updated user data for response
            updated_user = self.get_serializer(user)
            return Response(updated_user.data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"Error in update: {str(e)}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    

class DoctorProfileView(ModelViewSet):
    serializer_class = DoctorSerializer
    permission_classes = [IsAuthenticated]
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
        
        # Debug info
        print(f"Doctor ID: {user.id}, Role: {user.role}")
        print(f"Request data: {request.data}")
        
        try:
            # Convert request.data to mutable dict if it's a QueryDict
            if hasattr(request.data, 'copy'):
                data = request.data.copy()  # For QueryDict
            else:
                data = dict(request.data)   # For regular dict
            
            # Prevent unique validation errors by removing fields with same values
            # Handle both string and list values (QueryDict can have different formats)
            
            # Email check
            email_value = data.get('email')
            if email_value:
                # Handle list format from QueryDict
                if isinstance(email_value, list) and email_value[0] == user.email:
                    data.pop('email')
                # Handle string format
                elif email_value == user.email:
                    data.pop('email')
                
            # Phone number check
            phone_value = data.get('phone_number')
            if phone_value:
                if isinstance(phone_value, list) and phone_value[0] == user.phone_number:
                    data.pop('phone_number')
                elif phone_value == user.phone_number:
                    data.pop('phone_number')
                
            # NID check
            nid_value = data.get('nid')
            if nid_value:
                if isinstance(nid_value, list) and nid_value[0] == user.nid:
                    data.pop('nid')
                elif nid_value == user.nid:
                    data.pop('nid')
            
            # Only update fields that are explicitly provided in request.data
            serializer = self.get_serializer(user, data=data, partial=True)
            
            if not serializer.is_valid():
                print(f"Serializer errors: {serializer.errors}")
                return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
            
            serializer.save()
            
            # Get updated user data for response
            updated_user = self.get_serializer(user)
            return Response(updated_user.data, status=status.HTTP_200_OK)
        except Exception as e:
            import traceback
            print(f"Error in update: {str(e)}")
            traceback.print_exc()
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class EmailExistsView(APIView):
    permission_classes = [AllowAny]
    
    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            required=['email'],
            properties={
                'email': openapi.Schema(type=openapi.TYPE_STRING, description='Email to check')
            }
        ),
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'exists': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether email exists')
                }
            ),
            400: 'Bad Request'
        }
    )
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

    @swagger_auto_schema(
        manual_parameters=[
            openapi.Parameter('email', openapi.IN_QUERY, description="Email to check", type=openapi.TYPE_STRING, required=True),
        ],
        responses={
            200: openapi.Schema(
                type=openapi.TYPE_OBJECT,
                properties={
                    'exists': openapi.Schema(type=openapi.TYPE_BOOLEAN, description='Whether email exists')
                }
            ),
            400: 'Bad Request'
        }
    )
    def get(self, request):
        # পূর্বের কোড...
        pass



User = get_user_model()

@api_view(['GET'])
def activate_user(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        return Response(
            {'message': 'Invalid activation link or user not found'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    if user.is_active:
        return Response(
            {'message': 'Account is already activated'}, 
            status=status.HTTP_200_OK
        )

    if email_verification_token.check_token(user, token):
        user.is_active = True
        user.save()
        return Response(
            {'message': 'Account activated successfully'}, 
            status=status.HTTP_200_OK
        )
    else:
        return Response(
            {'message': 'Invalid or expired activation link'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

@api_view(['POST'])
def resend_activation_email(request):
    email = request.data.get('email')
    if not email:
        return Response(
            {'message': 'Email is required'}, 
            status=status.HTTP_400_BAD_REQUEST
        )

    try:
        user = User.objects.get(email=email)
        if user.is_active:
            return Response(
                {'message': 'Account is already activated'}, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        current_site = get_current_site(request)
        send_activation_email(user, current_site)
        return Response(
            {'message': 'Activation email sent successfully'}, 
            status=status.HTTP_200_OK
        )
    except User.DoesNotExist:
        return Response(
            {'message': 'User not found'}, 
            status=status.HTTP_404_NOT_FOUND
        )