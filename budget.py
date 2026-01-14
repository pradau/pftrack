"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Budget management system for personal finance tracking
Dependencies: Python 3.6+
Usage: BudgetManager class to load and manage budget configurations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Optional


class BudgetManager:
    """Manages budget configurations and provides budget data access.
    
    Supports monthly and annual budgets per category. Budgets are stored
    in JSON format for easy editing.
    """
    
    def __init__(self, budget_path: Optional[Path] = None):
        """Initialize budget manager with budget configuration.
        
        Args:
            budget_path: Path to JSON budget configuration file.
                        If None, creates empty budget manager.
        """
        self.monthly_budgets: Dict[str, float] = {}
        self.annual_budgets: Dict[str, float] = {}
        self.category_budgets: Dict[str, Dict[str, float]] = {}
        
        if budget_path and budget_path.exists():
            self.load_budgets(budget_path)
    
    def load_budgets(self, budget_path: Path) -> None:
        """Load budgets from JSON configuration file.
        
        Args:
            budget_path: Path to JSON budget file
            
        Raises:
            ValueError: If budget file is invalid
        """
        try:
            with open(budget_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            self.monthly_budgets = config.get('monthly_budgets', {})
            self.annual_budgets = config.get('annual_budgets', {})
            self.category_budgets = config.get('category_budgets', {})
            
            # Validate budget values are non-negative
            for budgets in [self.monthly_budgets, self.annual_budgets]:
                for category, amount in budgets.items():
                    if amount < 0:
                        raise ValueError(f"Budget amount for {category} cannot be negative: {amount}")
            
            for category_budgets in self.category_budgets.values():
                for period, amount in category_budgets.items():
                    if amount < 0:
                        raise ValueError(f"Budget amount cannot be negative: {amount}")
                        
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in budget file: {e}")
        except KeyError as e:
            raise ValueError(f"Missing required key in budget file: {e}")
    
    def get_monthly_budget(self, category: str) -> float:
        """Get monthly budget for a category.
        
        Args:
            category: Category name
            
        Returns:
            float: Monthly budget amount (0.0 if not set)
        """
        return self.monthly_budgets.get(category, 0.0)
    
    def get_annual_budget(self, category: str) -> float:
        """Get annual budget for a category.
        
        Args:
            category: Category name
            
        Returns:
            float: Annual budget amount (0.0 if not set)
        """
        return self.annual_budgets.get(category, 0.0)
    
    def get_budget_for_period(self, category: str, start_date: datetime, 
                              end_date: datetime) -> float:
        """Calculate budget for a category over a date range.
        
        Uses monthly budgets if available, otherwise annual budgets prorated.
        
        Args:
            category: Category name
            start_date: Start date of period
            end_date: End date of period
            
        Returns:
            float: Budget amount for the period
        """
        # Check for monthly budget first
        monthly_budget = self.get_monthly_budget(category)
        if monthly_budget > 0:
            # Calculate number of months (including partial months)
            days_diff = (end_date - start_date).days + 1
            months = days_diff / 30.44  # Average days per month
            return monthly_budget * months
        
        # Check for annual budget
        annual_budget = self.get_annual_budget(category)
        if annual_budget > 0:
            # Prorate annual budget for the period
            days_diff = (end_date - start_date).days + 1
            days_in_year = 365.25
            return annual_budget * (days_diff / days_in_year)
        
        # Check category-specific budgets
        if category in self.category_budgets:
            # For now, return first budget found (could be enhanced)
            budgets = self.category_budgets[category]
            if budgets:
                return list(budgets.values())[0]
        
        return 0.0
    
    def has_budget(self, category: str) -> bool:
        """Check if a category has any budget defined.
        
        Args:
            category: Category name
            
        Returns:
            bool: True if category has a budget, False otherwise
        """
        return (category in self.monthly_budgets or 
                category in self.annual_budgets or
                category in self.category_budgets)
    
    def get_all_categories_with_budgets(self) -> list:
        """Get list of all categories that have budgets defined.
        
        Returns:
            list: List of category names with budgets
        """
        categories = set()
        categories.update(self.monthly_budgets.keys())
        categories.update(self.annual_budgets.keys())
        categories.update(self.category_budgets.keys())
        return sorted(categories)
