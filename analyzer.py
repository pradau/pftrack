"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Spending analysis engine for transaction data
Dependencies: Python 3.6+
Usage: SpendingAnalyzer class to analyze categorized transactions
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from budget import BudgetManager
from transaction import Transaction


class SpendingAnalyzer:
    """Analyzes spending patterns from categorized transactions."""
    
    def __init__(self, transactions: List[Transaction]):
        """Initialize analyzer with transaction data.
        
        Args:
            transactions: List of categorized transactions
        """
        self.transactions = transactions
    
    def filter_by_date_range(self, start_date: Optional[datetime] = None, 
                            end_date: Optional[datetime] = None) -> List[Transaction]:
        """Filter transactions by date range.
        
        Args:
            start_date: Start date (inclusive). If None, no start limit.
            end_date: End date (inclusive). If None, no end limit.
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        filtered = self.transactions
        
        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]
        
        if end_date:
            filtered = [t for t in filtered if t.date <= end_date]
        
        return filtered
    
    def monthly_summary(self, start_date: Optional[datetime] = None,
                       end_date: Optional[datetime] = None) -> Dict[str, Dict[str, float]]:
        """Calculate monthly spending summaries by category.
        
        Format: {year-month: {category: total_amount}}
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dict mapping year-month strings to category totals
        """
        transactions = self.filter_by_date_range(start_date, end_date)
        
        monthly_data = defaultdict(lambda: defaultdict(float))
        
        for transaction in transactions:
            if transaction.is_expense():
                year_month = transaction.date.strftime("%Y-%m")
                monthly_data[year_month][transaction.category] += transaction.amount
        
        # Convert nested defaultdicts to regular dicts
        return {month: dict(categories) for month, categories in monthly_data.items()}
    
    def category_totals(self, start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> Dict[str, float]:
        """Calculate total spending per category.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dict mapping category names to total amounts
        """
        transactions = self.filter_by_date_range(start_date, end_date)
        
        totals = defaultdict(float)
        
        for transaction in transactions:
            if transaction.is_expense():
                totals[transaction.category] += transaction.amount
        
        return dict(totals)
    
    def spending_trends(self) -> Dict[str, List[Tuple[str, float]]]:
        """Calculate month-over-month spending trends by category.
        
        Returns:
            Dict mapping category names to list of (year-month, amount) tuples
        """
        monthly_data = self.monthly_summary()
        
        trends = defaultdict(list)
        
        for year_month in sorted(monthly_data.keys()):
            for category, amount in monthly_data[year_month].items():
                trends[category].append((year_month, amount))
        
        return dict(trends)
    
    def top_merchants(self, limit: int = 20, start_date: Optional[datetime] = None,
                     end_date: Optional[datetime] = None) -> List[Tuple[str, float, int]]:
        """Get top merchants by total spending amount.
        
        Args:
            limit: Maximum number of merchants to return
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            List of (merchant_name, total_amount, transaction_count) tuples,
            sorted by total amount descending
        """
        transactions = self.filter_by_date_range(start_date, end_date)
        
        merchant_totals = defaultdict(lambda: {'amount': 0.0, 'count': 0})
        
        for transaction in transactions:
            if transaction.is_expense():
                merchant = transaction.description
                merchant_totals[merchant]['amount'] += transaction.amount
                merchant_totals[merchant]['count'] += 1
        
        # Convert to list of tuples and sort by amount
        top_merchants = [
            (merchant, data['amount'], data['count'])
            for merchant, data in merchant_totals.items()
        ]
        
        top_merchants.sort(key=lambda x: x[1], reverse=True)
        
        return top_merchants[:limit]
    
    def income_vs_expenses(self, start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> Dict[str, float]:
        """Calculate total income and expenses.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dict with 'income' (positive), 'expenses' (positive), and 'net' keys
        """
        transactions = self.filter_by_date_range(start_date, end_date)
        
        total_income = 0.0
        total_expenses = 0.0
        
        for transaction in transactions:
            if transaction.is_income():
                total_income += abs(transaction.amount)
            elif transaction.is_expense():
                total_expenses += transaction.amount
        
        return {
            'income': total_income,
            'expenses': total_expenses,
            'net': total_income - total_expenses
        }
    
    def get_all_transactions(self) -> List[Transaction]:
        """Get all transactions sorted by date.
        
        Returns:
            List[Transaction]: Transactions sorted by date (oldest first)
        """
        return sorted(self.transactions, key=lambda t: t.date)
    
    def budget_vs_actual(self, budget_manager: BudgetManager,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> Dict[str, Dict[str, float]]:
        """Compare actual spending to budgets for each category.
        
        Args:
            budget_manager: BudgetManager instance with budget data
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dict mapping category names to dict with keys:
            - 'budget': Budget amount for period
            - 'actual': Actual spending amount
            - 'difference': Budget minus actual (positive = under budget)
            - 'utilization': Percentage of budget used (0-100+)
        """
        actual_spending = self.category_totals(start_date, end_date)
        budget_comparison = {}
        
        # Use start/end dates or default to all transactions
        period_start = start_date if start_date else min(t.date for t in self.transactions) if self.transactions else datetime.now()
        period_end = end_date if end_date else max(t.date for t in self.transactions) if self.transactions else datetime.now()
        
        # Get all categories that have budgets or actual spending
        all_categories = set(actual_spending.keys())
        all_categories.update(budget_manager.get_all_categories_with_budgets())
        
        for category in all_categories:
            budget_amount = budget_manager.get_budget_for_period(category, period_start, period_end)
            actual_amount = actual_spending.get(category, 0.0)
            difference = budget_amount - actual_amount
            
            utilization = 0.0
            if budget_amount > 0:
                utilization = (actual_amount / budget_amount) * 100.0
            
            budget_comparison[category] = {
                'budget': budget_amount,
                'actual': actual_amount,
                'difference': difference,
                'utilization': utilization
            }
        
        return budget_comparison
    
    def average_monthly_spending(self, category: str,
                                 start_date: Optional[datetime] = None,
                                 end_date: Optional[datetime] = None) -> float:
        """Calculate average monthly spending for a category.
        
        Args:
            category: Category name
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            float: Average monthly spending amount
        """
        monthly_data = self.monthly_summary(start_date, end_date)
        
        if not monthly_data:
            return 0.0
        
        total = 0.0
        count = 0
        
        for month_data in monthly_data.values():
            if category in month_data:
                total += month_data[category]
                count += 1
        
        return total / count if count > 0 else 0.0
    
    def spending_velocity(self, category: str, period_days: int = 30,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> float:
        """Calculate spending velocity (daily rate) for a category.
        
        Args:
            category: Category name
            period_days: Number of days to calculate velocity over
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            float: Daily spending rate
        """
        transactions = self.filter_by_date_range(start_date, end_date)
        category_transactions = [t for t in transactions 
                                if t.category == category and t.is_expense()]
        
        if not category_transactions:
            return 0.0
        
        # Use actual date range if provided, otherwise use period_days
        if start_date and end_date:
            days = (end_date - start_date).days + 1
        else:
            days = period_days
        
        total = sum(t.amount for t in category_transactions)
        return total / days if days > 0 else 0.0
    
    def category_comparison(self, categories: List[str],
                           start_date: Optional[datetime] = None,
                           end_date: Optional[datetime] = None) -> Dict[str, float]:
        """Compare spending across multiple categories.
        
        Args:
            categories: List of category names to compare
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Dict mapping category names to total amounts
        """
        all_totals = self.category_totals(start_date, end_date)
        return {cat: all_totals.get(cat, 0.0) for cat in categories}
    
    def spending_forecast(self, category: str, months: int = 3,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> float:
        """Project future spending for a category based on historical average.
        
        Args:
            category: Category name
            months: Number of months to forecast
            start_date: Start date filter for historical data (inclusive)
            end_date: End date filter for historical data (inclusive)
            
        Returns:
            float: Forecasted spending amount
        """
        avg_monthly = self.average_monthly_spending(category, start_date, end_date)
        return avg_monthly * months
    
    def seasonal_patterns(self) -> Dict[str, Dict[str, float]]:
        """Identify seasonal spending patterns by category.
        
        Groups spending by month of year to identify seasonal trends.
        
        Returns:
            Dict mapping category names to dict of month names to average amounts
        """
        transactions = [t for t in self.transactions if t.is_expense()]
        
        # Group by category and month
        category_month_totals = defaultdict(lambda: defaultdict(lambda: {'total': 0.0, 'count': 0}))
        
        for transaction in transactions:
            month_name = transaction.date.strftime("%B")
            category_month_totals[transaction.category][month_name]['total'] += transaction.amount
            category_month_totals[transaction.category][month_name]['count'] += 1
        
        # Calculate averages
        patterns = {}
        month_order = ['January', 'February', 'March', 'April', 'May', 'June',
                      'July', 'August', 'September', 'October', 'November', 'December']
        
        for category, month_data in category_month_totals.items():
            patterns[category] = {}
            for month in month_order:
                if month in month_data:
                    data = month_data[month]
                    # Average per occurrence (could be multiple years)
                    patterns[category][month] = data['total'] / max(data['count'], 1)
                else:
                    patterns[category][month] = 0.0
        
        return patterns
    
    def budget_remaining(self, budget_manager: BudgetManager, category: str,
                        start_date: Optional[datetime] = None,
                        end_date: Optional[datetime] = None) -> float:
        """Calculate remaining budget for a category.
        
        Args:
            budget_manager: BudgetManager instance with budget data
            category: Category name
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            float: Remaining budget amount (negative if over budget)
        """
        period_start = start_date if start_date else min(t.date for t in self.transactions) if self.transactions else datetime.now()
        period_end = end_date if end_date else max(t.date for t in self.transactions) if self.transactions else datetime.now()
        
        budget_amount = budget_manager.get_budget_for_period(category, period_start, period_end)
        actual_spending = self.category_totals(start_date, end_date).get(category, 0.0)
        
        return budget_amount - actual_spending
    
    def budget_utilization(self, budget_manager: BudgetManager, category: str,
                          start_date: Optional[datetime] = None,
                          end_date: Optional[datetime] = None) -> float:
        """Calculate budget utilization percentage for a category.
        
        Args:
            budget_manager: BudgetManager instance with budget data
            category: Category name
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            float: Budget utilization percentage (0-100+, where 100+ means over budget)
        """
        period_start = start_date if start_date else min(t.date for t in self.transactions) if self.transactions else datetime.now()
        period_end = end_date if end_date else max(t.date for t in self.transactions) if self.transactions else datetime.now()
        
        budget_amount = budget_manager.get_budget_for_period(category, period_start, period_end)
        if budget_amount == 0:
            return 0.0
        
        actual_spending = self.category_totals(start_date, end_date).get(category, 0.0)
        return (actual_spending / budget_amount) * 100.0

