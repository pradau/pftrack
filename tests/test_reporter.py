"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for reporter module
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from analyzer import SpendingAnalyzer
from budget import BudgetManager
from reporter import ReportGenerator
from transaction import Transaction


class TestReportGenerator(unittest.TestCase):
    """Test cases for ReportGenerator class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
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
                description='Restaurant',
                amount=50.00,
                category='Restaurants'
            )
        ]
        self.analyzer = SpendingAnalyzer(self.transactions)
        self.reporter = ReportGenerator(self.analyzer, self.temp_dir)
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_generate_category_totals(self):
        """Test generating category totals report."""
        path = self.reporter.generate_category_totals()
        self.assertTrue(path.exists())
        self.assertEqual(path.parent, self.temp_dir)
    
    def test_generate_monthly_summary(self):
        """Test generating monthly summary report."""
        path = self.reporter.generate_monthly_summary()
        self.assertTrue(path.exists())
    
    def test_generate_top_merchants(self):
        """Test generating top merchants report."""
        path = self.reporter.generate_top_merchants()
        self.assertTrue(path.exists())
    
    def test_generate_transaction_list(self):
        """Test generating transaction list report."""
        path = self.reporter.generate_transaction_list()
        self.assertTrue(path.exists())
    
    def test_generate_budget_comparison(self):
        """Test generating budget comparison report."""
        import json
        budget_file = self.temp_dir / 'test_budgets.json'
        budget_data = {
            "monthly_budgets": {
                "Groceries": 150.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        budget_manager = BudgetManager(budget_file)
        path = self.reporter.generate_budget_comparison(budget_manager)
        self.assertTrue(path.exists())
    
    def test_export_to_json(self):
        """Test exporting to JSON."""
        path = self.reporter.export_to_json()
        self.assertTrue(path.exists())
        self.assertEqual(path.suffix, '.json')
    
    def test_generate_all_reports(self):
        """Test generating all reports."""
        reports = self.reporter.generate_all_reports()
        self.assertIn('monthly_summary', reports)
        self.assertIn('category_totals', reports)
        self.assertIn('top_merchants', reports)
        self.assertIn('transactions', reports)


if __name__ == '__main__':
    unittest.main()
