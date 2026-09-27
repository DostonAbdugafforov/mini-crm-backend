import django_filters

from .models import Lead, LeadSource, LeadStatus


class LeadFilter(django_filters.FilterSet):
    status = django_filters.ChoiceFilter(choices=LeadStatus.choices)
    source = django_filters.ChoiceFilter(choices=LeadSource.choices)
    created_after = django_filters.DateFilter(field_name="created_at", lookup_expr="gte")
    created_before = django_filters.DateFilter(field_name="created_at", lookup_expr="lte")

    class Meta:
        model = Lead
        fields = ["status", "source", "created_after", "created_before"]