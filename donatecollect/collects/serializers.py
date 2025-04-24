from rest_framework import serializers
from .models import Collect
from payments.serializers import PaymentSerializer

class CollectSerializer(serializers.ModelSerializer):
    current_amount = serializers.DecimalField(
        max_digits=12,
        decimal_places=2,
        read_only=True
    )
    
    class Meta:
        model = Collect
        fields = ['id', 'title', 'author', 'target_amount', 'current_amount', 'contributors_count']
        read_only_fields = ('current_amount', 'contributors_count', 'author')

class CollectDetailSerializer(CollectSerializer):
    payments = serializers.SerializerMethodField()
    
    class Meta(CollectSerializer.Meta):
        fields = CollectSerializer.Meta.fields + [
            'payments', 'description', 'reason', 
            'target_amount', 'end_datetime'
        ]
    
    def get_payments(self, obj):
        payments = obj.payments.all()[:10]
        return PaymentSerializer(payments, many=True).data
