from rest_framework.exceptions import PermissionDenied
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import  IsAdminUser
from .models import Vaccine, VaccinationSchedule, VaccineReview, VaccineCampaign, Payment
from .serializers import VaccineSerializer, VaccinationScheduleSerializer, VaccineReviewSerializer, VaccineCampaignSerializer
import stripe
from django.conf import settings
stripe.api_key = settings.STRIPE_TEST_SECRET_KEY

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
            payment_method=payment_method
        )

        amount = vaccine.price  

        if payment_method == 'online':
            try:
                payment_intent = stripe.PaymentIntent.create(
                    amount=amount * 100, 
                    currency="usd",
                    metadata={"integration_check": "accept_a_payment"}
                )

                payment = Payment.objects.create(
                    schedule=schedule,
                    amount=amount,
                    payment_method='online',
                    payment_status='pending',
                    transaction_id=payment_intent.id
                )

                return Response({
                    "client_secret": payment_intent.client_secret
                }, status=status.HTTP_200_OK)

            except stripe.error.StripeError as e:
                return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        else:
            payment = Payment.objects.create(
                schedule=schedule,
                amount=amount,  
                payment_method='cod',
                payment_status='completed',  
            )
            return Response({"message": "Booking confirmed with Cash on Delivery"}, status=status.HTTP_200_OK)

    def update(self, request, *args, **kwargs):

        user = self.request.user
        if user.role != 'doctor':
            return Response({"error": "Only doctors can modify vaccine schedules."}, status=status.HTTP_403_FORBIDDEN)

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