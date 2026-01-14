"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for categorizer module
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

from categorizer import CategoryClassifier
from transaction import Transaction


class TestCategoryClassifier(unittest.TestCase):
    """Test cases for CategoryClassifier class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / 'test_config.json'
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_default_categories(self):
        """Test using default categories."""
        classifier = CategoryClassifier()
        self.assertIn("Groceries", classifier.get_category_list())
        self.assertIn("Other", classifier.get_category_list())
    
    def test_categorize_by_keyword(self):
        """Test categorizing transaction by keyword."""
        classifier = CategoryClassifier()
        
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='SUPERMARKET',
            amount=50.00
        )
        
        category = classifier.categorize(transaction)
        self.assertEqual(category, "Groceries")
    
    def test_categorize_income(self):
        """Test categorizing income transaction."""
        config_data = {
            "categories": {
                "Income": {
                    "keywords": ["PAYROLL", "DEPOSIT"],
                    "priority": 1,
                    "require_negative": True
                },
                "Other": {
                    "keywords": [],
                    "priority": 999
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
        
        classifier = CategoryClassifier(self.config_file)
        
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='PAYROLL DEPOSIT',
            amount=-2000.00
        )
        
        category = classifier.categorize(transaction)
        self.assertEqual(category, "Income")
    
    def test_categorize_all(self):
        """Test categorizing multiple transactions."""
        classifier = CategoryClassifier()
        
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='SUPERMARKET',
                amount=50.00
            ),
            Transaction(
                date=datetime(2025, 1, 16),
                account_type='visa',
                description='RESTAURANT',
                amount=10.00
            )
        ]
        
        categorized = classifier.categorize_all(transactions)
        self.assertEqual(categorized[0].category, "Groceries")
        self.assertEqual(categorized[1].category, "Restaurants")
    
    def test_priority_ordering(self):
        """Test that priority affects categorization."""
        config_data = {
            "categories": {
                "Pets": {
                    "keywords": ["PET PLANET"],
                    "priority": 0
                },
                "Housing": {
                    "keywords": ["RENT"],
                    "priority": 1
                },
                "Other": {
                    "keywords": [],
                    "priority": 999
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
        
        classifier = CategoryClassifier(self.config_file)
        
        # "PET PLANET-BRENTWOOD" should match Pets (priority 0) not Housing (priority 1)
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='PET PLANET-BRENTWOOD',
            amount=50.00
        )
        
        category = classifier.categorize(transaction)
        self.assertEqual(category, "Pets")
    
    def test_auto_tagging(self):
        """Test auto-tagging functionality."""
        config_data = {
            "auto_tagging": {
                "tax-deductible": {
                    "keywords": ["WORK"],
                    "categories": []
                }
            },
            "categories": {
                "Work": {
                    "keywords": ["WORK"],
                    "priority": 1
                },
                "Other": {
                    "keywords": [],
                    "priority": 999
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(config_data, f)
        
        classifier = CategoryClassifier(self.config_file)
        
        transaction = Transaction(
            date=datetime(2025, 1, 15),
            account_type='chequing',
            description='WORK EXPENSE',
            amount=50.00
        )
        
        categorized = classifier.categorize_all([transaction])
        self.assertIn("tax-deductible", categorized[0].tags)


if __name__ == '__main__':
    unittest.main()
