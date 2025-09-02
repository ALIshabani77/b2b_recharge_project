from django.db import models

class Seller(models.Model):
    name = models.CharField(max_length=100, unique=True, verbose_name="نام فروشنده")
    credit = models.DecimalField(max_digits=12, decimal_places=2, default=0, verbose_name="اعتبار")

    def __str__(self):
        return f"{self.name} - Credit: {self.credit}"

    class Meta:
        verbose_name = "فروشنده"
        verbose_name_plural = "فروشندگان"


class Transaction(models.Model):
    TRANSACTION_TYPES = (
        ('CREDIT_INCREASE', 'افزایش اعتبار'),
        ('TOPUP_SALE', 'فروش شارژ'),
    )
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='transactions', verbose_name="فروشنده")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ تراکنش")
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES, verbose_name="نوع تراکنش")
    timestamp = models.DateTimeField(auto_now_add=True, verbose_name="زمان تراکنش")
    description = models.TextField(blank=True, null=True, verbose_name="توضیحات")

    def __str__(self):
        return f"{self.seller.name} | {self.get_transaction_type_display()} | {self.amount}"

    class Meta:
        verbose_name = "تراکنش"
        verbose_name_plural = "تراکنش‌ها"
        ordering = ['-timestamp']


class CreditRequest(models.Model):

    STATUS_CHOICES = (
        ('PENDING', 'در انتظار'),
        ('APPROVED', 'تایید شده'),
        ('REJECTED', 'رد شده'),
    )
    
    seller = models.ForeignKey(Seller, on_delete=models.CASCADE, related_name='credit_requests', verbose_name="فروشنده")
    amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name="مبلغ درخواستی")
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='PENDING', verbose_name="وضعیت")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="زمان ایجاد")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="زمان به‌روزرسانی")
    
    def __str__(self):
        return f"Request by {self.seller.name} for {self.amount} - Status: {self.status}"

    class Meta:
        verbose_name = "درخواست اعتبار"
        verbose_name_plural = "درخواست‌های اعتبار"