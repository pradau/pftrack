"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for transaction module
"""

import unittest
from datetime import datetime

from transaction import Transaction


class TestTransaction(unittest.TestCase):
    """Test cases for Transaction dataclass."""
    
    def test_transaction_creation(self):
        """Test creating a valid transaction."""
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Test Transaction',
            amount=50.00
        )
        self.assertEqual(transaction.amount, 50.00)
        self.assertEqual(transaction.category, 'Other')
    
    def test_is_expense(self):
        """Test expense detection."""
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Expense',
            amount=50.00
        )
        self.assertTrue(transaction.is_expense())
        self.assertFalse(transaction.is_income())
    
    def test_is_income(self):
        """Test income detection."""
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Income',
            amount=-100.00
        )
        self.assertTrue(transaction.is_income())
        self.assertFalse(transaction.is_expense())
    
    def test_invalid_account_type(self):
        """Test invalid account type raises error."""
        with self.assertRaises(ValueError):
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='invalid',
                description='Test',
                amount=50.00
            )
    
    def test_tags_and_notes(self):
        """Test tags and notes fields."""
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Test',
            amount=50.00,
            tags=['test-tag'],
            notes='Test note'
        )
        self.assertEqual(transaction.tags, ['test-tag'])
        self.assertEqual(transaction.notes, 'Test note')


if __name__ == '__main__':
    unittest.main()
