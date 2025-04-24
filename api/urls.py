from django.urls import path, include
from rest_framework_nested import routers
from users.views import UserProfileView
from vaccination.views import VaccineViewSet, VaccinationScheduleViewSet, VaccineReviewViewSet, VaccineCampaignViewSet
from users.views import UserProfileView,DoctorProfileView
from order.views import OrderViewSet, CartViewSet, CartItemViewSet    

router = routers.DefaultRouter()
router.register('patient-profile', UserProfileView, basename='patient-profile')
router.register('doctor-profile', DoctorProfileView, basename='doctor-profile')
router.register('vaccines', VaccineViewSet, basename = 'vaccine')
router.register('vaccination-schedules', VaccinationScheduleViewSet, basename = 'vaccination-schedules' )
router.register('review', VaccineReviewViewSet, basename='review')
router.register('vaccine-campaign', VaccineCampaignViewSet, basename='vaccine-campaign')
router.register('order', OrderViewSet, basename='order')
router.register('cart', CartViewSet, basename='cart')

product_router = routers.NestedDefaultRouter(router, 'vaccine', lookup='vaccine')

carts_router = routers.NestedDefaultRouter(router, 'carts', lookup='cart')
carts_router.register('items', CartItemViewSet, basename='cart-item')


urlpatterns = [
    path('', include(router.urls)),
    path('', include(product_router.urls)),
    path('', include(carts_router.urls)),
    path('auth/', include('djoser.urls')),  
    path('auth/', include('djoser.urls.authtoken')),
    path('auth/', include('djoser.urls')),
    path('auth/', include('djoser.urls.jwt')),

]