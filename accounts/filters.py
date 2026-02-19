import django_filters
from django.contrib.auth import get_user_model

User = get_user_model()


class UserFilter(django_filters.FilterSet):
    # filtros exatos
    is_active = django_filters.BooleanFilter(field_name="is_active")
    is_staff = django_filters.BooleanFilter(field_name="is_staff")

    # filtros por data
    date_joined_after = django_filters.DateTimeFilter(field_name="date_joined", lookup_expr="gte")
    date_joined_before = django_filters.DateTimeFilter(field_name="date_joined", lookup_expr="lte")

    # filtros texto (parciais)
    email = django_filters.CharFilter(field_name="email", lookup_expr="icontains")
    username = django_filters.CharFilter(field_name="username", lookup_expr="icontains")

    class Meta:
        model = User
        fields = [
            "is_active",
            "is_staff",
            "email",
            "username",
            "date_joined_after",
            "date_joined_before",
        ]
