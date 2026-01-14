"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Recurring transaction detection and prediction
Dependencies: Python 3.6+
Usage: RecurringDetector class to identify and predict recurring transactions
"""

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

from transaction import Transaction


class RecurringTransaction:
    """Represents a detected recurring transaction pattern."""
    
    def __init__(self, merchant: str, average_amount: float, 
                 interval_days: float, last_date: datetime, count: int):
        """Initialize recurring transaction pattern.
        
        Args:
            merchant: Merchant name
            average_amount: Average transaction amount
            interval_days: Average interval between transactions in days
            last_date: Date of most recent transaction
            count: Number of occurrences detected
        """
        self.merchant = merchant
        self.average_amount = average_amount
        self.interval_days = interval_days
        self.last_date = last_date
        self.count = count
    
    def predict_next(self) -> datetime:
        """Predict date of next expected transaction.
        
        Returns:
            datetime: Predicted next transaction date
        """
        return self.last_date + timedelta(days=self.interval_days)
    
    def is_due(self, current_date: Optional[datetime] = None) -> bool:
        """Check if next transaction is due.
        
        Args:
            current_date: Current date (defaults to today)
            
        Returns:
            bool: True if transaction is due
        """
        if current_date is None:
            current_date = datetime.now()
        
        next_date = self.predict_next()
        return current_date >= next_date


class RecurringDetector:
    """Detects recurring transaction patterns and predicts future transactions."""
    
    def __init__(self, transactions: List[Transaction]):
        """Initialize recurring detector.
        
        Args:
            transactions: List of transactions to analyze
        """
        self.transactions = transactions
    
    def detect_recurring(self, min_occurrences: int = 3,
                        amount_tolerance: float = 0.1,
                        merchant_similarity: float = 0.8) -> List[RecurringTransaction]:
        """Detect recurring transaction patterns.
        
        Args:
            min_occurrences: Minimum number of occurrences to consider recurring
            amount_tolerance: Maximum relative difference in amounts (0.1 = 10%)
            merchant_similarity: Minimum similarity for merchant matching (0.8 = 80%)
            
        Returns:
            List of RecurringTransaction objects
        """
        # Group transactions by merchant (normalized)
        merchant_groups = defaultdict(list)
        
        for transaction in self.transactions:
            if transaction.is_expense():
                # Normalize merchant name (uppercase, remove extra spaces)
                merchant = ' '.join(transaction.description.upper().split())
                merchant_groups[merchant].append(transaction)
        
        recurring = []
        
        for merchant, transactions in merchant_groups.items():
            if len(transactions) < min_occurrences:
                continue
            
            # Sort by date
            transactions.sort(key=lambda t: t.date)
            
            # Calculate average amount
            amounts = [abs(t.amount) for t in transactions]
            avg_amount = sum(amounts) / len(amounts)
            
            # Check if amounts are similar (within tolerance)
            amount_variance = max(amounts) / min(amounts) if min(amounts) > 0 else float('inf')
            if amount_variance > (1 + amount_tolerance):
                continue
            
            # Calculate average interval
            intervals = []
            for i in range(len(transactions) - 1):
                interval = (transactions[i+1].date - transactions[i].date).days
                if interval > 0:  # Ignore same-day transactions
                    intervals.append(interval)
            
            if not intervals:
                continue
            
            avg_interval = sum(intervals) / len(intervals)
            
            # Check if intervals are relatively consistent (within 50% variance)
            if intervals:
                interval_variance = max(intervals) / min(intervals) if min(intervals) > 0 else float('inf')
                if interval_variance > 2.0:  # Allow up to 2x variation
                    continue
            
            recurring_transaction = RecurringTransaction(
                merchant=merchant,
                average_amount=avg_amount,
                interval_days=avg_interval,
                last_date=transactions[-1].date,
                count=len(transactions)
            )
            
            recurring.append(recurring_transaction)
        
        return recurring
    
    def predict_future(self, recurring_transactions: List[RecurringTransaction],
                      months_ahead: int = 3) -> List[Tuple[RecurringTransaction, datetime]]:
        """Predict future recurring transactions.
        
        Args:
            recurring_transactions: List of detected recurring transactions
            months_ahead: Number of months to predict ahead
            
        Returns:
            List of (RecurringTransaction, predicted_date) tuples
        """
        predictions = []
        end_date = datetime.now() + timedelta(days=months_ahead * 30)
        
        for recurring in recurring_transactions:
            next_date = recurring.predict_next()
            current_date = next_date
            
            while current_date <= end_date:
                predictions.append((recurring, current_date))
                current_date += timedelta(days=recurring.interval_days)
        
        # Sort by date
        predictions.sort(key=lambda x: x[1])
        
        return predictions
    
    def find_missing(self, recurring_transactions: List[RecurringTransaction],
                    current_date: Optional[datetime] = None) -> List[RecurringTransaction]:
        """Find recurring transactions that are overdue.
        
        Args:
            recurring_transactions: List of detected recurring transactions
            current_date: Current date (defaults to today)
            
        Returns:
            List of overdue RecurringTransaction objects
        """
        if current_date is None:
            current_date = datetime.now()
        
        missing = []
        
        for recurring in recurring_transactions:
            if recurring.is_due(current_date):
                # Check if transaction actually occurred
                expected_date = recurring.predict_next()
                tolerance_days = recurring.interval_days * 0.5  # 50% tolerance
                
                found = False
                for transaction in self.transactions:
                    if transaction.is_expense():
                        merchant_match = recurring.merchant.upper() in transaction.description.upper()
                        date_diff = abs((transaction.date - expected_date).days)
                        amount_diff = abs(abs(transaction.amount) - recurring.average_amount) / recurring.average_amount
                        
                        if merchant_match and date_diff <= tolerance_days and amount_diff <= 0.2:
                            found = True
                            break
                
                if not found:
                    missing.append(recurring)
        
        return missing
