"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for transaction_manager module
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from transaction import Transaction
from transaction_manager import TransactionManager


class TestTransactionManager(unittest.TestCase):
    """Test cases for TransactionManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = TransactionManager(self.temp_dir / 'manual_transactions.json')
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_add_transaction(self):
        """Test adding a manual transaction."""
        transaction_data = self.manager.add_transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Manual Entry',
            amount=50.00,
            category='Shopping'
        )
        self.assertEqual(transaction_data['amount'], 50.00)
        self.assertEqual(transaction_data['category'], 'Shopping')
    
    def test_get_manual_transactions(self):
        """Test retrieving manual transactions."""
        self.manager.add_transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Test',
            amount=50.00
        )
        
        transactions = self.manager.get_manual_transactions()
        self.assertEqual(len(transactions), 1)
        self.assertEqual(transactions[0].description, 'Test')
    
    def test_edit_transaction(self):
        """Test editing a transaction."""
        self.manager.add_transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Original',
            amount=50.00
        )
        
        updated = self.manager.edit_transaction(0, description='Updated')
        self.assertEqual(updated['description'], 'Updated')
    
    def test_delete_transaction(self):
        """Test deleting a transaction."""
        self.manager.add_transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='To Delete',
            amount=50.00
        )
        
        self.manager.delete_transaction(0)
        transactions = self.manager.get_manual_transactions()
        self.assertEqual(len(transactions), 0)
    
    def test_detect_duplicates(self):
        """Test duplicate detection."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='Same Store',
                amount=50.00
            ),
            Transaction(
                date=datetime(2025, 1, 16),
                account_type='chequing',
                description='Same Store',
                amount=50.00
            )
        ]
        
        duplicates = self.manager.detect_duplicates(transactions, date_tolerance_days=2)
        self.assertGreater(len(duplicates), 0)
    
    def test_merge_transactions(self):
        """Test merging duplicate transactions."""
        t1 = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Test',
            amount=50.00,
            tags=['tag1']
        )
        t2 = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='Test',
            amount=50.00,
            tags=['tag2'],
            notes='Note'
        )
        
        merged = self.manager.merge_transactions(t1, t2)
        self.assertIn('tag1', merged.tags)
        self.assertIn('tag2', merged.tags)
        self.assertIsNotNone(merged.notes)


if __name__ == '__main__':
    unittest.main()
