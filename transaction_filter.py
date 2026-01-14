"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Transaction filtering and search functionality
Dependencies: Python 3.6+
Usage: TransactionFilter class to filter and search transactions
"""

from datetime import datetime
from typing import List, Optional

from transaction import Transaction


class TransactionFilter:
    """Provides filtering and search capabilities for transactions."""
    
    @staticmethod
    def filter_by_category(transactions: List[Transaction], 
                          category: str) -> List[Transaction]:
        """Filter transactions by category.
        
        Args:
            transactions: List of transactions to filter
            category: Category name to filter by
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        return [t for t in transactions if t.category == category]
    
    @staticmethod
    def filter_by_account_type(transactions: List[Transaction],
                               account_type: str) -> List[Transaction]:
        """Filter transactions by account type.
        
        Args:
            transactions: List of transactions to filter
            account_type: Account type ('chequing' or 'visa')
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        return [t for t in transactions if t.account_type == account_type]
    
    @staticmethod
    def filter_by_date_range(transactions: List[Transaction],
                             start_date: Optional[datetime] = None,
                             end_date: Optional[datetime] = None) -> List[Transaction]:
        """Filter transactions by date range.
        
        Args:
            transactions: List of transactions to filter
            start_date: Start date (inclusive). If None, no start limit.
            end_date: End date (inclusive). If None, no end limit.
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        filtered = transactions
        
        if start_date:
            filtered = [t for t in filtered if t.date >= start_date]
        
        if end_date:
            filtered = [t for t in filtered if t.date <= end_date]
        
        return filtered
    
    @staticmethod
    def filter_by_amount_range(transactions: List[Transaction],
                              min_amount: Optional[float] = None,
                              max_amount: Optional[float] = None) -> List[Transaction]:
        """Filter transactions by amount range.
        
        Args:
            transactions: List of transactions to filter
            min_amount: Minimum amount (inclusive). If None, no minimum.
            max_amount: Maximum amount (inclusive). If None, no maximum.
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        filtered = transactions
        
        if min_amount is not None:
            filtered = [t for t in filtered if abs(t.amount) >= min_amount]
        
        if max_amount is not None:
            filtered = [t for t in filtered if abs(t.amount) <= max_amount]
        
        return filtered
    
    @staticmethod
    def filter_by_merchant(transactions: List[Transaction],
                          merchant: str) -> List[Transaction]:
        """Filter transactions by merchant name (case-insensitive partial match).
        
        Args:
            transactions: List of transactions to filter
            merchant: Merchant name to search for
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        merchant_upper = merchant.upper()
        return [t for t in transactions if merchant_upper in t.description.upper()]
    
    @staticmethod
    def search_by_keyword(transactions: List[Transaction],
                         keyword: str) -> List[Transaction]:
        """Search transactions by keyword in description (case-insensitive).
        
        Args:
            transactions: List of transactions to search
            keyword: Keyword to search for in transaction descriptions
            
        Returns:
            List[Transaction]: Matching transactions
        """
        keyword_upper = keyword.upper()
        return [t for t in transactions if keyword_upper in t.description.upper()]
    
    @staticmethod
    def filter_all(transactions: List[Transaction],
                   category: Optional[str] = None,
                   account_type: Optional[str] = None,
                   start_date: Optional[datetime] = None,
                   end_date: Optional[datetime] = None,
                   min_amount: Optional[float] = None,
                   max_amount: Optional[float] = None,
                   merchant: Optional[str] = None,
                   search: Optional[str] = None) -> List[Transaction]:
        """Apply all specified filters to transactions.
        
        Args:
            transactions: List of transactions to filter
            category: Category name to filter by
            account_type: Account type to filter by
            start_date: Start date (inclusive)
            end_date: End date (inclusive)
            min_amount: Minimum amount (inclusive)
            max_amount: Maximum amount (inclusive)
            merchant: Merchant name to filter by
            search: Keyword to search for in descriptions
            
        Returns:
            List[Transaction]: Filtered transactions
        """
        filtered = transactions
        
        if category:
            filtered = TransactionFilter.filter_by_category(filtered, category)
        
        if account_type:
            filtered = TransactionFilter.filter_by_account_type(filtered, account_type)
        
        if start_date or end_date:
            filtered = TransactionFilter.filter_by_date_range(filtered, start_date, end_date)
        
        if min_amount is not None or max_amount is not None:
            filtered = TransactionFilter.filter_by_amount_range(filtered, min_amount, max_amount)
        
        if merchant:
            filtered = TransactionFilter.filter_by_merchant(filtered, merchant)
        
        if search:
            filtered = TransactionFilter.search_by_keyword(filtered, search)
        
        return filtered
