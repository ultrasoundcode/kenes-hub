import django_filters
from django.contrib.auth import get_user_model
from .models import Application

User = get_user_model()


class ApplicationFilter(django_filters.FilterSet):
    status = django_filters.CharFilter(field_name='status')
    application_type = django_filters.CharFilter(field_name='application_type')
    source = django_filters.CharFilter(field_name='source')
    applicant = django_filters.NumberFilter(field_name='applicant__id')
    assigned_to = django_filters.NumberFilter(field_name='assigned_to__id')
    created_after = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='gte')
    created_before = django_filters.DateTimeFilter(field_name='created_at', lookup_expr='lte')
    search = django_filters.CharFilter(method='filter_search')

    class Meta:
        model = Application
        fields = ['status', 'application_type', 'source', 'applicant', 'assigned_to']

    def filter_search(self, queryset, name, value):
        return queryset.filter(
            django_filters.Q(subject__icontains=value) |
            django_filters.Q(description__icontains=value) |
            django_filters.Q(number__icontains=value) |
            django_filters.Q(applicant__first_name__icontains=value) |
            django_filters.Q(applicant__last_name__icontains=value) |
            django_filters.Q(creditor_name__icontains=value)
        )