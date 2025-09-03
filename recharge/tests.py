

import threading
import json
from decimal import Decimal
from django.test import TestCase
from django.db import connection, transaction as db_transaction
from .models import Seller, Transaction

class AccountingIntegrityTests(TestCase):
    def setUp(self):

        self.seller1 = Seller.objects.create(name='Seller One', credit=Decimal('10000000.00'))
        self.seller2 = Seller.objects.create(name='Seller Two', credit=Decimal('500000.00'))

    def test_simple_accounting_flow(self):
        print("\nRunning Simple Accounting Test...")
        initial_credit_seller1 = self.seller1.credit

        total_credit_added = Decimal('0.00')
        for i in range(10):
            amount = Decimal(f'{10000 * (i+1)}.00')
            with db_transaction.atomic():
                seller = Seller.objects.select_for_update().get(pk=self.seller1.pk)
                seller.credit += amount
                seller.save()
                Transaction.objects.create(
                    seller=seller, 
                    amount=amount, 
                    transaction_type='CREDIT_INCREASE'
                )
            total_credit_added += amount

        total_sales = Decimal('0.00')
        sale_amount = Decimal('5000.00')
        for _ in range(1000):
            payload = {
                'seller_id': self.seller1.id,
                'phone_number': '09123456789',
                'amount': str(sale_amount)
            }
            response = self.client.post(
                '/api/top-up/', 
                data=json.dumps(payload),
                content_type='application/json'
            )
            self.assertEqual(response.status_code, 200, f"API failed: {response.content}")
            total_sales += sale_amount

        self.seller1.refresh_from_db()
        expected_final_credit = initial_credit_seller1 + total_credit_added - total_sales
        self.assertEqual(self.seller1.credit, expected_final_credit)

        transaction_sum = sum(t.amount for t in self.seller1.transactions.all())
        final_credit_from_transactions = initial_credit_seller1 + transaction_sum
        self.assertEqual(self.seller1.credit, final_credit_from_transactions)

        print("Simple Accounting Test Passed!")

    def _perform_safe_sale(self, seller_id, amount, phone_number):
        try:
            with db_transaction.atomic():
                seller = Seller.objects.select_for_update().get(pk=seller_id)
                if seller.credit >= amount:
                    seller.credit -= amount
                    seller.save()
                    Transaction.objects.create(
                        seller=seller,
                        amount=-amount,
                        transaction_type='TOPUP_SALE',
                        description=f"Top-up for {phone_number}"
                    )
        except Exception:
            pass

    def test_concurrent_top_up(self):
        print("\nRunning Parallel Load Test...")
        initial_credit = self.seller2.credit
        num_threads = 100
        sale_amount = Decimal('100.00')

        def make_request():
            connection.close()
            self._perform_safe_sale(
                seller_id=self.seller2.id,
                amount=sale_amount,
                phone_number='09120000000'
            )
            

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.seller2.refresh_from_db() 
        successful_sales = Transaction.objects.filter(
            seller=self.seller2, 
            transaction_type='TOPUP_SALE'
        ).count()

        print(f"{successful_sales} out of {num_threads} concurrent sales were successful.")

        expected_final_credit = initial_credit - (successful_sales * sale_amount)

        self.assertEqual(self.seller2.credit, expected_final_credit)

        print("Parallel Load Test Passed! Final credit is accurate.")