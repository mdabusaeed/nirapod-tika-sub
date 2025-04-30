from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserProfileView
from vaccination.views import VaccineViewSet, VaccinationScheduleViewSet, VaccineReviewViewSet, VaccineCampaignViewSet
from users.views import UserProfileView,DoctorProfileView, EmailExistsView
from order.views import OrderViewSet, CartViewSet, CartItemViewSet    
from users.views import resend_activation_email, activate_user

router = routers.DefaultRouter()
router.register('patient-profile', UserProfileView, basename='patient-profile')
router.register('doctor-profile', DoctorProfileView, basename='doctor-profile')
router.register('vaccines', VaccineViewSet, basename = 'vaccines')
router.register('vaccination-schedules', VaccinationScheduleViewSet, basename = 'vaccination-schedules' )
router.register('review', VaccineReviewViewSet, basename='review')
router.register('vaccine-campaign', VaccineCampaignViewSet, basename='vaccine-campaign')
router.register('order', OrderViewSet, basename='order')
router.register('carts', CartViewSet, basename='carts')

product_router = routers.NestedDefaultRouter(router, 'vaccines', lookup='vaccines')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-item')



urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(carts_router.urls)),
    path('auth/', include('djoser.urls')),  
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls.jwt')),
    path('check-email/', EmailExistsView.as_view(), name='check-email'),
    path('activate/<str:uidb64>/<str:token>/', activate_user, name='activate_user'),
    path('resend-activation/', resend_activation_email, name='resend_activation_email'),    
]