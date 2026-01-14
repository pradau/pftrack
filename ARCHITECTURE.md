# Personal Finance Tracker - Architecture Documentation

## System Overview

The Personal Finance Tracker is a Python-based application that processes banking transaction data, categorizes transactions, performs spending analysis, and generates comprehensive reports. The system is designed with a modular architecture for maintainability and extensibility.

## Architecture Diagram

```
┌─────────────────┐
│   CSV Parser    │ → Transaction objects
│  (csv_parser)   │
└─────────────────┘
         ↓
┌─────────────────┐
│  Categorizer    │ → Categorized transactions
│ (categorizer)   │   with tags
└─────────────────┘
         ↓
┌─────────────────┐
│    Analyzer     │ → Analysis results
│   (analyzer)    │
└─────────────────┘
         ↓
┌─────────────────┐
│   Reporters     │ → CSV/HTML/PDF/Excel reports
│ (reporter,      │
│ html_reporter)  │
└─────────────────┘
```

## Core Modules

### Data Layer

**transaction.py**
- Defines the `Transaction` dataclass
- Represents a single financial transaction
- Fields: date, account_type, description, amount, category, tags, notes, etc.

**csv_parser.py**
- Parses Simplii banking CSV files
- Handles chequing and Visa account formats
- Converts CSV rows to Transaction objects
- Normalizes transaction data

### Processing Layer

**categorizer.py**
- Implements keyword-based transaction categorization
- Loads rules from config.json
- Applies auto-tagging rules
- Priority-based category matching

**analyzer.py**
- Performs spending analysis
- Calculates statistics (totals, averages, trends)
- Budget comparison functionality
- Advanced analytics (forecasts, seasonal patterns)

**budget.py**
- Manages budget configurations
- Loads budgets from budgets.json
- Calculates budget amounts for date ranges
- Supports monthly and annual budgets

**transaction_filter.py**
- Provides filtering and search capabilities
- Filter by category, date, amount, merchant, etc.
- Keyword search in descriptions

**transaction_manager.py**
- Manages manual transaction entry
- Edit and delete transactions
- Duplicate detection and merging
- Stores manual transactions in JSON

**recurring_detector.py**
- Identifies recurring transaction patterns
- Predicts future transactions
- Detects missing expected transactions

**goals.py**
- Tracks financial goals (savings, spending reduction)
- Calculates goal progress
- Stores goals in JSON format

**alerts.py**
- Generates spending and budget alerts
- Budget threshold monitoring
- Unusual spending detection
- Spending spike detection

### Output Layer

**reporter.py**
- Generates CSV reports
- Exports to JSON, PDF, Excel formats
- Budget comparison reports

**html_reporter.py**
- Generates HTML reports with styling
- Interactive features (sortable tables)
- Budget visualization with progress bars
- QA comparison reports

**chart_generator.py**
- Creates visualizations using matplotlib
- Pie charts, line charts, bar charts, heatmaps
- Saves charts as PNG files

**data_manager.py**
- Import/export utilities
- Backup and restore functionality
- Data migration tools

### Configuration

**config.json**
- Category definitions with keywords
- Auto-tagging rules
- Category priorities

**budgets.json**
- Monthly and annual budgets per category
- Budget configuration

## Data Flow

1. **Input**: CSV files from banking accounts
2. **Parsing**: CSV parser converts to Transaction objects
3. **Categorization**: Categorizer assigns categories and tags
4. **Analysis**: Analyzer performs calculations
5. **Budget Comparison**: Budget manager provides budget data
6. **Reporting**: Reporters generate output files

## Design Patterns

- **Modular Design**: Each module has a single responsibility
- **Data Classes**: Transaction uses dataclass for clean data representation
- **Strategy Pattern**: Different report formats (CSV, HTML, PDF, Excel)
- **Configuration-Driven**: Categories and budgets loaded from JSON files

## Extension Points

- **New Bank Formats**: Extend csv_parser.py with new parser functions
- **New Report Formats**: Add methods to reporter.py
- **New Analytics**: Extend analyzer.py with new methods
- **New Alert Types**: Extend alerts.py with new detection methods

## Dependencies

- **Standard Library**: csv, json, datetime, pathlib, argparse, dataclasses, typing
- **External**: matplotlib (charts), reportlab (PDF), openpyxl (Excel)

## File Structure

```
pftrack/
├── pftrack.py              # Main entry point
├── transaction.py           # Data model
├── csv_parser.py           # CSV parsing
├── categorizer.py           # Categorization
├── analyzer.py              # Analysis engine
├── budget.py                # Budget management
├── transaction_filter.py    # Filtering
├── transaction_manager.py   # Transaction management
├── recurring_detector.py   # Recurring detection
├── goals.py                 # Goal tracking
├── alerts.py                # Alert generation
├── reporter.py              # CSV/PDF/Excel reports
├── html_reporter.py         # HTML reports
├── chart_generator.py       # Visualizations
├── data_manager.py         # Data utilities
├── config.json              # Category configuration
├── budgets.json             # Budget configuration
├── data/                    # Input CSV files
└── reports/                 # Generated reports
```
