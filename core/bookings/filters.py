import django_filters

from .models import Booking


class BookingsFilter(django_filters.FilterSet):
    boarding_point = django_filters.CharFilter(field_name='boarding_point',lookup_expr='iexact')
    dropping_point = django_filters.CharFilter(field_name='dropping_point',lookup_expr='iexact')
    status = django_filters.CharFilter(field_name='status',lookup_expr='iexact')
    class Meta:
        model = Booking
        fields = ['boarding_point','dropping_point','status']