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

    def validate(self, data):
        """
        Check that the dose_intervals and doses_required are consistent.
        """
        try:
            print(f"Validating data: {data}")
            dose_intervals = data.get('dose_intervals', [])
            doses_required = data.get('doses_required', 1)
            
            print(f"Validating: dose_intervals={dose_intervals}, doses_required={doses_required}")
            
            if doses_required > 1 and len(dose_intervals) != doses_required - 1:
                msg = f"Dose intervals must have exactly doses_required - 1 entries. Got {len(dose_intervals)} intervals but need {doses_required - 1}."
                print(f"Serializer validation error: {msg}")
                raise serializers.ValidationError(msg)
                
            return data
            
        except Exception as e:
            print(f"Error in validate method: {str(e)}")
            raise


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
    vaccines = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Vaccine.objects.all(),
        write_only=True  # POST-এ IDs গ্রহণ করবে
    )
    vaccine_names = serializers.SerializerMethodField(read_only=True)  # GET-এ names ফেরত দেবে

    class Meta:
        model = VaccineCampaign
        fields = ['id', 'name', 'description', 'location', 'start_date', 'end_date', 'vaccines', 'vaccine_names']

    def get_vaccine_names(self, obj):
        return [vaccine.name for vaccine in obj.vaccines.all()]

    def to_representation(self, instance):
        # GET রিকোয়েস্টে 'vaccines' ফিল্ডকে 'vaccine_names' দিয়ে রিপ্লেস করো
        ret = super().to_representation(instance)
        ret['vaccines'] = ret.pop('vaccine_names')
        return ret
    
    