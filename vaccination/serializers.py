from rest_framework import serializers
from .models import Vaccine, VaccineReview, VaccineCampaign, VaccinationSchedule, VaccineImage


class VaccinationImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineImage
        fields = ['id', 'image']

class VaccineSerializer(serializers.ModelSerializer):
    created_by = serializers.StringRelatedField() 
    images = VaccinationImageSerializer(many=True, read_only=True)
    class Meta:
        model = Vaccine
        fields = ['id', 'name','price', 'manufacturer', 'dose_intervals', 'doses_required','created_by', "images"]
        # read_only_fields = ['created_by']  


class VaccinationScheduleSerializer(serializers.ModelSerializer):
    vaccine_name = serializers.CharField(source='vaccine.name', read_only=True)
    dose_dates = serializers.ListField(child=serializers.DateField(), required=False)  

    class Meta:
        model = VaccinationSchedule
        fields = ['id', 'patient', 'vaccine', 'campaign',"payment_method", 'vaccine_name', 'dose_dates']
        extra_kwargs = {'patient': {'read_only': True}}  

    def create(self, validated_data):

        validated_data['patient'] = self.context['request'].user
        return super().create(validated_data)

    def update(self, instance, validated_data):

        request = self.context['request']
        if request.user.role != 'doctor': 
            raise serializers.ValidationError("Only doctors can modify the booking schedule.")

        instance.dose_dates = validated_data.get('dose_dates', instance.dose_dates)
        instance.save()
        return instance
    
    def validate(self, data):
        """
        Validate that the campaign is available in the vaccination schedule.
        """
        patient = self.context['request'].user
        campaign = data.get('campaign')
        vaccination_schedule = data.get('vaccination_schedule')

        if vaccination_schedule and vaccination_schedule.campaign != campaign:
            raise serializers.ValidationError("The selected vaccination schedule is not available for this campaign.")

        booking_exists = VaccinationSchedule.objects.filter(patient=patient, campaign=campaign).exists()
        if booking_exists:
            raise serializers.ValidationError("You already have a booking for this campaign.")

        return data
    
class VaccineReviewSerializer(serializers.ModelSerializer):
    patient_name = serializers.CharField(source='patient.first_name', read_only=True)
    campaign_name = serializers.CharField(source='campaign.name', read_only=True)

    class Meta:
        model = VaccineReview
        fields = ['id', 'patient', 'patient_name', 'campaign', 'campaign_name', 'rating', 'comment', 'created_at']
        extra_kwargs = {'patient': {'read_only': True}}

    def validate(self, data):

        request = self.context['request']
        patient = request.user
        campaign = data.get('campaign')

        booking_exists = VaccinationSchedule.objects.filter(patient=patient, campaign=campaign).exists()
        if not booking_exists:
            raise serializers.ValidationError("You cannot review this campaign because you have not booked any vaccine from it.")

        return data

class VaccineCampaignSerializer(serializers.ModelSerializer):
    class Meta:
        model = VaccineCampaign
        fields = ['id', 'name', 'description', 'start_date', 'end_date', 'vaccines', 'images']

  