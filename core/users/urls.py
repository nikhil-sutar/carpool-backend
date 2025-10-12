from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('profile',views.ProfileViewset)
router.register('driver-profile',views.DriverProfileViewset)
router.register('passenger-profile',views.PassengerProfileViewset)
router.register('driver-documents',views.DriverDocumentViewset)
router.register('driver-verification',views.DriverVerificationViewset)
router.register('driver-verification-requests',views.DriverVerificationAdminViewset,basename="driver-verification-approval")
urlpatterns = [
    path('register/', views.UserListCreateAPIView.as_view(), name = 'register'),
    path('', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)