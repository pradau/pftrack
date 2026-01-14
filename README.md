# Personal Finance Tracker

A Python application that processes Simplii banking CSV exports (chequing and Visa accounts), automatically categorizes transactions using keyword-based rules, and generates detailed spending analysis reports in both CSV and HTML formats.

## Features

- Parses Simplii chequing and Visa account CSV files
- Automatic transaction categorization using keyword patterns
- Comprehensive spending analysis:
  - Monthly spending summaries by category
  - Total spending per category
  - Spending trends over time
  - Top merchants by spending
  - Income vs. expenses analysis
- Generates CSV and HTML reports for all analyses
- HTML reports with professional styling for better readability
- QA comparison report for reviewing and verifying transaction categorizations
- Configurable category definitions
- Date range filtering

## Requirements

- Python 3.6 or higher
- No external dependencies (uses only Python standard library)

## Installation

1. Clone or download this repository
2. Ensure Python 3.6+ is installed
3. Place your Simplii CSV files in the `data/` directory:
   - `SIMPLII -chequing.csv` (chequing account)
   - `SIMPLII -visa.csv` (Visa credit card)

## Usage

### Basic Usage

Run the script with default settings:

```bash
python pftrack.py
```

This will:
- Read CSV files from `data/` directory
- Categorize all transactions
- Generate reports in `reports/` directory

### Command-Line Options

```bash
python pftrack.py [options]
```

Options:
- `--debit-csv PATH`: Path to debit CSV file (default: `data/SIMPLII -chequing.csv`)
- `--visa-csv PATH`: Path to Visa CSV file (default: `data/SIMPLII -visa.csv`)
- `--output-dir PATH`: Directory for output reports (default: `reports`)
- `--config PATH`: Path to JSON configuration file for custom categories (optional)
- `--start-date DATE`: Start date filter in MM/DD/YYYY format (inclusive)
- `--end-date DATE`: End date filter in MM/DD/YYYY format (inclusive)
- `--html`: Generate HTML reports in addition to CSV reports
- `--html-only`: Generate only HTML reports (skip CSV reports)
- `--qa`: Generate QA comparison report for reviewing transaction categorizations

### Examples

Filter transactions for a specific date range:

```bash
python pftrack.py --start-date 12/01/2025 --end-date 12/31/2025
```

Use custom category configuration:

```bash
python pftrack.py --config my_categories.json
```

Specify custom file paths:

```bash
python pftrack.py --debit-csv /path/to/debit.csv --visa-csv /path/to/visa.csv --output-dir /path/to/reports
```

Generate HTML reports in addition to CSV:

```bash
python pftrack.py --html
```

Generate only HTML reports (no CSV):

```bash
python pftrack.py --html-only
```

Generate QA comparison report to review transaction categorizations:

```bash
python pftrack.py --qa
```

Combine options:

```bash
python pftrack.py --html --qa --start-date 12/01/2025 --end-date 12/31/2025
```

## Generated Reports

### CSV Reports

By default, the script generates the following CSV reports in the output directory:

1. **monthly_summary.csv**: Monthly spending by category with totals
2. **category_totals.csv**: Total spending per category (all-time or filtered)
3. **top_merchants.csv**: Top merchants by total spending amount
4. **spending_trends.csv**: Month-over-month spending trends by category
5. **transactions.csv**: Detailed transaction list with categories

### HTML Reports

When using `--html` or `--html-only`, the script generates:

1. **summary.html**: Comprehensive HTML report with:
   - Summary statistics (income, expenses, net)
   - Spending by category with visual formatting
   - Monthly spending summary tables
   - Top merchants list
   - Professional styling for easy reading

2. **qa_comparison.html** (with `--qa` flag): QA comparison report for reviewing transaction categorizations:
   - Summary of transactions by category
   - Complete transaction list grouped by category
   - Transactions in "Other" category highlighted in red for review
   - Helps identify miscategorizations and refine category keywords

HTML reports are self-contained (no external dependencies) and can be opened in any web browser.

## Category Configuration

Categories are defined in two configuration files:

### Public Configuration (`config.json`)
Contains generic, non-confidential keywords that can be safely shared publicly. This file is included in the repository.

### Private Configuration (`config.private.json`)
Contains personal merchant names, specific store locations, and other confidential transaction keywords. This file is **excluded from git** via `.gitignore` to protect your privacy.

**Setup:**
1. Copy `config.private.json.example` to `config.private.json`
2. Add your personal merchant names and transaction keywords
3. The system automatically merges both configs when categorizing transactions

**Configuration Structure:**
Each category includes:
- `keywords`: List of keywords to match in transaction descriptions
- `priority`: Lower numbers = higher priority (more specific patterns checked first)
- `require_negative`: Optional flag for income categories (requires negative amount)

You can customize categories by editing `config.json` and/or `config.private.json`, or provide custom config files with `--config`.

## Default Categories

- **Groceries**: Grocery stores, CO-OP, Superstore, etc.
- **Restaurants**: Restaurants, fast food, cafes
- **Gas/Transportation**: Gas stations, parking
- **Utilities**: Telus, Enmax, utility bills
- **Housing**: Mortgage, rent, property insurance
- **Shopping**: Amazon, retail stores
- **Entertainment**: Streaming services, books
- **Income**: Payroll, deposits, interest
- **Transfers**: Transfers and bill payments
- **Other**: Default for unmatched transactions

## Data Format

The script expects Simplii CSV files with the following formats:

**Debit CSV:**
- Columns: Date, Transaction Details, Funds Out, Funds In
- Date format: MM/DD/YYYY

**Visa CSV:**
- Columns: Date, Transaction Details, Funds Out, Funds In, Credit Card
- Date format: MM/DD/YYYY

## Future Enhancements

- Budget comparison module
- Web interface
- Database storage
- Multi-account support beyond Simplii
- Machine learning for improved categorization

## License

This is a personal finance tracking tool for individual use.

