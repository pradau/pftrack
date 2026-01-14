"""
Author: Perry Radau
Date: 2025-01-27
Brief description: CSV parser for Simplii banking transaction files
Dependencies: Python 3.6+
Usage: parse_debit_csv() and parse_visa_csv() functions to load transaction data
"""

import csv
from datetime import datetime
from pathlib import Path
from typing import List, Optional

from transaction import Transaction


def parse_date(date_str: str) -> datetime:
    """Parse date string in MM/DD/YYYY format.
    
    Args:
        date_str: Date string in MM/DD/YYYY format
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If date string cannot be parsed
    """
    date_str = date_str.strip()
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        raise ValueError(f"Unable to parse date: {date_str}. Expected MM/DD/YYYY format")


def parse_amount(funds_out: str, funds_in: str) -> float:
    """Convert Funds Out/In fields to normalized signed amount.
    
    Positive amount = expense (money going out)
    Negative amount = income (money coming in)
    
    Args:
        funds_out: Funds Out field from CSV (may be empty)
        funds_in: Funds In field from CSV (may be empty)
        
    Returns:
        float: Normalized amount (positive for expenses, negative for income)
    """
    funds_out = funds_out.strip() if funds_out else ""
    funds_in = funds_in.strip() if funds_in else ""
    
    if funds_out:
        try:
            return float(funds_out)
        except ValueError:
            return 0.0
    elif funds_in:
        try:
            return -float(funds_in)  # Negative for income
        except ValueError:
            return 0.0
    else:
        return 0.0


def parse_debit_csv(file_path: Path) -> List[Transaction]:
    """Parse Simplii chequing account CSV file.
    
    Expected format:
    Date, Transaction Details, Funds Out, Funds In
    
    Args:
        file_path: Path to the debit CSV file
        
    Returns:
        List[Transaction]: List of parsed transactions
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If CSV format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Debit CSV file not found: {file_path}")
    
    transactions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Normalize row keys by stripping whitespace
                normalized_row = {k.strip(): v for k, v in row.items()}
                
                date_str = normalized_row.get('Date', '').strip()
                if not date_str:
                    continue
                
                date = parse_date(date_str)
                description = normalized_row.get('Transaction Details', '').strip()
                funds_out = normalized_row.get('Funds Out', '').strip()
                funds_in = normalized_row.get('Funds In', '').strip()
                
                amount = parse_amount(funds_out, funds_in)
                
                if amount == 0.0 and not description:
                    continue
                
                transaction = Transaction(
                    date=date,
                    account_type='chequing',
                    description=description,
                    amount=amount
                )
                transactions.append(transaction)
                
            except (ValueError, KeyError) as e:
                # Log error but continue processing
                print(f"Warning: Skipping row {row_num} in {file_path.name}: {e}")
                continue
    
    return transactions


def parse_visa_csv(file_path: Path) -> List[Transaction]:
    """Parse Simplii Visa credit card CSV file.
    
    Expected format:
    Date, Transaction Details, Funds Out, Funds In, Credit Card
    
    Args:
        file_path: Path to the Visa CSV file
        
    Returns:
        List[Transaction]: List of parsed transactions
        
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If CSV format is invalid
    """
    if not file_path.exists():
        raise FileNotFoundError(f"Visa CSV file not found: {file_path}")
    
    transactions = []
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Normalize row keys by stripping whitespace
                normalized_row = {k.strip(): v for k, v in row.items()}
                
                date_str = normalized_row.get('Date', '').strip()
                if not date_str:
                    continue
                
                date = parse_date(date_str)
                description = normalized_row.get('Transaction Details', '').strip()
                # Remove quotes if present
                if description.startswith('"') and description.endswith('"'):
                    description = description[1:-1]
                
                funds_out = normalized_row.get('Funds Out', '').strip()
                funds_in = normalized_row.get('Funds In', '').strip()
                credit_card = normalized_row.get('Credit Card', '').strip()
                
                amount = parse_amount(funds_out, funds_in)
                
                # Skip payment transactions (they appear in both accounts)
                if amount < 0 and 'PAYMENT' in description.upper():
                    continue
                
                if amount == 0.0 and not description:
                    continue
                
                transaction = Transaction(
                    date=date,
                    account_type='visa',
                    description=description,
                    amount=amount,
                    credit_card=credit_card if credit_card else None
                )
                transactions.append(transaction)
                
            except (ValueError, KeyError) as e:
                # Log error but continue processing
                print(f"Warning: Skipping row {row_num} in {file_path.name}: {e}")
                continue
    
    return transactions

