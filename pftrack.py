#!/usr/bin/env python3
"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Main entry point for personal finance tracking system
Dependencies: Python 3.6+
Usage: python pftrack.py [options]
"""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from typing import Optional

from analyzer import SpendingAnalyzer
from budget import BudgetManager
from categorizer import CategoryClassifier
from csv_parser import parse_debit_csv, parse_visa_csv
from html_reporter import HTMLReportGenerator
from interactive_categorizer import InteractiveCategorizer
from reporter import ReportGenerator
from transaction_filter import TransactionFilter


def parse_args() -> argparse.Namespace:
    """Parse command-line arguments.
    
    Returns:
        argparse.Namespace: Parsed arguments
    """
    parser = argparse.ArgumentParser(
        description='Personal Finance Tracker - Analyze Simplii banking transactions'
    )
    
    parser.add_argument(
        '--debit-csv',
        type=Path,
        default=Path('data/SIMPLII -chequing.csv'),
        help='Path to Simplii debit/chequing CSV file (default: data/SIMPLII -chequing.csv)'
    )
    
    parser.add_argument(
        '--visa-csv',
        type=Path,
        default=Path('data/SIMPLII -visa.csv'),
        help='Path to Simplii Visa CSV file (default: data/SIMPLII -visa.csv)'
    )
    
    parser.add_argument(
        '--output-dir',
        type=Path,
        default=Path('reports'),
        help='Directory for output CSV reports (default: reports)'
    )
    
    parser.add_argument(
        '--config',
        type=Path,
        default=None,
        help='Path to JSON configuration file for categories (optional)'
    )
    
    parser.add_argument(
        '--start-date',
        type=str,
        default=None,
        help='Start date filter (MM/DD/YYYY format, inclusive)'
    )
    
    parser.add_argument(
        '--end-date',
        type=str,
        default=None,
        help='End date filter (MM/DD/YYYY format, inclusive)'
    )
    
    parser.add_argument(
        '--html',
        action='store_true',
        help='Generate HTML reports in addition to CSV reports'
    )
    
    parser.add_argument(
        '--html-only',
        action='store_true',
        help='Generate only HTML reports (skip CSV reports)'
    )
    
    parser.add_argument(
        '--qa',
        action='store_true',
        help='Generate QA comparison report for reviewing transaction categorizations'
    )
    
    parser.add_argument(
        '--budget-config',
        type=Path,
        default=None,
        help='Path to budget configuration JSON file (default: budgets.json)'
    )
    
    parser.add_argument(
        '--category',
        type=str,
        default=None,
        help='Filter transactions by category'
    )
    
    parser.add_argument(
        '--merchant',
        type=str,
        default=None,
        help='Filter transactions by merchant name'
    )
    
    parser.add_argument(
        '--min-amount',
        type=float,
        default=None,
        help='Filter transactions with minimum amount (inclusive)'
    )
    
    parser.add_argument(
        '--max-amount',
        type=float,
        default=None,
        help='Filter transactions with maximum amount (inclusive)'
    )
    
    parser.add_argument(
        '--search',
        type=str,
        default=None,
        help='Search transactions by keyword in description'
    )
    
    parser.add_argument(
        '--interactive',
        action='store_true',
        help='Interactive categorization mode - review and re-categorize transactions'
    )
    
    return parser.parse_args()


def parse_date_arg(date_str: str) -> datetime:
    """Parse date argument from command line.
    
    Args:
        date_str: Date string in MM/DD/YYYY format
        
    Returns:
        datetime: Parsed datetime object
        
    Raises:
        ValueError: If date cannot be parsed
    """
    try:
        return datetime.strptime(date_str, "%m/%d/%Y")
    except ValueError:
        raise ValueError(f"Invalid date format: {date_str}. Expected MM/DD/YYYY")


def main() -> int:
    """Main application entry point.
    
    Returns:
        int: Exit code (0 for success, non-zero for error)
    """
    args = parse_args()
    
    try:
        # Parse date filters
        start_date = None
        end_date = None
        
        if args.start_date:
            start_date = parse_date_arg(args.start_date)
        
        if args.end_date:
            end_date = parse_date_arg(args.end_date)
        
        # Load and parse CSV files
        print("Loading transaction data...")
        debit_transactions = parse_debit_csv(args.debit_csv)
        visa_transactions = parse_visa_csv(args.visa_csv)
        
        all_transactions = debit_transactions + visa_transactions
        print(f"Loaded {len(debit_transactions)} debit transactions and "
              f"{len(visa_transactions)} Visa transactions")
        
        # Apply date filters if specified (for both interactive and normal modes)
        if start_date or end_date:
            all_transactions = TransactionFilter.filter_by_date_range(
                all_transactions,
                start_date=start_date,
                end_date=end_date
            )
            if start_date or end_date:
                print(f"Filtered to {len(all_transactions)} transactions in date range")
        
        # Apply other transaction filters if specified (only for non-interactive mode)
        if not args.interactive and (args.category or args.merchant or args.min_amount is not None or
           args.max_amount is not None or args.search):
            print("Applying transaction filters...")
            all_transactions = TransactionFilter.filter_all(
                all_transactions,
                category=args.category,
                merchant=args.merchant,
                min_amount=args.min_amount,
                max_amount=args.max_amount,
                search=args.search,
                start_date=None,  # Already filtered above
                end_date=None     # Already filtered above
            )
            print(f"Filtered to {len(all_transactions)} transactions")
        
        # Categorize transactions
        print("Categorizing transactions...")
        # Default to config.json if not specified
        config_path = args.config if args.config else Path('config.json')
        classifier = CategoryClassifier(config_path)
        categorized_transactions = classifier.categorize_all(all_transactions)
        print(f"Categorized {len(categorized_transactions)} transactions")
        
        # Interactive mode
        if args.interactive:
            print("\n=== Interactive Categorization Mode ===")
            private_config_path = config_path.parent / 'config.private.json'
            interactive_categorizer = InteractiveCategorizer()
            stats = interactive_categorizer.categorize_interactively(
                categorized_transactions,
                classifier,
                private_config_path
            )
            
            print("\n=== Categorization Summary ===")
            print(f"Total transactions: {stats['total']}")
            print(f"Selected for review: {stats['selected']}")
            print(f"Reviewed: {stats['reviewed']}")
            print(f"Accepted (no change): {stats['accepted']}")
            print(f"Re-categorized: {stats['re_categorized']}")
            print(f"Keywords added: {stats['keywords_added']}")
            print(f"Skipped: {stats['skipped']}")
            
            return 0
        
        # Analyze spending
        print("Analyzing spending patterns...")
        analyzer = SpendingAnalyzer(categorized_transactions)
        
        # Load budgets if specified
        budget_manager = None
        if args.budget_config or Path('budgets.json').exists():
            budget_path = args.budget_config if args.budget_config else Path('budgets.json')
            if budget_path.exists():
                print(f"Loading budgets from {budget_path}...")
                budget_manager = BudgetManager(budget_path)
            elif args.budget_config:
                print(f"Warning: Budget file not found: {budget_path}")
        
        # Generate CSV reports
        reports = {}
        if not args.html_only:
            print(f"Generating CSV reports in {args.output_dir}...")
            reporter = ReportGenerator(analyzer, args.output_dir)
            csv_reports = reporter.generate_all_reports(
                start_date=start_date,
                end_date=end_date,
                budget_manager=budget_manager
            )
            reports.update(csv_reports)
        
        # Generate HTML reports
        if args.html or args.html_only or args.qa:
            print(f"Generating HTML reports in {args.output_dir}...")
            html_reporter = HTMLReportGenerator(analyzer, args.output_dir)
            html_reports = html_reporter.generate_all_html_reports(
                start_date=start_date,
                end_date=end_date,
                include_qa=args.qa,
                budget_manager=budget_manager
            )
            reports.update(html_reports)
        
        print("\nGenerated reports:")
        for report_name, report_path in reports.items():
            print(f"  - {report_name}: {report_path}")
        
        # Print summary statistics
        income_expenses = analyzer.income_vs_expenses(start_date=start_date, end_date=end_date)
        print(f"\nSummary:")
        print(f"  Total Income: ${income_expenses['income']:.2f}")
        print(f"  Total Expenses: ${income_expenses['expenses']:.2f}")
        print(f"  Net: ${income_expenses['net']:.2f}")
        
        if args.qa:
            print(f"\nQA Report: Review transactions in {reports.get('qa_comparison', 'N/A')}")
            print("  Transactions in 'Other' category are highlighted for review.")
        
        return 0
        
    except FileNotFoundError as e:
        print(f"Error: File not found - {e}", file=sys.stderr)
        return 1
    except ValueError as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Unexpected error: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        return 1


if __name__ == '__main__':
    sys.exit(main())

