from rest_framework import serializers

class TopUpSerializer(serializers.Serializer):
    
    seller_id = serializers.IntegerField(required=True)
    phone_number = serializers.CharField(max_length=20, required=True)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2, required=True)

    def validate_amount(self, value):
        if value <= 0:
            raise serializers.ValidationError("مبلغ شارژ باید بزرگتر از صفر باشد.")
        return value