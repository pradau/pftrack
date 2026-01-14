"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Data import/export and migration utilities
Dependencies: Python 3.6+
Usage: DataManager class for data management operations
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from transaction import Transaction


class DataManager:
    """Manages data import, export, and migration operations."""
    
    def __init__(self, output_dir: Path = Path('data')):
        """Initialize data manager.
        
        Args:
            output_dir: Directory for data operations
        """
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def export_transactions_to_csv(self, transactions: List[Transaction],
                                  filename: str = "exported_transactions.csv") -> Path:
        """Export transactions to CSV format.
        
        Args:
            transactions: List of transactions to export
            filename: Output filename
            
        Returns:
            Path to generated CSV file
        """
        import csv
        
        output_path = self.output_dir / filename
        transactions = sorted(transactions, key=lambda t: t.date)
        
        with open(output_path, 'w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow([
                'Date', 'Account Type', 'Description', 'Amount',
                'Category', 'Subcategory', 'Credit Card', 'Tags', 'Notes'
            ])
            
            for t in transactions:
                writer.writerow([
                    t.date.strftime("%Y-%m-%d"),
                    t.account_type,
                    t.description,
                    f"{t.amount:.2f}",
                    t.category,
                    t.subcategory or "",
                    t.credit_card or "",
                    ", ".join(t.tags),
                    t.notes or ""
                ])
        
        return output_path
    
    def export_transactions_to_json(self, transactions: List[Transaction],
                                   filename: str = "exported_transactions.json") -> Path:
        """Export transactions to JSON format.
        
        Args:
            transactions: List of transactions to export
            filename: Output filename
            
        Returns:
            Path to generated JSON file
        """
        output_path = self.output_dir / filename
        transactions = sorted(transactions, key=lambda t: t.date)
        
        transaction_data = []
        for t in transactions:
            data = {
                'date': t.date.isoformat(),
                'account_type': t.account_type,
                'description': t.description,
                'amount': t.amount,
                'category': t.category,
                'subcategory': t.subcategory,
                'credit_card': t.credit_card,
                'tags': t.tags,
                'notes': t.notes
            }
            transaction_data.append(data)
        
        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump({
                'transactions': transaction_data,
                'count': len(transaction_data),
                'export_date': datetime.now().isoformat()
            }, f, indent=2, default=str)
        
        return output_path
    
    def import_transactions_from_json(self, json_path: Path) -> List[Transaction]:
        """Import transactions from JSON file.
        
        Args:
            json_path: Path to JSON file
            
        Returns:
            List of Transaction objects
            
        Raises:
            ValueError: If JSON file is invalid
        """
        try:
            with open(json_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            transactions = []
            transaction_list = data.get('transactions', [])
            
            for t_data in transaction_list:
                try:
                    date = datetime.fromisoformat(t_data['date'])
                    transaction = Transaction(
                        date=date,
                        account_type=t_data['account_type'],
                        description=t_data['description'],
                        amount=t_data['amount'],
                        category=t_data.get('category', 'Other'),
                        subcategory=t_data.get('subcategory'),
                        credit_card=t_data.get('credit_card'),
                        tags=t_data.get('tags', []),
                        notes=t_data.get('notes')
                    )
                    transactions.append(transaction)
                except (KeyError, ValueError) as e:
                    # Skip invalid transactions
                    continue
            
            return transactions
            
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON file: {e}")
    
    def backup_data(self, transactions: List[Transaction],
                   backup_dir: Optional[Path] = None) -> Path:
        """Create a backup of transaction data.
        
        Args:
            transactions: List of transactions to backup
            backup_dir: Directory for backup (defaults to data/backups)
            
        Returns:
            Path to backup file
        """
        if backup_dir is None:
            backup_dir = self.output_dir / 'backups'
        backup_dir = Path(backup_dir)
        backup_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = backup_dir / f"backup_{timestamp}.json"
        
        return self.export_transactions_to_json(transactions, str(backup_path.name))
    
    def restore_from_backup(self, backup_path: Path) -> List[Transaction]:
        """Restore transactions from a backup file.
        
        Args:
            backup_path: Path to backup JSON file
            
        Returns:
            List of Transaction objects
        """
        return self.import_transactions_from_json(backup_path)
