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

class VaccineViewSet(ModelViewSet):
    queryset = Vaccine.objects.all()
    serializer_class = VaccineSerializer

    def perform_create(self, serializer):
        if self.request.user.role != 'doctor':
            raise PermissionDenied("Only doctors can add vaccines.")
        serializer.save(created_by=self.request.user)  

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
    permission_classes = [IsAdminUser]