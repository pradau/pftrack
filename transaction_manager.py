"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Transaction management for manual entry, editing, and duplicate detection
Dependencies: Python 3.6+
Usage: TransactionManager class to manage manual transactions and detect duplicates
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from transaction import Transaction


class TransactionManager:
    """Manages manual transactions and provides duplicate detection."""
    
    def __init__(self, manual_transactions_path: Path = Path('manual_transactions.json')):
        """Initialize transaction manager.
        
        Args:
            manual_transactions_path: Path to JSON file storing manual transactions
        """
        self.manual_transactions_path = Path(manual_transactions_path)
        self.manual_transactions: List[Dict] = []
        self._load_manual_transactions()
    
    def _load_manual_transactions(self) -> None:
        """Load manual transactions from JSON file."""
        if self.manual_transactions_path.exists():
            try:
                with open(self.manual_transactions_path, 'r', encoding='utf-8') as f:
                    self.manual_transactions = json.load(f)
            except (json.JSONDecodeError, IOError):
                self.manual_transactions = []
        else:
            self.manual_transactions = []
    
    def _save_manual_transactions(self) -> None:
        """Save manual transactions to JSON file."""
        self.manual_transactions_path.parent.mkdir(parents=True, exist_ok=True)
        with open(self.manual_transactions_path, 'w', encoding='utf-8') as f:
            json.dump(self.manual_transactions, f, indent=2, default=str)
    
    def add_transaction(self, date: datetime, account_type: str, description: str,
                       amount: float, category: str = "Other",
                       subcategory: Optional[str] = None,
                       credit_card: Optional[str] = None,
                       tags: Optional[List[str]] = None,
                       notes: Optional[str] = None) -> Dict:
        """Add a manual transaction.
        
        Args:
            date: Transaction date
            account_type: Account type ('chequing' or 'visa')
            description: Transaction description
            amount: Transaction amount
            category: Category name
            subcategory: Optional subcategory
            credit_card: Credit card number (for Visa)
            tags: List of tags
            notes: Optional notes
            
        Returns:
            Dict: Transaction data as stored
        """
        transaction_data = {
            'date': date.isoformat(),
            'account_type': account_type,
            'description': description,
            'amount': amount,
            'category': category,
            'subcategory': subcategory,
            'credit_card': credit_card,
            'tags': tags or [],
            'notes': notes
        }
        
        self.manual_transactions.append(transaction_data)
        self._save_manual_transactions()
        
        return transaction_data
    
    def edit_transaction(self, index: int, **kwargs) -> Dict:
        """Edit an existing manual transaction.
        
        Args:
            index: Index of transaction to edit
            **kwargs: Fields to update
            
        Returns:
            Dict: Updated transaction data
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.manual_transactions):
            raise IndexError(f"Transaction index {index} out of range")
        
        transaction = self.manual_transactions[index]
        transaction.update(kwargs)
        
        # Convert date string back to ISO format if datetime provided
        if 'date' in kwargs and isinstance(kwargs['date'], datetime):
            transaction['date'] = kwargs['date'].isoformat()
        
        self._save_manual_transactions()
        
        return transaction
    
    def delete_transaction(self, index: int) -> None:
        """Delete a manual transaction.
        
        Args:
            index: Index of transaction to delete
            
        Raises:
            IndexError: If index is out of range
        """
        if index < 0 or index >= len(self.manual_transactions):
            raise IndexError(f"Transaction index {index} out of range")
        
        del self.manual_transactions[index]
        self._save_manual_transactions()
    
    def get_manual_transactions(self) -> List[Transaction]:
        """Convert manual transactions to Transaction objects.
        
        Returns:
            List[Transaction]: List of Transaction objects
        """
        transactions = []
        
        for data in self.manual_transactions:
            try:
                date = datetime.fromisoformat(data['date'])
                transaction = Transaction(
                    date=date,
                    account_type=data['account_type'],
                    description=data['description'],
                    amount=data['amount'],
                    category=data.get('category', 'Other'),
                    subcategory=data.get('subcategory'),
                    credit_card=data.get('credit_card'),
                    tags=data.get('tags', []),
                    notes=data.get('notes')
                )
                transactions.append(transaction)
            except (KeyError, ValueError) as e:
                # Skip invalid transactions
                continue
        
        return transactions
    
    def detect_duplicates(self, transactions: List[Transaction],
                         date_tolerance_days: int = 1,
                         amount_tolerance: float = 0.01) -> List[Tuple[Transaction, Transaction]]:
        """Detect potential duplicate transactions.
        
        Matches transactions with same merchant, similar amount, and close dates.
        
        Args:
            transactions: List of transactions to check
            date_tolerance_days: Maximum days difference for duplicate match
            amount_tolerance: Maximum amount difference for duplicate match
            
        Returns:
            List of (transaction1, transaction2) tuples for potential duplicates
        """
        duplicates = []
        
        for i, t1 in enumerate(transactions):
            for t2 in transactions[i+1:]:
                # Check if same merchant (case-insensitive partial match)
                if t1.description.upper() not in t2.description.upper() and \
                   t2.description.upper() not in t1.description.upper():
                    continue
                
                # Check if amounts are similar
                amount_diff = abs(abs(t1.amount) - abs(t2.amount))
                if amount_diff > amount_tolerance:
                    continue
                
                # Check if dates are close
                date_diff = abs((t1.date - t2.date).days)
                if date_diff > date_tolerance_days:
                    continue
                
                duplicates.append((t1, t2))
        
        return duplicates
    
    def merge_transactions(self, transaction1: Transaction,
                          transaction2: Transaction) -> Transaction:
        """Merge two duplicate transactions into one.
        
        Uses data from transaction1, combining tags and notes.
        
        Args:
            transaction1: First transaction (primary)
            transaction2: Second transaction (to merge)
            
        Returns:
            Transaction: Merged transaction
        """
        # Combine tags
        combined_tags = list(set(transaction1.tags + transaction2.tags))
        
        # Combine notes
        combined_notes = None
        if transaction1.notes or transaction2.notes:
            notes_parts = []
            if transaction1.notes:
                notes_parts.append(transaction1.notes)
            if transaction2.notes:
                notes_parts.append(transaction2.notes)
            combined_notes = " | ".join(notes_parts)
        
        # Use transaction1 as base, update tags and notes
        merged = Transaction(
            date=transaction1.date,
            account_type=transaction1.account_type,
            description=transaction1.description,
            amount=transaction1.amount,
            category=transaction1.category,
            subcategory=transaction1.subcategory,
            credit_card=transaction1.credit_card,
            tags=combined_tags,
            notes=combined_notes
        )
        
        return merged
