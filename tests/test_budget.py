"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for budget module
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from budget import BudgetManager


class TestBudgetManager(unittest.TestCase):
    """Test cases for BudgetManager class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.budget_file = self.temp_dir / 'test_budgets.json'
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_empty_budget_manager(self):
        """Test creating budget manager with no file."""
        manager = BudgetManager()
        self.assertEqual(manager.get_monthly_budget("Groceries"), 0.0)
    
    def test_load_monthly_budgets(self):
        """Test loading monthly budgets from file."""
        budget_data = {
            "monthly_budgets": {
                "Groceries": 500.00,
                "Restaurants": 200.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        self.assertEqual(manager.get_monthly_budget("Groceries"), 500.00)
        self.assertEqual(manager.get_monthly_budget("Restaurants"), 200.00)
        self.assertEqual(manager.get_monthly_budget("Unknown"), 0.0)
    
    def test_load_annual_budgets(self):
        """Test loading annual budgets."""
        budget_data = {
            "monthly_budgets": {},
            "annual_budgets": {
                "Travel": 3000.00
            },
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        self.assertEqual(manager.get_annual_budget("Travel"), 3000.00)
    
    def test_get_budget_for_period_monthly(self):
        """Test calculating budget for period with monthly budget."""
        budget_data = {
            "monthly_budgets": {
                "Groceries": 500.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        budget = manager.get_budget_for_period("Groceries", start_date, end_date)
        # Budget calculation uses days/30.44, so for 31 days it's approximately 500
        # Allow some tolerance for day-based calculation (within 20 dollars)
        self.assertAlmostEqual(budget, 500.00, delta=20.0)
    
    def test_get_budget_for_period_annual(self):
        """Test calculating budget for period with annual budget."""
        budget_data = {
            "monthly_budgets": {},
            "annual_budgets": {
                "Travel": 3650.00
            },
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        
        budget = manager.get_budget_for_period("Travel", start_date, end_date)
        # Should be approximately 1/12 of annual budget (prorated by days)
        # Calculation uses days/365.25, so for 31 days it's approximately 1/12
        expected = 3650.00 / 12
        # Allow tolerance for day-based proration
        self.assertAlmostEqual(budget, expected, delta=10.0)
    
    def test_has_budget(self):
        """Test checking if category has budget."""
        budget_data = {
            "monthly_budgets": {
                "Groceries": 500.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        self.assertTrue(manager.has_budget("Groceries"))
        self.assertFalse(manager.has_budget("Unknown"))
    
    def test_get_all_categories_with_budgets(self):
        """Test getting all categories with budgets."""
        budget_data = {
            "monthly_budgets": {
                "Groceries": 500.00
            },
            "annual_budgets": {
                "Travel": 3000.00
            },
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        manager = BudgetManager(self.budget_file)
        categories = manager.get_all_categories_with_budgets()
        self.assertIn("Groceries", categories)
        self.assertIn("Travel", categories)
        self.assertEqual(len(categories), 2)
    
    def test_invalid_budget_file(self):
        """Test handling invalid budget file."""
        with open(self.budget_file, 'w') as f:
            f.write("invalid json")
        
        with self.assertRaises(ValueError):
            BudgetManager(self.budget_file)
    
    def test_negative_budget_validation(self):
        """Test that negative budgets raise error."""
        budget_data = {
            "monthly_budgets": {
                "Groceries": -100.00
            },
            "annual_budgets": {},
            "category_budgets": {}
        }
        with open(self.budget_file, 'w') as f:
            json.dump(budget_data, f)
        
        with self.assertRaises(ValueError):
            BudgetManager(self.budget_file)


if __name__ == '__main__':
    unittest.main()
