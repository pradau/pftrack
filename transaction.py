"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Transaction data model for personal finance tracking
Dependencies: Python 3.6+
Usage: Import Transaction class for transaction data representation
"""

from dataclasses import dataclass, field
from datetime import datetime
from typing import List, Optional


@dataclass
class Transaction:
    """Represents a single financial transaction.
    
    A transaction can be from either a chequing account or credit card.
    Amounts are normalized: positive for expenses, negative for income.
    
    Attributes:
        date: Transaction date
        account_type: Type of account ('chequing' or 'visa')
        description: Transaction description/merchant name
        amount: Transaction amount (positive=expense, negative=income)
        category: Assigned category name
        subcategory: Optional subcategory
        credit_card: Credit card number (for Visa transactions only)
        tags: List of tags for additional categorization
        notes: Optional notes or comments about the transaction
        account_id: Optional account identifier for multi-account support
    """
    date: datetime
    account_type: str
    description: str
    amount: float
    category: str = "Other"
    subcategory: Optional[str] = None
    credit_card: Optional[str] = None
    tags: List[str] = field(default_factory=list)
    notes: Optional[str] = None
    account_id: Optional[str] = None
    
    def __post_init__(self) -> None:
        """Validate transaction data after initialization."""
        if self.account_type not in ('chequing', 'visa'):
            raise ValueError(f"Invalid account_type: {self.account_type}. Must be 'chequing' or 'visa'")
        
        if not self.description or not self.description.strip():
            raise ValueError("Transaction description cannot be empty")
    
    def is_expense(self) -> bool:
        """Check if transaction is an expense.
        
        Returns:
            bool: True if amount is positive (expense), False otherwise
        """
        return self.amount > 0
    
    def is_income(self) -> bool:
        """Check if transaction is income.
        
        Returns:
            bool: True if amount is negative (income), False otherwise
        """
        return self.amount < 0
    
    def abs_amount(self) -> float:
        """Get absolute value of transaction amount.
        
        Returns:
            float: Absolute value of amount
        """
        return abs(self.amount)

