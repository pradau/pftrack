"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for data_manager module
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from data_manager import DataManager
from transaction import Transaction


class TestDataManager(unittest.TestCase):
    """Test cases for DataManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.manager = DataManager(self.temp_dir)
        self.transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='Test Transaction',
                amount=50.00,
                category='Shopping'
            )
        ]
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_export_to_csv(self):
        """Test exporting transactions to CSV."""
        path = self.manager.export_transactions_to_csv(self.transactions)
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, '.csv')
    
    def test_export_to_json(self):
        """Test exporting transactions to JSON."""
        path = self.manager.export_transactions_to_json(self.transactions)
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, '.json')
    
    def test_import_from_json(self):
        """Test importing transactions from JSON."""
        # First export
        json_path = self.manager.export_transactions_to_json(self.transactions)
        
        # Then import
        imported = self.manager.import_transactions_from_json(json_path)
        self.assertEqual(len(imported), 1)
        self.assertEqual(imported[0].description, 'Test Transaction')
    
    def test_backup_data(self):
        """Test creating backup."""
        backup_path = self.manager.backup_data(self.transactions)
        self.assertTrue(backup_path.exists())
        self.assertIn('backup_', backup_path.name)
    
    def test_restore_from_backup(self):
        """Test restoring from backup."""
        backup_path = self.manager.backup_data(self.transactions)
        restored = self.manager.restore_from_backup(backup_path)
        self.assertEqual(len(restored), 1)


if __name__ == '__main__':
    unittest.main()
