from rest_framework import serializers
from .models import PaymentInstalment, SharePayment
from django.db.models import Sum

class PaymentInstalmentSerializer(serializers.ModelSerializer):
    shareholder_name = serializers.SerializerMethodField()
    shareholder_mobile_number = serializers.SerializerMethodField()

    class Meta:
        model = PaymentInstalment
        fields = ['id', 'shareholder', 'share_payment', 'payment_date', 'amount', 'status', 'paid_at', 'created_at', 'updated_at', 'shareholder_name','shareholder_mobile_number']

    def get_shareholder_name(self, obj):
        return obj.shareholder.name if obj.shareholder else None
    
    def get_shareholder_mobile_number(self, obj):
        return obj.shareholder.mobile_number if obj.shareholder else None
    
class SharePaymentSerializer(serializers.ModelSerializer):
    total_paid_amount = serializers.SerializerMethodField()

    class Meta:
        model = SharePayment
        fields = ['shareholder', 'duration', 'annual_amount', 'instalment_type', 'start_date', 'status', 'payment_mode', 'staff_name','total_paid_amount']
       
    def get_total_paid_amount(self, obj):
        total_paid_amount = PaymentInstalment.objects.filter(share_payment=obj, status=1).aggregate(total_paid=Sum('amount'))['total_paid']
        return total_paid_amount
