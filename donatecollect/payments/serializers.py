from decimal import Decimal
from rest_framework import serializers
from .models import Payment
from collects.models import Collect

class PaymentSerializer(serializers.ModelSerializer):
    amount = serializers.DecimalField(
        max_digits=10,
        decimal_places=2,
        min_value=Decimal('0.01')
    )
    user = serializers.HiddenField(
        default=serializers.CurrentUserDefault()
    )
    user_name = serializers.CharField(source='user.username', read_only=True)

    class Meta:
        model = Payment
        fields = ['id', 'user', 'user_name', 'amount', 'created_at']
        read_only_fields = ('user_name', 'created_at')
        extra_kwargs = {
            'collect': {'queryset': Collect.objects.select_related('author')}
        }