"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for transaction_filter module
"""

import unittest
from datetime import datetime

from transaction import Transaction
from transaction_filter import TransactionFilter


class TestTransactionFilter(unittest.TestCase):
    """Test cases for TransactionFilter class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='Groceries Store',
                amount=100.00,
                category='Groceries'
            ),
            Transaction(
                date=datetime(2025, 1, 20),
                account_type='visa',
                description='Restaurant ABC',
                amount=50.00,
                category='Restaurants'
            ),
            Transaction(
                date=datetime(2025, 2, 10),
                account_type='chequing',
                description='Gas Station',
                amount=75.00,
                category='Gas/Transportation'
            )
        ]
    
    def test_filter_by_category(self):
        """Test filtering by category."""
        filtered = TransactionFilter.filter_by_category(self.transactions, 'Groceries')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].category, 'Groceries')
    
    def test_filter_by_account_type(self):
        """Test filtering by account type."""
        filtered = TransactionFilter.filter_by_account_type(self.transactions, 'visa')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].account_type, 'visa')
    
    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        filtered = TransactionFilter.filter_by_date_range(
            self.transactions, start_date, end_date
        )
        self.assertEqual(len(filtered), 2)
    
    def test_filter_by_amount_range(self):
        """Test filtering by amount range."""
        filtered = TransactionFilter.filter_by_amount_range(
            self.transactions, min_amount=60.00, max_amount=100.00
        )
        self.assertEqual(len(filtered), 2)
    
    def test_filter_by_merchant(self):
        """Test filtering by merchant name."""
        filtered = TransactionFilter.filter_by_merchant(self.transactions, 'Restaurant')
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0].description, 'Restaurant ABC')
    
    def test_search_by_keyword(self):
        """Test searching by keyword."""
        filtered = TransactionFilter.search_by_keyword(self.transactions, 'Store')
        self.assertEqual(len(filtered), 1)
    
    def test_filter_all(self):
        """Test applying all filters."""
        filtered = TransactionFilter.filter_all(
            self.transactions,
            category='Groceries',
            start_date=datetime(2025, 1, 1),
            end_date=datetime(2025, 1, 31)
        )
        self.assertEqual(len(filtered), 1)


if __name__ == '__main__':
    unittest.main()
