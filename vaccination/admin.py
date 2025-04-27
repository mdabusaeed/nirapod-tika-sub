from django.contrib import admin
from vaccination.models import Vaccine, VaccineImage, VaccineReview, VaccineCampaign, VaccinationSchedule


# Register your models here.

admin.site.register(Vaccine)
admin.site.register(VaccineImage)
admin.site.register(VaccineReview)
admin.site.register(VaccineCampaign)
admin.site.register(VaccinationSchedule)

