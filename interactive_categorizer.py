"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Interactive transaction categorization tool
Dependencies: Python 3.6+
Usage: InteractiveCategorizer class for interactive transaction review and re-categorization
"""

import json
import re
import shutil
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from categorizer import CategoryClassifier
from transaction import Transaction


class InteractiveCategorizer:
    """Interactive tool for reviewing and re-categorizing transactions.
    
    Provides a two-phase interface:
    1. Display all transactions and let user select which ones to review
    2. Review selected transactions and save merchant keywords to config.private.json
    """
    
    def __init__(self):
        """Initialize the interactive categorizer."""
        self.config_backup_created = False
    
    def display_all_transactions(self, transactions: List[Transaction]) -> None:
        """Display all transactions in a numbered list.
        
        Args:
            transactions: List of transactions to display
        """
        if not transactions:
            print("No transactions to display.")
            return
        
        # Sort by date (most recent first)
        sorted_transactions = sorted(transactions, key=lambda t: t.date, reverse=True)
        
        print(f"\n=== All Transactions ({len(transactions)} total) ===")
        print(f"{'#':<5} {'Date':<12} {'Description':<35} {'Amount':>12} {'Category':<20}")
        print("-" * 95)
        
        for idx, transaction in enumerate(sorted_transactions, start=1):
            date_str = transaction.date.strftime("%m/%d/%Y")
            description = transaction.description[:33] + ".." if len(transaction.description) > 35 else transaction.description
            amount_str = f"${transaction.amount:.2f}"
            category = transaction.category[:18] + ".." if len(transaction.category) > 20 else transaction.category
            
            print(f"{idx:<5} {date_str:<12} {description:<35} {amount_str:>12} {category:<20}")
    
    def get_transaction_selection(self, total_count: int) -> Optional[List[int]]:
        """Get user selection of transaction numbers to review.
        
        Args:
            total_count: Total number of transactions available
            
        Returns:
            List of selected transaction indices (0-based), or None if user quits
        """
        if total_count == 0:
            return None
        
        while True:
            try:
                user_input = input(
                    f"\nEnter transaction numbers to review (space-separated, e.g., \"2 45 12\"):\n"
                    f"Or 'a' for all, 'q' to quit: "
                ).strip()
                
                if not user_input:
                    continue
                
                if user_input.lower() == 'q':
                    return None
                
                if user_input.lower() == 'a':
                    return list(range(total_count))
                
                # Parse space-separated numbers
                numbers = user_input.split()
                selected_indices = []
                
                for num_str in numbers:
                    try:
                        num = int(num_str)
                        if num < 1 or num > total_count:
                            print(f"Error: Transaction number {num} is out of range (1-{total_count})")
                            raise ValueError(f"Invalid transaction number: {num}")
                        # Convert to 0-based index
                        selected_indices.append(num - 1)
                    except ValueError:
                        print(f"Error: '{num_str}' is not a valid number")
                        raise ValueError(f"Invalid input: {num_str}")
                
                # Deduplicate while preserving order
                seen = set()
                unique_indices = []
                for idx in selected_indices:
                    if idx not in seen:
                        seen.add(idx)
                        unique_indices.append(idx)
                
                if not unique_indices:
                    print("No valid transactions selected. Please try again.")
                    continue
                
                return unique_indices
                
            except ValueError:
                print("Please enter valid transaction numbers, 'a' for all, or 'q' to quit.")
                continue
            except KeyboardInterrupt:
                print("\n\nCancelled by user.")
                return None
    
    def display_transaction_for_review(self, transaction: Transaction, 
                                      index: int, total_selected: int, 
                                      category_list: List[str]) -> None:
        """Display single transaction details for review.
        
        Args:
            transaction: Transaction to display
            index: Current transaction index (1-based for display)
            total_selected: Total number of selected transactions
            category_list: List of available category names
        """
        print(f"\n=== Reviewing Transaction {index} of {total_selected} ===")
        print(f"\nDate: {transaction.date.strftime('%m/%d/%Y')}")
        print(f"Description: {transaction.description}")
        print(f"Amount: ${transaction.amount:.2f}")
        print(f"Current Category: {transaction.category}")
        print(f"\nAvailable Categories:")
        
        for idx, category in enumerate(category_list, start=1):
            marker = " (current)" if category == transaction.category else ""
            print(f"  {idx}. {category}{marker}")
    
    def get_user_category_choice(self, category_list: List[str], 
                                current_category: str) -> Optional[str]:
        """Get user's category choice for a transaction.
        
        Args:
            category_list: List of available category names
            current_category: Current category of the transaction
            
        Returns:
            Selected category name, or None if user skips/quits
        """
        while True:
            try:
                prompt = (
                    f"\n[Enter] Accept current category | "
                    f"[1-{len(category_list)}] Select new category | "
                    f"[s] Skip | [q] Quit: "
                )
                user_input = input(prompt).strip()
                
                if not user_input:
                    # Enter pressed - accept current category
                    return current_category
                
                if user_input.lower() == 'q':
                    return None
                
                if user_input.lower() == 's':
                    return None  # Skip this transaction
                
                try:
                    choice_num = int(user_input)
                    if choice_num < 1 or choice_num > len(category_list):
                        print(f"Error: Please enter a number between 1 and {len(category_list)}")
                        continue
                    return category_list[choice_num - 1]
                except ValueError:
                    print(f"Error: '{user_input}' is not a valid choice")
                    continue
                    
            except KeyboardInterrupt:
                print("\n\nCancelled by user.")
                return None
    
    def extract_merchant_keyword(self, description: str) -> str:
        """Extract clean merchant name from transaction description.
        
        Args:
            description: Transaction description
            
        Returns:
            Cleaned merchant name in uppercase
        """
        # Convert to uppercase
        merchant = description.upper().strip()
        
        # Remove common prefixes
        prefixes = [
            r'^SQ\s*\*\s*',
            r'^TST-',
            r'^FS\s*\*\s*',
            r'^CBA\*\s*',
        ]
        for prefix in prefixes:
            merchant = re.sub(prefix, '', merchant, flags=re.IGNORECASE)
        
        # Remove location suffixes (e.g., "CALGARY, AB", postal codes, city names)
        # Common patterns: ", AB", ", BC", ", ON", ", QC", etc.
        merchant = re.sub(r',\s*[A-Z]{2}(\s|$)', '', merchant)
        # Remove postal codes (e.g., "T2P 1A1")
        merchant = re.sub(r'\b[A-Z]\d[A-Z]\s?\d[A-Z]\d\b', '', merchant)
        # Remove common city names at the end
        city_patterns = [
            r'\s+CALGARY\s*$',
            r'\s+EDMONTON\s*$',
            r'\s+TORONTO\s*$',
            r'\s+VANCOUVER\s*$',
        ]
        for pattern in city_patterns:
            merchant = re.sub(pattern, '', merchant, flags=re.IGNORECASE)
        
        # Remove common separators and descriptive text (e.g., " - University D", " - ")
        merchant = re.sub(r'\s*-\s*[^-]*$', '', merchant)  # Remove everything after " - "
        merchant = re.sub(r'\s*-\s*$', '', merchant)  # Remove trailing " - "
        
        # Remove trailing transaction codes/numbers (e.g., "#1234", store numbers)
        merchant = re.sub(r'\s*#\s*\d+\s*$', '', merchant)
        merchant = re.sub(r'\s+\d{4,}\s*$', '', merchant)  # Remove trailing 4+ digit numbers
        
        # Remove extra whitespace
        merchant = ' '.join(merchant.split())
        
        return merchant
    
    def confirm_keyword_addition(self, merchant: str, category: str) -> bool:
        """Confirm with user before adding keyword to config.
        
        Args:
            merchant: Extracted merchant keyword
            category: Category name
            
        Returns:
            True if user confirms, False otherwise
        """
        while True:
            try:
                response = input(
                    f'\nExtracted keyword: "{merchant}"\n'
                    f'Add "{merchant}" to "{category}" category? [y/n]: '
                ).strip().lower()
                
                if response in ('y', 'yes'):
                    return True
                elif response in ('n', 'no'):
                    return False
                else:
                    print("Please enter 'y' or 'n'")
                    continue
            except KeyboardInterrupt:
                print("\n\nCancelled.")
                return False
    
    def _backup_config(self, config_path: Path) -> None:
        """Create backup of config file before modification.
        
        Args:
            config_path: Path to config file to backup
        """
        if not self.config_backup_created and config_path.exists():
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = config_path.parent / f"{config_path.name}.backup.{timestamp}"
            shutil.copy2(config_path, backup_path)
            print(f"Created backup: {backup_path}")
            self.config_backup_created = True
    
    def save_keyword_to_config(self, merchant: str, category: str, 
                               config_path: Path) -> bool:
        """Save merchant keyword to config.private.json.
        
        Args:
            merchant: Merchant keyword to add
            category: Category name
            config_path: Path to config.private.json
            
        Returns:
            True if keyword was added, False otherwise
        """
        # Create backup before first write
        self._backup_config(config_path)
        
        # Load existing config or create new structure
        if config_path.exists():
            try:
                with open(config_path, 'r', encoding='utf-8') as f:
                    config = json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                print(f"Error reading config file: {e}")
                return False
        else:
            # Create new config structure
            config = {
                "auto_tagging": {},
                "categories": {}
            }
        
        # Ensure categories structure exists
        if "categories" not in config:
            config["categories"] = {}
        
        # Get or create category entry
        if category not in config["categories"]:
            config["categories"][category] = {
                "keywords": [],
                "priority": 1  # Default priority
            }
        
        # Add keyword if not already present
        keywords = config["categories"][category].get("keywords", [])
        if merchant not in keywords:
            keywords.append(merchant)
            config["categories"][category]["keywords"] = keywords
            
            # Save updated config
            try:
                with open(config_path, 'w', encoding='utf-8') as f:
                    json.dump(config, f, indent=2, ensure_ascii=False)
                print(f"Added \"{merchant}\" to config.private.json")
                return True
            except IOError as e:
                print(f"Error writing config file: {e}")
                return False
        else:
            print(f"Keyword \"{merchant}\" already exists in \"{category}\" category")
            return False
    
    def categorize_interactively(self, transactions: List[Transaction], 
                                 classifier: CategoryClassifier, 
                                 config_path: Path) -> Dict[str, int]:
        """Main orchestration method for interactive categorization.
        
        Args:
            transactions: List of transactions to review
            classifier: CategoryClassifier instance
            config_path: Path to config.private.json
            
        Returns:
            Dictionary with statistics about the session
        """
        stats = {
            "total": len(transactions),
            "selected": 0,
            "reviewed": 0,
            "accepted": 0,
            "re_categorized": 0,
            "keywords_added": 0,
            "skipped": 0
        }
        
        if not transactions:
            print("No transactions to review.")
            return stats
        
        # Ensure transactions are categorized
        categorized_transactions = classifier.categorize_all(transactions)
        
        # Sort by date (most recent first) for display
        sorted_transactions = sorted(categorized_transactions, 
                                   key=lambda t: t.date, reverse=True)
        
        # Phase 1: Display all transactions and get selection
        self.display_all_transactions(sorted_transactions)
        selected_indices = self.get_transaction_selection(len(sorted_transactions))
        
        if selected_indices is None:
            print("\nNo transactions selected. Exiting.")
            return stats
        
        stats["selected"] = len(selected_indices)
        
        # Get category list from classifier
        category_list = classifier.get_category_list()
        
        # Phase 2: Review selected transactions
        print(f"\n=== Reviewing {len(selected_indices)} selected transaction(s) ===")
        
        for idx, transaction_idx in enumerate(selected_indices, start=1):
            transaction = sorted_transactions[transaction_idx]
            original_category = transaction.category
            
            # Display transaction for review
            self.display_transaction_for_review(transaction, idx, 
                                              len(selected_indices), category_list)
            
            # Get user's category choice
            new_category = self.get_user_category_choice(category_list, original_category)
            
            if new_category is None:
                # User skipped or quit
                stats["skipped"] += 1
                # If not the last transaction, ask if they want to continue
                if idx < len(selected_indices):
                    try:
                        continue_choice = input("\nContinue with remaining transactions? [y/n]: ").strip().lower()
                        if continue_choice not in ('y', 'yes'):
                            # User wants to quit - count remaining as skipped
                            stats["skipped"] += len(selected_indices) - idx
                            break
                    except KeyboardInterrupt:
                        # User interrupted - count remaining as skipped
                        stats["skipped"] += len(selected_indices) - idx
                        break
                continue
            
            stats["reviewed"] += 1
            
            if new_category == original_category:
                # User accepted current category
                stats["accepted"] += 1
            else:
                # User selected new category
                stats["re_categorized"] += 1
                transaction.category = new_category
                
                # Extract merchant keyword
                merchant = self.extract_merchant_keyword(transaction.description)
                
                if merchant:
                    # Confirm and save keyword
                    if self.confirm_keyword_addition(merchant, new_category):
                        if self.save_keyword_to_config(merchant, new_category, config_path):
                            stats["keywords_added"] += 1
        
        return stats
