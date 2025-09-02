import threading
from decimal import Decimal
from django.test import TestCase
from django.db import connection
from recharge.models import Seller, Transaction

class AccountingIntegrityTests(TestCase):
    
    def setUp(self):
        self.seller1 = Seller.objects.create(name='Seller One', credit=Decimal('1000000.00'))
        self.seller2 = Seller.objects.create(name='Seller Two', credit=Decimal('500000.00'))

    def test_simple_accounting_flow(self):
       
        print("\nRunning Simple Accounting Test...")
        total_credit_added = Decimal('0.00')
        for i in range(10):
            amount = Decimal(f'{10000 * (i+1)}.00')
            self.seller1.credit += amount
            total_credit_added += amount
            Transaction.objects.create(seller=self.seller1, amount=amount, transaction_type='CREDIT_INCREASE')
        
        self.seller1.save()
        self.seller1.refresh_from_db()
        
    
        total_sales = Decimal('0.00')
        sale_amount = Decimal('5000.00')
        for _ in range(1000):
            self.client.post('/api/top-up/', {
                'seller_id': self.seller1.id,
                'phone_number': '09123456789',
                'amount': sale_amount
            }, content_type='application/json')
            total_sales += sale_amount

        self.seller1.refresh_from_db()
        
        expected_final_credit = Decimal('1000000.00') + total_credit_added - total_sales
    
        self.assertEqual(self.seller1.credit, expected_final_credit)
        
       
        transaction_sum = sum(t.amount for t in self.seller1.transactions.all())
        final_credit_from_transactions = Decimal('1000000.00') + transaction_sum 
        self.assertEqual(self.seller1.credit, final_credit_from_transactions)
        print("Simple Accounting Test Passed!")
 
    def test_concurrent_top_up(self):
    
        print("\nRunning Parallel Load Test...")
        initial_credit = self.seller2.credit
        num_threads = 100
        sale_amount = Decimal('100.00')

        
        def make_request():
            connection.close() 
            self.client.post('/api/top-up/', {
                'seller_id': self.seller2.id,
                'phone_number': '09120000000',
                'amount': sale_amount
            }, content_type='application/json')

        threads = []
        for _ in range(num_threads):
            thread = threading.Thread(target=make_request)
            threads.append(thread)
            thread.start()

        for thread in threads:
            thread.join()

        self.seller2.refresh_from_db()
        
        expected_final_credit = initial_credit - (num_threads * sale_amount)
        final_transaction_count = Transaction.objects.filter(seller=self.seller2, transaction_type='TOPUP_SALE').count()

        self.assertEqual(self.seller2.credit, expected_final_credit)
        self.assertEqual(final_transaction_count, num_threads)
        print("Parallel Load Test Passed! Final credit is accurate.")