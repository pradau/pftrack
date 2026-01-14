"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Unit tests for interactive_categorizer module
"""

import json
import tempfile
import unittest
from datetime import datetime
from pathlib import Path
from unittest.mock import patch, MagicMock

from categorizer import CategoryClassifier
from interactive_categorizer import InteractiveCategorizer
from transaction import Transaction


class TestInteractiveCategorizer(unittest.TestCase):
    """Test cases for InteractiveCategorizer class."""
    
    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = Path(tempfile.mkdtemp())
        self.config_file = self.temp_dir / 'config.private.json'
        self.categorizer = InteractiveCategorizer()
        
        # Create a test classifier
        self.classifier = CategoryClassifier()
    
    def tearDown(self):
        """Clean up test fixtures."""
        import shutil
        shutil.rmtree(self.temp_dir)
    
    def test_display_all_transactions_empty(self):
        """Test displaying empty transaction list."""
        with patch('builtins.print') as mock_print:
            self.categorizer.display_all_transactions([])
            mock_print.assert_called_with("No transactions to display.")
    
    def test_display_all_transactions(self):
        """Test displaying transactions."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='SAVE ON FOODS',
                amount=50.00,
                category='Groceries'
            ),
            Transaction(
                date=datetime(2025, 1, 16),
                account_type='visa',
                description='SQ *SESAME',
                amount=12.50,
                category='Other'
            ),
        ]
        
        with patch('builtins.print'):
            # Should not raise exception
            self.categorizer.display_all_transactions(transactions)
    
    @patch('builtins.input', return_value='2 3')
    def test_get_transaction_selection_valid(self, mock_input):
        """Test getting valid transaction selection."""
        result = self.categorizer.get_transaction_selection(5)
        self.assertEqual(result, [1, 2])  # 0-based indices
    
    @patch('builtins.input', return_value='a')
    def test_get_transaction_selection_all(self, mock_input):
        """Test selecting all transactions."""
        result = self.categorizer.get_transaction_selection(5)
        self.assertEqual(result, [0, 1, 2, 3, 4])
    
    @patch('builtins.input', return_value='q')
    def test_get_transaction_selection_quit(self, mock_input):
        """Test quitting selection."""
        result = self.categorizer.get_transaction_selection(5)
        self.assertIsNone(result)
    
    @patch('builtins.input', side_effect=['99', '2'])
    @patch('builtins.print')
    def test_get_transaction_selection_invalid_then_valid(self, mock_print, mock_input):
        """Test handling invalid input then valid input."""
        result = self.categorizer.get_transaction_selection(5)
        self.assertEqual(result, [1])
    
    @patch('builtins.input', return_value='1 1 2')
    def test_get_transaction_selection_deduplicate(self, mock_input):
        """Test deduplication of transaction numbers."""
        result = self.categorizer.get_transaction_selection(5)
        self.assertEqual(result, [0, 1])  # Should deduplicate
    
    def test_extract_merchant_keyword_simple(self):
        """Test extracting simple merchant name."""
        result = self.categorizer.extract_merchant_keyword("SAVE ON FOODS")
        self.assertEqual(result, "SAVE ON FOODS")
    
    def test_extract_merchant_keyword_with_prefix(self):
        """Test extracting merchant name with prefix."""
        result = self.categorizer.extract_merchant_keyword("SQ *SESAME CALGARY, AB")
        self.assertEqual(result, "SESAME")
    
    def test_extract_merchant_keyword_with_tst_prefix(self):
        """Test extracting merchant name with TST- prefix."""
        result = self.categorizer.extract_merchant_keyword("TST-Una - University D Calgary, AB")
        # Should remove TST- prefix, location, and descriptive text after " - "
        self.assertEqual(result, "UNA")
    
    def test_extract_merchant_keyword_with_store_number(self):
        """Test extracting merchant name with store number."""
        result = self.categorizer.extract_merchant_keyword("SAVE ON FOODS #1234")
        self.assertEqual(result, "SAVE ON FOODS")
    
    def test_extract_merchant_keyword_with_cba_prefix(self):
        """Test extracting merchant name with CBA* prefix."""
        result = self.categorizer.extract_merchant_keyword("CBA*SOPHOS")
        self.assertEqual(result, "SOPHOS")
    
    def test_extract_merchant_keyword_with_location(self):
        """Test extracting merchant name with location suffix."""
        result = self.categorizer.extract_merchant_keyword("PARKDALE GAS CALGARY, AB")
        self.assertEqual(result, "PARKDALE GAS")
    
    def test_extract_merchant_keyword_rcss_nursery(self):
        """Test extracting RCSS NURSERY with store number."""
        result = self.categorizer.extract_merchant_keyword("RCSS NURSERY #3730")
        self.assertEqual(result, "RCSS NURSERY")
    
    @patch('builtins.input', return_value='y')
    def test_confirm_keyword_addition_yes(self, mock_input):
        """Test confirming keyword addition."""
        result = self.categorizer.confirm_keyword_addition("SESAME", "Restaurants")
        self.assertTrue(result)
    
    @patch('builtins.input', return_value='n')
    def test_confirm_keyword_addition_no(self, mock_input):
        """Test rejecting keyword addition."""
        result = self.categorizer.confirm_keyword_addition("SESAME", "Restaurants")
        self.assertFalse(result)
    
    @patch('builtins.input', side_effect=['invalid', 'y'])
    @patch('builtins.print')
    def test_confirm_keyword_addition_invalid_then_yes(self, mock_print, mock_input):
        """Test handling invalid input then yes."""
        result = self.categorizer.confirm_keyword_addition("SESAME", "Restaurants")
        self.assertTrue(result)
    
    def test_save_keyword_to_config_new_file(self):
        """Test saving keyword to new config file."""
        result = self.categorizer.save_keyword_to_config(
            "SESAME", "Restaurants", self.config_file
        )
        self.assertTrue(result)
        self.assertTrue(self.config_file.exists())
        
        # Verify content
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("Restaurants", config["categories"])
        self.assertIn("SESAME", config["categories"]["Restaurants"]["keywords"])
    
    def test_save_keyword_to_config_existing_file(self):
        """Test saving keyword to existing config file."""
        # Create existing config
        existing_config = {
            "auto_tagging": {},
            "categories": {
                "Restaurants": {
                    "keywords": ["MCDONALD"],
                    "priority": 1
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(existing_config, f)
        
        # Add new keyword
        result = self.categorizer.save_keyword_to_config(
            "SESAME", "Restaurants", self.config_file
        )
        self.assertTrue(result)
        
        # Verify content
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        keywords = config["categories"]["Restaurants"]["keywords"]
        self.assertIn("MCDONALD", keywords)
        self.assertIn("SESAME", keywords)
    
    def test_save_keyword_to_config_duplicate(self):
        """Test saving duplicate keyword."""
        # Create existing config with keyword
        existing_config = {
            "auto_tagging": {},
            "categories": {
                "Restaurants": {
                    "keywords": ["SESAME"],
                    "priority": 1
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(existing_config, f)
        
        # Try to add duplicate
        with patch('builtins.print') as mock_print:
            result = self.categorizer.save_keyword_to_config(
                "SESAME", "Restaurants", self.config_file
            )
            self.assertFalse(result)
            # Should print that keyword already exists
            mock_print.assert_called()
    
    def test_save_keyword_to_config_new_category(self):
        """Test saving keyword to new category in existing config."""
        # Create existing config without the category
        existing_config = {
            "auto_tagging": {},
            "categories": {
                "Groceries": {
                    "keywords": ["CO-OP"],
                    "priority": 2
                }
            }
        }
        with open(self.config_file, 'w') as f:
            json.dump(existing_config, f)
        
        # Add keyword to new category
        result = self.categorizer.save_keyword_to_config(
            "SESAME", "Restaurants", self.config_file
        )
        self.assertTrue(result)
        
        # Verify both categories exist
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        self.assertIn("Groceries", config["categories"])
        self.assertIn("Restaurants", config["categories"])
        self.assertIn("SESAME", config["categories"]["Restaurants"]["keywords"])
    
    def test_backup_config_creation(self):
        """Test that backup is created before first write."""
        # Create existing config file first (backup only created if file exists)
        existing_config = {
            "auto_tagging": {},
            "categories": {}
        }
        with open(self.config_file, 'w') as f:
            json.dump(existing_config, f)
        
        # First write should create backup
        self.categorizer.save_keyword_to_config(
            "SESAME", "Restaurants", self.config_file
        )
        
        # Check backup exists
        backup_files = list(self.temp_dir.glob("config.private.json.backup.*"))
        self.assertEqual(len(backup_files), 1)
    
    @patch('builtins.input', return_value='')
    @patch('builtins.print')
    def test_get_user_category_choice_accept(self, mock_print, mock_input):
        """Test accepting current category (Enter key)."""
        category_list = ["Groceries", "Restaurants", "Other"]
        result = self.categorizer.get_user_category_choice(category_list, "Groceries")
        self.assertEqual(result, "Groceries")
    
    @patch('builtins.input', return_value='2')
    @patch('builtins.print')
    def test_get_user_category_choice_select(self, mock_print, mock_input):
        """Test selecting a different category."""
        category_list = ["Groceries", "Restaurants", "Other"]
        result = self.categorizer.get_user_category_choice(category_list, "Groceries")
        self.assertEqual(result, "Restaurants")
    
    @patch('builtins.input', return_value='s')
    @patch('builtins.print')
    def test_get_user_category_choice_skip(self, mock_print, mock_input):
        """Test skipping transaction."""
        category_list = ["Groceries", "Restaurants", "Other"]
        result = self.categorizer.get_user_category_choice(category_list, "Groceries")
        self.assertIsNone(result)
    
    @patch('builtins.input', return_value='q')
    @patch('builtins.print')
    def test_get_user_category_choice_quit(self, mock_print, mock_input):
        """Test quitting."""
        category_list = ["Groceries", "Restaurants", "Other"]
        result = self.categorizer.get_user_category_choice(category_list, "Groceries")
        self.assertIsNone(result)
    
    @patch('builtins.input', side_effect=['99', '2'])
    @patch('builtins.print')
    def test_get_user_category_choice_invalid_then_valid(self, mock_print, mock_input):
        """Test handling invalid category number then valid."""
        category_list = ["Groceries", "Restaurants", "Other"]
        result = self.categorizer.get_user_category_choice(category_list, "Groceries")
        self.assertEqual(result, "Restaurants")
    
    @patch('builtins.input', side_effect=['2 3', 'q'])
    @patch('builtins.print')
    def test_categorize_interactively_selection_quit(self, mock_print, mock_input):
        """Test interactive categorization with quit at selection."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='SAVE ON FOODS',
                amount=50.00
            ),
        ]
        
        stats = self.categorizer.categorize_interactively(
            transactions, self.classifier, self.config_file
        )
        
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["selected"], 0)
    
    @patch('builtins.input', side_effect=['1', '', 'y'])
    @patch('builtins.print')
    def test_categorize_interactively_accept_category(self, mock_print, mock_input):
        """Test interactive categorization accepting current category."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='CO-OP GROCERY',
                amount=50.00,
                category='Groceries'
            ),
        ]
        
        stats = self.categorizer.categorize_interactively(
            transactions, self.classifier, self.config_file
        )
        
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["selected"], 1)
        self.assertEqual(stats["reviewed"], 1)
        self.assertEqual(stats["accepted"], 1)
        self.assertEqual(stats["re_categorized"], 0)
    
    @patch('builtins.input', side_effect=['1', '2', 'y', 'y'])
    @patch('builtins.print')
    def test_categorize_interactively_re_categorize(self, mock_print, mock_input):
        """Test interactive categorization with re-categorization."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='SQ *SESAME',
                amount=12.50,
                category='Other'
            ),
        ]
        
        stats = self.categorizer.categorize_interactively(
            transactions, self.classifier, self.config_file
        )
        
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["selected"], 1)
        self.assertEqual(stats["reviewed"], 1)
        self.assertEqual(stats["accepted"], 0)
        self.assertEqual(stats["re_categorized"], 1)
        self.assertEqual(stats["keywords_added"], 1)
        
        # Verify keyword was saved
        self.assertTrue(self.config_file.exists())
        with open(self.config_file, 'r') as f:
            config = json.load(f)
        
        # Find which category has SESAME (should be Restaurants if that's category 2)
        categories = list(self.classifier.get_category_list())
        if len(categories) >= 2:
            expected_category = categories[1]  # 0-based, so 2nd category
            self.assertIn(expected_category, config["categories"])
            self.assertIn("SESAME", config["categories"][expected_category]["keywords"])
    
    @patch('builtins.input', side_effect=['1', 's'])
    @patch('builtins.print')
    def test_categorize_interactively_skip(self, mock_print, mock_input):
        """Test interactive categorization skipping transaction."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='SAVE ON FOODS',
                amount=50.00,
                category='Groceries'
            ),
        ]
        
        stats = self.categorizer.categorize_interactively(
            transactions, self.classifier, self.config_file
        )
        
        self.assertEqual(stats["total"], 1)
        self.assertEqual(stats["selected"], 1)
        self.assertEqual(stats["skipped"], 1)
    
    def test_categorize_interactively_empty_list(self):
        """Test interactive categorization with empty transaction list."""
        with patch('builtins.print') as mock_print:
            stats = self.categorizer.categorize_interactively(
                [], self.classifier, self.config_file
            )
            
            self.assertEqual(stats["total"], 0)
            mock_print.assert_called_with("No transactions to review.")
    
    @patch('builtins.input', side_effect=['a', '', '', 'y'])
    @patch('builtins.print')
    def test_categorize_interactively_select_all(self, mock_print, mock_input):
        """Test selecting all transactions."""
        transactions = [
            Transaction(
                date=datetime(2025, 1, 15),
                account_type='chequing',
                description='TRANSACTION 1',
                amount=10.00,
                category='Other'
            ),
            Transaction(
                date=datetime(2025, 1, 16),
                account_type='chequing',
                description='TRANSACTION 2',
                amount=20.00,
                category='Other'
            ),
        ]
        
        stats = self.categorizer.categorize_interactively(
            transactions, self.classifier, self.config_file
        )
        
        self.assertEqual(stats["total"], 2)
        self.assertEqual(stats["selected"], 2)
        self.assertEqual(stats["reviewed"], 2)
        self.assertEqual(stats["accepted"], 2)


if __name__ == '__main__':
    unittest.main()
