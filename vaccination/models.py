from django.db import models
from users.models import User 
from datetime import timedelta
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from cloudinary.models import CloudinaryField


class Vaccine(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2) 
    stock = models.PositiveBigIntegerField(default=0)
    manufacturer = models.CharField(max_length=255, blank=True, null=True)
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role__in': ['doctor', 'admin']})

    def __str__(self):
        return f"{self.name}"

class VaccineImage(models.Model):
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE, related_name='images')
    image = CloudinaryField('image')

    

class VaccineCampaign(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    location = models.CharField(max_length=255, blank=True, null=True)
    start_date = models.DateField()
    end_date = models.DateField()
    vaccines = models.ManyToManyField('Vaccine')  

    def __str__(self):
        return self.name

class VaccinationSchedule(models.Model):
    vaccine = models.ForeignKey(Vaccine, on_delete=models.CASCADE)
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    dose_dates = models.JSONField(default=list,null=True, blank=True) 
    created_at = models.DateTimeField(auto_now_add=True)
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE,null=True, blank=True) 
    
    PAYMENT_METHOD_CHOICES = [
    ('online', 'Online Payment'),
    ('cod', 'Cash on Delivery'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES, default='cod')
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')

    def save(self, *args, **kwargs):
        if not self.dose_dates:
            # Simply set the current date as the vaccination date
            self.dose_dates = [timezone.now().strftime('%Y-%m-%dT%H:%M:%S')]

        super(VaccinationSchedule, self).save(*args, **kwargs)

    def __str__(self):
        return f"{self.patient.first_name} - {self.vaccine.name} - {self.payment_method}"


class VaccineReview(models.Model):
    patient = models.ForeignKey(User, on_delete=models.CASCADE, limit_choices_to={'role': 'patient'})
    campaign = models.ForeignKey(VaccineCampaign, on_delete=models.CASCADE)  
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)]) 
    comment = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Review by {self.patient.first_name} for {self.campaign.name}"


class Payment(models.Model):
    PAYMENT_METHOD_CHOICES = [
        ('online', 'Online Payment'),
        ('cod', 'Cash on Delivery'),
    ]
    PAYMENT_STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
    ]
    
    schedule = models.ForeignKey(VaccinationSchedule, on_delete=models.CASCADE)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=10, choices=PAYMENT_METHOD_CHOICES)
    payment_status = models.CharField(max_length=10, choices=PAYMENT_STATUS_CHOICES, default='pending')
    transaction_id = models.CharField(max_length=255, blank=True, null=True)  
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment for {self.schedule.patient.username} - {self.amount} - {self.payment_method}"