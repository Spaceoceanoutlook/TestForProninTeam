from rest_framework import serializers
from .models import Collect
from payments.serializers import PaymentSerializer
from django.utils import timezone

class CollectSerializer(serializers.ModelSerializer):
    current_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    end_datetime = serializers.DateTimeField(
        required=True,
        format="%Y-%m-%dT%H:%M:%SZ",
        input_formats=["%Y-%m-%dT%H:%M:%SZ", "iso-8601"]
    )

    class Meta:
        model = Collect
        fields = ['id', 'title', 'author', 'target_amount', 'current_amount',
                  'contributors_count', 'end_datetime']
        read_only_fields = ('current_amount', 'contributors_count', 'author')

    def validate_end_datetime(self, value):
        """Проверка, что дата завершения в будущем"""
        if value <= timezone.now():
            raise serializers.ValidationError("Дата завершения должна быть в будущем.")
        return value

class CollectDetailSerializer(CollectSerializer):
    payments = serializers.SerializerMethodField()

    class Meta(CollectSerializer.Meta):
        fields = CollectSerializer.Meta.fields + [
            'payments', 'description', 'reason', 'cover_image'
        ]

    def get_payments(self, obj):
        payments = obj.payments.all()
        return PaymentSerializer(payments, many=True, context=self.context).data
