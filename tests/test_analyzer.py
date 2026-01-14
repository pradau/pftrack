"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for analyzer module
"""

import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from analyzer import SpendingAnalyzer
from budget import BudgetManager
from transaction import Transaction


class TestSpendingAnalyzer(unittest.TestCase):
    """Test cases for SpendingAnalyzer class."""
    
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
                description='Restaurant',
                amount=50.00,
                category='Restaurants'
            ),
            Transaction(
                date=datetime(2025, 2, 10),
                account_type='chequing',
                description='Groceries Store',
                amount=120.00,
                category='Groceries'
            ),
            Transaction(
                date=datetime(2025, 1, 1),
                account_type='chequing',
                description='PAYROLL',
                amount=-2000.00,
                category='Income'
            )
        ]
        self.analyzer = SpendingAnalyzer(self.transactions)
    
    def test_category_totals(self):
        """Test calculating category totals."""
        totals = self.analyzer.category_totals()
        self.assertEqual(totals['Groceries'], 220.00)
        self.assertEqual(totals['Restaurants'], 50.00)
        self.assertNotIn('Income', totals)  # Income not included in expense totals
    
    def test_monthly_summary(self):
        """Test monthly summary calculation."""
        summary = self.analyzer.monthly_summary()
        self.assertIn('2025-01', summary)
        self.assertIn('2025-02', summary)
        self.assertEqual(summary['2025-01']['Groceries'], 100.00)
        self.assertEqual(summary['2025-01']['Restaurants'], 50.00)
        self.assertEqual(summary['2025-02']['Groceries'], 120.00)
    
    def test_income_vs_expenses(self):
        """Test income vs expenses calculation."""
        result = self.analyzer.income_vs_expenses()
        self.assertEqual(result['income'], 2000.00)
        self.assertEqual(result['expenses'], 270.00)
        self.assertEqual(result['net'], 1730.00)
    
    def test_filter_by_date_range(self):
        """Test filtering by date range."""
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        filtered = self.analyzer.filter_by_date_range(start_date, end_date)
        self.assertEqual(len(filtered), 3)  # 3 transactions in January
    
    def test_top_merchants(self):
        """Test top merchants calculation."""
        top = self.analyzer.top_merchants(limit=5)
        # Should have at least 2 unique merchants (Groceries Store appears twice, Restaurant once)
        self.assertGreaterEqual(len(top), 2)
        # Groceries Store should be first (highest total: 220.00)
        merchant_names = [m[0] for m in top]
        self.assertIn('Groceries Store', merchant_names)
    
    def test_budget_vs_actual(self):
        """Test budget comparison."""
        import json
        temp_dir = Path(tempfile.mkdtemp())
        budget_file = temp_dir / 'test_budgets.json'
        
        budget_data = {
            "monthly_budgets": {
                "Groceries": 150.00,
                "Restaurants": 100.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        budget_manager = BudgetManager(budget_file)
        comparison = self.analyzer.budget_vs_actual(budget_manager)
        
        self.assertIn('Groceries', comparison)
        self.assertGreater(comparison['Groceries']['actual'], comparison['Groceries']['budget'])
        
        import shutil
        shutil.rmtree(temp_dir)
    
    def test_average_monthly_spending(self):
        """Test average monthly spending calculation."""
        avg = self.analyzer.average_monthly_spending('Groceries')
        self.assertAlmostEqual(avg, 110.00, places=2)
    
    def test_spending_velocity(self):
        """Test spending velocity calculation."""
        velocity = self.analyzer.spending_velocity('Groceries', period_days=60)
        self.assertGreater(velocity, 0)
    
    def test_category_comparison(self):
        """Test category comparison."""
        comparison = self.analyzer.category_comparison(['Groceries', 'Restaurants'])
        self.assertEqual(comparison['Groceries'], 220.00)
        self.assertEqual(comparison['Restaurants'], 50.00)
    
    def test_spending_forecast(self):
        """Test spending forecast."""
        forecast = self.analyzer.spending_forecast('Groceries', months=3)
        self.assertGreater(forecast, 0)
    
    def test_seasonal_patterns(self):
        """Test seasonal pattern detection."""
        patterns = self.analyzer.seasonal_patterns()
        self.assertIn('Groceries', patterns)
        self.assertIn('January', patterns['Groceries'])


if __name__ == '__main__':
    unittest.main()
