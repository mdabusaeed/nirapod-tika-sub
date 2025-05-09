from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import  IsAdminUser
from .models import Vaccine, VaccinationSchedule, VaccineReview, VaccineCampaign, Payment
from .serializers import VaccineSerializer, VaccinationScheduleSerializer, VaccineReviewSerializer, VaccineCampaignSerializer
from django.conf import settings
from .models import VaccineImage
from django.db import transaction

class VaccineViewSet(ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer

    def create(self, request, *args, **kwargs):
        try:
            print("\n\n==== VACCINE CREATE ====")
            print(f"User: {request.user.username}, Role: {request.user.role}")
            print(f"Request data: {request.data}")
            print(f"Request FILES: {request.FILES}")
            
            # সব মডেলের জরুরি ফিল্ডগুলি নিশ্চিত করি
            data = request.data.copy()
            if 'stock' not in data or data['stock'] is None:
                data['stock'] = 0
                print("Setting default stock to 0")
            
            # সাধারণ মেথড ব্যবহার করি
            serializer = self.get_serializer(data=data)
            print(f"Serializer data before validation: {serializer.initial_data}")
            serializer.is_valid(raise_exception=True)
            print(f"Serializer valid data: {serializer.validated_data}")
            self.perform_create(serializer)
            headers = self.get_success_headers(serializer.data)
            return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)
        except Exception as e:
            print(f"\n\nERROR in create: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    def perform_create(self, serializer):
        try:
            print("Starting perform_create in VaccineViewSet")
            print(f"User role: {self.request.user.role}")
            
            if self.request.user.role not in ['doctor', 'admin']:
                raise PermissionDenied("Only doctors and admins can add vaccines.")
            
            with transaction.atomic():
                print("Creating vaccine...")
                vaccine = serializer.save(created_by=self.request.user)
                print(f"Vaccine created with ID: {vaccine.id}")
                
                images = self.request.FILES.getlist('images')
                print(f"Found {len(images)} images")
                
                for image in images:
                    print(f"Creating image for {vaccine.name}")
                    VaccineImage.objects.create(vaccine=vaccine, image=image)
                print("Vaccine creation completed successfully")
        except Exception as e:
            print(f"ERROR in perform_create: {str(e)}")
            raise

class VaccinationScheduleViewSet(ModelViewSet):
    serializer_class = VaccinationScheduleSerializer

    def get_queryset(self):

        user = self.request.user
        if user.role == 'doctor':
            return VaccinationSchedule.objects.all()  
        return VaccinationSchedule.objects.filter(patient=user)  

    def create(self, request, *args, **kwargs):

        patient = request.user
        vaccine_id = request.data.get('vaccine')
        dose_dates = request.data.get('dose_dates')
        payment_method = request.data.get('payment_method')

        vaccine = Vaccine.objects.get(id=vaccine_id)

        schedule = VaccinationSchedule.objects.create(
            patient=patient,
            vaccine=vaccine,
            dose_dates=dose_dates,
            payment_method=payment_method,
            status='pending' if payment_method == 'online' else 'confirmed'
        )

        # ডামি পেমেন্ট রেকর্ড তৈরি
        payment = Payment.objects.create(
            schedule=schedule,
            amount=vaccine.price,
            payment_method=payment_method,
            payment_status='pending' if payment_method == 'online' else 'completed',
            transaction_id=f"dummy_{schedule.id}"  # ডামি ট্রানজেকশন আইডি
        )

        return Response({
            "message": "Schedule created successfully",
            "schedule_id": schedule.id,
            "payment_status": payment.payment_status,
            "next_step": "Confirm payment from frontend" if payment_method == 'online' else "Booking confirmed"
        }, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        user = self.request.user
        if user.role != 'doctor':
            return Response({"error": "Only doctors can modify schedules."}, status=status.HTTP_403_FORBIDDEN)
        return super().update(request, *args, **kwargs)


class PatientVaccinationHistoryViewSet(ModelViewSet):
    queryset = VaccinationSchedule.objects.all()
    serializer_class = VaccinationScheduleSerializer

    def get_queryset(self):
        return VaccinationSchedule.objects.filter(patient=self.request.user)
    

class VaccineReviewViewSet(ModelViewSet):
    serializer_class = VaccineReviewSerializer

    def get_queryset(self):
        return VaccineReview.objects.all() 

    def perform_create(self, serializer):
        serializer.save(patient=self.request.user)

    def update(self, request, *args, **kwargs):
        review = self.get_object()
        if review.patient != request.user:
            return Response({"error": "You can only update your own review."}, status=status.HTTP_403_FORBIDDEN)

        return super().update(request, *args, **kwargs)

class VaccineCampaignViewSet(ModelViewSet):
    queryset = VaccineCampaign.objects.all()
    serializer_class = VaccineCampaignSerializer
    
    def get_permissions(self):
        if self.action in ['create', 'update', 'partial_update', 'destroy']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

class DebugApiView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        try:
            print("DEBUG API VIEW")
            print(f"User: {request.user.username}, Role: {request.user.role}")
            print(f"Request data: {request.data}")
            print(f"Request FILES: {request.FILES}")
            
            # যদি ভ্যাকসিন তৈরি করতে হয়
            if request.data.get('debug_type') == 'create_vaccine':
                vaccine = Vaccine.objects.create(
                    name=request.data.get('name'),
                    price=request.data.get('price'),
                    manufacturer=request.data.get('manufacturer'),
                    stock=request.data.get('stock', 100),
                    created_by=request.user
                )
                print(f"Created vaccine: {vaccine.id} - {vaccine.name}")
                
                # ইমেজ হ্যান্ডলিং
                images = request.FILES.getlist('images')
                for image in images:
                    print(f"Creating image for {vaccine.name}")
                    img = VaccineImage.objects.create(vaccine=vaccine, image=image)
                    print(f"Created image: {img.id}")
                
                return Response({
                    "success": True,
                    "message": "Vaccine created successfully for debugging",
                    "vaccine_id": vaccine.id
                })
            
            return Response({
                "success": True,
                "message": "Debug request received",
                "data": request.data
            })
            
        except Exception as e:
            print(f"ERROR in debug view: {str(e)}")
            import traceback
            traceback.print_exc()
            return Response({
                "success": False,
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


