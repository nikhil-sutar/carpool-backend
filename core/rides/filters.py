import django_filters

from .models import Ride


class RideFilter(django_filters.FilterSet):
    source = django_filters.CharFilter(field_name='source',lookup_expr='iexact')
    destination = django_filters.CharFilter(field_name='destination',lookup_expr='iexact')
    date = django_filters.DateFilter(field_name='start_time',lookup_expr='date')
    class Meta:
        model = Ride
        fields = ['source','destination','date']