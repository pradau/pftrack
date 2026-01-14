"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Rules-based transaction categorization system
Dependencies: Python 3.6+
Usage: CategoryClassifier class to automatically categorize transactions
"""

import json
from pathlib import Path
from typing import Dict, List, Optional

from transaction import Transaction


class CategoryClassifier:
    """Categorizes transactions using keyword-based pattern matching.
    
    Uses a priority-based system where more specific patterns override
    general ones. Categories are defined in a configuration file with
    keyword patterns for matching.
    """
    
    def __init__(self, config_path: Optional[Path] = None, 
                 private_config_path: Optional[Path] = None):
        """Initialize classifier with category rules.
        
        Args:
            config_path: Path to JSON config file with category definitions.
                         If None, uses default categories.
            private_config_path: Path to private/confidential config file.
                                If None, looks for config.private.json in same directory as config_path.
        """
        self.auto_tagging_rules = {}
        
        # Load public config
        if config_path and config_path.exists():
            config = self._load_config(config_path)
            self.categories = config.get('categories', self._get_default_categories())
            self.auto_tagging_rules = config.get('auto_tagging', {})
            
            # Load private config if available
            if private_config_path is None:
                # Default to config.private.json in same directory as config_path
                private_config_path = config_path.parent / 'config.private.json'
            
            if private_config_path and private_config_path.exists():
                private_config = self._load_config(private_config_path)
                # Merge private config into categories (private keywords extend public ones)
                self._merge_config(private_config)
        else:
            self.categories = self._get_default_categories()
        
        # Sort categories by priority (more specific patterns first)
        self._sort_categories_by_priority()
    
    def _merge_config(self, private_config: Dict) -> None:
        """Merge private config into existing categories and auto-tagging rules.
        
        Private config keywords are added to existing categories.
        Private auto-tagging rules extend public ones.
        
        Args:
            private_config: Private configuration dictionary
        """
        # Merge categories
        private_categories = private_config.get('categories', {})
        for category_name, category_config in private_categories.items():
            if category_name in self.categories:
                # Merge keywords (extend existing list)
                existing_keywords = set(self.categories[category_name].get('keywords', []))
                private_keywords = set(category_config.get('keywords', []))
                self.categories[category_name]['keywords'] = list(existing_keywords | private_keywords)
                # Private config can override priority if specified
                if 'priority' in category_config:
                    self.categories[category_name]['priority'] = category_config['priority']
                # Merge other properties
                for key, value in category_config.items():
                    if key not in ['keywords', 'priority']:
                        self.categories[category_name][key] = value
            else:
                # Add new category from private config
                self.categories[category_name] = category_config.copy()
        
        # Merge auto-tagging rules
        private_auto_tagging = private_config.get('auto_tagging', {})
        for tag_name, tag_config in private_auto_tagging.items():
            if tag_name in self.auto_tagging_rules:
                # Merge keywords and categories
                existing_keywords = set(self.auto_tagging_rules[tag_name].get('keywords', []))
                private_keywords = set(tag_config.get('keywords', []))
                self.auto_tagging_rules[tag_name]['keywords'] = list(existing_keywords | private_keywords)
                
                existing_categories = set(self.auto_tagging_rules[tag_name].get('categories', []))
                private_categories = set(tag_config.get('categories', []))
                self.auto_tagging_rules[tag_name]['categories'] = list(existing_categories | private_categories)
            else:
                # Add new auto-tagging rule
                self.auto_tagging_rules[tag_name] = tag_config.copy()
    
    def _get_default_categories(self) -> Dict[str, Dict]:
        """Get default category definitions with keyword patterns.
        
        Returns:
            Dict mapping category names to their configuration
        """
        return {
            "Groceries": {
                "keywords": ["GROCERY", "CO-OP", "SUPERSTORE", "SAFEWAY", "WALMART", "COSTCO", "NO FRILLS"],
                "priority": 1
            },
            "Restaurants": {
                "keywords": ["RESTAURANT", "MCDONALD", "STARBUKO", "PIZZA", "TIM HORTONS", "SUBWAY", 
                            "PEKING GARDEN", "SHAWARMA", "KOREAN VILLAGE"],
                "priority": 1
            },
            "Gas/Transportation": {
                "keywords": ["GAS", "PETRO", "SHELL", "PARKING", "ESSO", "MOBIL"],
                "priority": 1
            },
            "Utilities": {
                "keywords": ["TELUS", "ENMAX", "UTILITY BILL", "HYDRO", "ELECTRIC"],
                "priority": 2
            },
            "Housing": {
                "keywords": ["MORTGAGE", "RENT", "INSURANCE INTACT", "PROPERTY TAX"],
                "priority": 1
            },
            "Shopping": {
                "keywords": ["AMAZON", "CANADIAN TIRE", "WINNERS", "DOLLARAMA", "LONDON DRUGS", 
                            "GOODWILL", "PLATO'S CLOSET", "FAIR'S FAIR"],
                "priority": 2
            },
            "Entertainment": {
                "keywords": ["AMAZON CHANNELS", "ONEBOOKSHEL", "NETFLIX", "SPOTIFY"],
                "priority": 1
            },
            "Income": {
                "keywords": ["PAYROLL", "DEPOSIT", "INTEREST"],
                "priority": 1,
                "require_negative": True  # Income has negative amount
            },
            "Transfers": {
                "keywords": ["TRANSFER", "BILL PAYMENT"],
                "priority": 3
            },
            "Other": {
                "keywords": [],
                "priority": 999  # Default category
            }
        }
    
    def _load_config(self, config_path: Path) -> Dict:
        """Load configuration from JSON file.
        
        Args:
            config_path: Path to JSON config file
            
        Returns:
            Dict: Configuration dictionary
            
        Raises:
            ValueError: If config file is invalid
        """
        try:
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            if 'categories' not in config:
                raise ValueError("Config file must contain 'categories' key")
            
            return config
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in config file: {e}")
    
    def _sort_categories_by_priority(self) -> None:
        """Sort categories by priority (lower priority number = higher priority)."""
        # Convert to list of tuples, sort, then rebuild dict
        items = list(self.categories.items())
        items.sort(key=lambda x: x[1].get('priority', 999))
        
        # Rebuild dict maintaining order (Python 3.7+ preserves insertion order)
        self.categories = {name: config for name, config in items}
    
    def categorize(self, transaction: Transaction) -> str:
        """Categorize a transaction based on description keywords.
        
        Args:
            transaction: Transaction to categorize
            
        Returns:
            str: Category name
        """
        description_upper = transaction.description.upper()
        
        # Check each category in priority order
        for category_name, category_config in self.categories.items():
            # Skip default "Other" category unless no match found
            if category_name == "Other":
                continue
            
            keywords = category_config.get('keywords', [])
            require_negative = category_config.get('require_negative', False)
            
            # Check if transaction matches income category requirement
            if require_negative and transaction.amount >= 0:
                continue
            
            # Check if any keyword matches
            for keyword in keywords:
                if keyword.upper() in description_upper:
                    # Special case: CASH INTEREST should only match Travel for positive amounts
                    # Negative CASH INTEREST should go to Income
                    if category_name == "Travel" and keyword.upper() == "CASH INTEREST" and transaction.amount < 0:
                        continue  # Skip Travel for negative CASH INTEREST, let it match Income instead
                    return category_name
        
        # Default to "Other" if no match
        return "Other"
    
    def _apply_auto_tags(self, transaction: Transaction) -> None:
        """Apply auto-tagging rules to a transaction.
        
        Args:
            transaction: Transaction to tag
        """
        description_upper = transaction.description.upper()
        
        for tag_name, tag_config in self.auto_tagging_rules.items():
            # Check keyword matches
            keywords = tag_config.get('keywords', [])
            keyword_match = any(kw.upper() in description_upper for kw in keywords)
            
            # Check category matches
            categories = tag_config.get('categories', [])
            category_match = transaction.category in categories
            
            # Apply tag if either condition matches
            if keyword_match or category_match:
                if tag_name not in transaction.tags:
                    transaction.tags.append(tag_name)
    
    def categorize_all(self, transactions: List[Transaction]) -> List[Transaction]:
        """Categorize a list of transactions and apply auto-tags.
        
        Args:
            transactions: List of transactions to categorize
            
        Returns:
            List[Transaction]: Transactions with categories and tags assigned
        """
        for transaction in transactions:
            transaction.category = self.categorize(transaction)
            self._apply_auto_tags(transaction)
        
        return transactions
    
    def get_category_list(self) -> List[str]:
        """Get list of all available category names.
        
        Returns:
            List[str]: Category names
        """
        return list(self.categories.keys())

