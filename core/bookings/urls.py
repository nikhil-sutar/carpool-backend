from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import BookingViewSet, PaymentViewSet

router = DefaultRouter()
router.register('bookings',BookingViewSet)
router.register('payments',PaymentViewSet)

urlpatterns = [
    path('', include(router.urls)),
]