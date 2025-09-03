from django.db import transaction
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Seller, Transaction
from .serializers import TopUpSerializer


class TopUpAPIView(APIView):
    def post(self, request, *args, **kwargs):
        serializer = TopUpSerializer(data=request.data)

    
        if not serializer.is_valid():
            print("Serializer Errors:", serializer.errors)
            return Response(
                serializer.errors, 
                status=status.HTTP_400_BAD_REQUEST
            )
        
        validated_data = serializer.validated_data
        seller_id = validated_data['seller_id']
        amount = validated_data['amount']
        phone_number = validated_data['phone_number']

        try:
            with transaction.atomic():

                seller = Seller.objects.select_for_update().get(pk=seller_id)
                
                if seller.credit < amount:
                    return Response(
                        {"error": "اعتبار کافی نیست."}, 
                        status=status.HTTP_400_BAD_REQUEST
                    )
                
                seller.credit -= amount
                seller.save()
                
                Transaction.objects.create(
                    seller=seller,
                    amount=-amount,
                    transaction_type='TOPUP_SALE',
                    description=f"شارژ برای شماره {phone_number}"
                )
            
            return Response(
                {
                    "message": "شارژ با موفقیت انجام شد.", 
                    "remaining_credit": seller.credit
                },
                status=status.HTTP_200_OK
            )
            
        except Seller.DoesNotExist:
            return Response(
                {"error": "فروشنده یافت نشد."}, 
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            
            print(f"An unexpected error occurred: {e}")
            return Response(
                {"error": str(e)}, 
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )