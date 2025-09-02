from django.contrib import admin
from django.db import transaction
from .models import Seller, Transaction, CreditRequest

@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ('name', 'credit')
    search_fields = ('name',)

@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ('seller', 'transaction_type', 'amount', 'timestamp')
    list_filter = ('transaction_type', 'seller')
    search_fields = ('seller__name',)

@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ('seller', 'amount', 'status', 'created_at')
    list_filter = ('status',)
    actions = ['approve_requests']

    @admin.action(description='تایید درخواست‌های انتخاب شده و افزایش اعتبار')
    def approve_requests(self, request, queryset):
        
        pending_requests = queryset.filter(status='PENDING')
        
        for req in pending_requests:
            try:
                
                with transaction.atomic():
                    
                    seller = Seller.objects.select_for_update().get(pk=req.seller.pk)
                    
                    seller.credit += req.amount
                    seller.save()
                    
                    Transaction.objects.create(
                        seller=seller,
                        amount=req.amount,
                        transaction_type='CREDIT_INCREASE',
                        description=f'Approved request ID: {req.id}'
                    )
                    
                    req.status = 'APPROVED'
                    req.save()

            except Exception as e:
                self.message_user(request, f"خطا در پردازش درخواست {req.id}: {e}", level='error')
        
        self.message_user(request, f"{pending_requests.count()} درخواست با موفقیت تایید شد.")












