from django.urls import include, path
from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('ride',views.RideViewset)
router.register('vehicle-make',views.VehicleMakeViewset)
router.register('vehicle-model',views.VehicleModelViewset)
router.register('vehicle',views.VehicleViewset)
urlpatterns = [
    path('', include(router.urls)),
]