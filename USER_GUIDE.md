# Personal Finance Tracker - User Guide

## Introduction

The Personal Finance Tracker is a comprehensive tool for analyzing your spending, tracking budgets, and managing financial transactions. This guide covers all features and usage.

## Installation

1. Ensure Python 3.6+ is installed
2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```
3. Place your banking CSV files in the `data/` directory:
   - `SIMPLII -chequing.csv` (chequing account)
   - `SIMPLII -visa.csv` (Visa credit card)

## Basic Usage

### Running the Script

```bash
python pftrack.py
```

This will:
- Load transactions from CSV files
- Categorize all transactions
- Generate reports in the `reports/` directory

### Command-Line Options

#### File Options

- `--debit-csv PATH`: Path to chequing account CSV (default: `data/SIMPLII -chequing.csv`)
- `--visa-csv PATH`: Path to Visa CSV (default: `data/SIMPLII -visa.csv`)
- `--output-dir PATH`: Output directory for reports (default: `reports`)
- `--config PATH`: Path to category configuration file (default: `config.json`)
- `--budget-config PATH`: Path to budget configuration file (default: `budgets.json`)

#### Date Filtering

- `--start-date DATE`: Start date in MM/DD/YYYY format (inclusive)
- `--end-date DATE`: End date in MM/DD/YYYY format (inclusive)

#### Report Options

- `--html`: Generate HTML reports in addition to CSV
- `--html-only`: Generate only HTML reports (skip CSV)
- `--qa`: Generate QA comparison report for reviewing categorizations

#### Transaction Filtering

- `--category CATEGORY`: Filter by category name
- `--merchant MERCHANT`: Filter by merchant name
- `--min-amount AMOUNT`: Minimum transaction amount
- `--max-amount AMOUNT`: Maximum transaction amount
- `--search KEYWORD`: Search transactions by keyword

## Examples

### Basic Analysis

```bash
python pftrack.py
```

### Date Range Analysis

```bash
python pftrack.py --start-date 01/01/2025 --end-date 01/31/2025
```

### With Budget Tracking

```bash
python pftrack.py --html --budget-config budgets.json
```

### Filtered Analysis

```bash
python pftrack.py --category "Restaurants" --start-date 01/01/2025
```

### QA Review

```bash
python pftrack.py --html --qa
```

## Reports

### CSV Reports

Generated in the `reports/` directory:

- **monthly_summary.csv**: Monthly spending by category
- **category_totals.csv**: Total spending per category
- **top_merchants.csv**: Top merchants by spending
- **spending_trends.csv**: Month-over-month trends
- **transactions.csv**: Complete transaction list
- **budget_comparison.csv**: Budget vs. actual spending (if budgets configured)

### HTML Reports

- **summary.html**: Comprehensive summary with visualizations
- **qa_comparison.html**: Transaction categorization review (with `--qa`)

### Export Formats

The system supports exporting to:
- **JSON**: Programmatic access to transaction data
- **PDF**: Formatted reports (requires reportlab)
- **Excel**: Multi-sheet workbook (requires openpyxl)

## Category Configuration

Categories are defined in `config.json`. Each category includes:
- `keywords`: List of keywords to match in transaction descriptions
- `priority`: Lower numbers = higher priority
- `require_negative`: For income categories (requires negative amount)

### Adding Categories

Edit `config.json` to add new categories:

```json
{
  "categories": {
    "My Category": {
      "keywords": ["KEYWORD1", "KEYWORD2"],
      "priority": 1
    }
  }
}
```

### Auto-Tagging

Configure auto-tagging rules in `config.json`:

```json
{
  "auto_tagging": {
    "tax-deductible": {
      "keywords": ["WORK", "BUSINESS"],
      "categories": ["Work"]
    }
  }
}
```

## Budget Management

See [BUDGET_GUIDE.md](BUDGET_GUIDE.md) for detailed budget setup and usage.

## Transaction Management

### Manual Transactions

Use the `TransactionManager` class to add manual transactions:

```python
from transaction_manager import TransactionManager

manager = TransactionManager()
manager.add_transaction(
    date=datetime(2025, 1, 15),
    account_type='chequing',
    description='Manual Entry',
    amount=50.00,
    category='Shopping'
)
```

### Duplicate Detection

Detect duplicate transactions:

```python
from transaction_manager import TransactionManager

manager = TransactionManager()
duplicates = manager.detect_duplicates(transactions)
```

## Advanced Features

### Recurring Transactions

Detect and predict recurring transactions:

```python
from recurring_detector import RecurringDetector

detector = RecurringDetector(transactions)
recurring = detector.detect_recurring()
predictions = detector.predict_future(recurring, months_ahead=3)
```

### Goal Tracking

Track financial goals:

```python
from goals import GoalTracker

tracker = GoalTracker()
tracker.add_goal(
    name="Emergency Fund",
    goal_type="savings",
    target=10000.00,
    deadline=datetime(2025, 12, 31)
)
tracker.update_goal_progress(analyzer)
```

### Alerts

Generate spending alerts:

```python
from alerts import AlertManager

alert_manager = AlertManager(analyzer, budget_manager)
alerts = alert_manager.get_all_alerts()
```

## Troubleshooting

### No Transactions Loaded

- Check CSV file paths are correct
- Verify CSV file format matches expected Simplii format
- Check file encoding (should be UTF-8)

### Incorrect Categorization

- Review QA comparison report
- Update keywords in `config.json`
- Adjust category priorities if needed

### Budget Not Showing

- Ensure `budgets.json` exists
- Check budget file format is valid JSON
- Verify category names match transaction categories

## Tips

1. **Regular Reviews**: Run QA reports regularly to refine categorization
2. **Budget Updates**: Update budgets monthly based on actual spending
3. **Tag Usage**: Use tags for tax-deductible or reimbursable expenses
4. **Backup Data**: Use data manager to backup transaction data regularly
5. **Date Ranges**: Use date filters to analyze specific periods

## Support

For issues or questions:
1. Check documentation files (ARCHITECTURE.md, API.md)
2. Review example configurations
3. Check error messages for specific issues
