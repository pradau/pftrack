# Personal Finance Tracker - API Documentation

## Module APIs

### transaction.py

#### Transaction (dataclass)

Represents a single financial transaction.

**Fields:**
- `date: datetime` - Transaction date
- `account_type: str` - Account type ('chequing' or 'visa')
- `description: str` - Transaction description/merchant
- `amount: float` - Amount (positive=expense, negative=income)
- `category: str` - Assigned category (default: "Other")
- `subcategory: Optional[str]` - Optional subcategory
- `credit_card: Optional[str]` - Credit card number (Visa only)
- `tags: List[str]` - List of tags
- `notes: Optional[str]` - Optional notes
- `account_id: Optional[str]` - Account identifier

**Methods:**
- `is_expense() -> bool` - Check if transaction is an expense
- `is_income() -> bool` - Check if transaction is income
- `abs_amount() -> float` - Get absolute value of amount

### csv_parser.py

#### parse_debit_csv(csv_path: Path) -> List[Transaction]

Parse Simplii chequing account CSV file.

**Args:**
- `csv_path`: Path to CSV file

**Returns:**
- List of Transaction objects

#### parse_visa_csv(csv_path: Path) -> List[Transaction]

Parse Simplii Visa account CSV file.

**Args:**
- `csv_path`: Path to CSV file

**Returns:**
- List of Transaction objects

### categorizer.py

#### CategoryClassifier

Transaction categorization using keyword matching.

**Methods:**
- `__init__(config_path: Optional[Path] = None)` - Initialize with config file
- `categorize(transaction: Transaction) -> str` - Categorize single transaction
- `categorize_all(transactions: List[Transaction]) -> List[Transaction]` - Categorize all transactions
- `get_category_list() -> List[str]` - Get list of all categories

### analyzer.py

#### SpendingAnalyzer

Spending analysis engine.

**Methods:**
- `__init__(transactions: List[Transaction])` - Initialize with transactions
- `filter_by_date_range(start_date, end_date) -> List[Transaction]` - Filter transactions
- `monthly_summary(start_date, end_date) -> Dict[str, Dict[str, float]]` - Monthly spending by category
- `category_totals(start_date, end_date) -> Dict[str, float]` - Total spending per category
- `spending_trends() -> Dict[str, List[Tuple[str, float]]]` - Month-over-month trends
- `top_merchants(limit, start_date, end_date) -> List[Tuple[str, float, int]]` - Top merchants
- `income_vs_expenses(start_date, end_date) -> Dict[str, float]` - Income/expense summary
- `budget_vs_actual(budget_manager, start_date, end_date) -> Dict` - Budget comparison
- `budget_remaining(budget_manager, category, start_date, end_date) -> float` - Remaining budget
- `budget_utilization(budget_manager, category, start_date, end_date) -> float` - Budget utilization %
- `average_monthly_spending(category, start_date, end_date) -> float` - Average monthly spending
- `spending_velocity(category, period_days, start_date, end_date) -> float` - Daily spending rate
- `category_comparison(categories, start_date, end_date) -> Dict[str, float]` - Compare categories
- `spending_forecast(category, months, start_date, end_date) -> float` - Forecast future spending
- `seasonal_patterns() -> Dict[str, Dict[str, float]]` - Seasonal spending patterns

### budget.py

#### BudgetManager

Budget configuration and management.

**Methods:**
- `__init__(budget_path: Optional[Path] = None)` - Initialize with budget file
- `load_budgets(budget_path: Path) -> None` - Load budgets from file
- `get_monthly_budget(category: str) -> float` - Get monthly budget for category
- `get_annual_budget(category: str) -> float` - Get annual budget for category
- `get_budget_for_period(category, start_date, end_date) -> float` - Calculate budget for period
- `has_budget(category: str) -> bool` - Check if category has budget
- `get_all_categories_with_budgets() -> list` - Get all categories with budgets

### transaction_filter.py

#### TransactionFilter

Transaction filtering and search.

**Static Methods:**
- `filter_by_category(transactions, category) -> List[Transaction]`
- `filter_by_account_type(transactions, account_type) -> List[Transaction]`
- `filter_by_date_range(transactions, start_date, end_date) -> List[Transaction]`
- `filter_by_amount_range(transactions, min_amount, max_amount) -> List[Transaction]`
- `filter_by_merchant(transactions, merchant) -> List[Transaction]`
- `search_by_keyword(transactions, keyword) -> List[Transaction]`
- `filter_all(transactions, **filters) -> List[Transaction]` - Apply all filters

### transaction_manager.py

#### TransactionManager

Manual transaction management.

**Methods:**
- `__init__(manual_transactions_path: Path)` - Initialize with storage path
- `add_transaction(**kwargs) -> Dict` - Add manual transaction
- `edit_transaction(index, **kwargs) -> Dict` - Edit transaction
- `delete_transaction(index) -> None` - Delete transaction
- `get_manual_transactions() -> List[Transaction]` - Get all manual transactions
- `detect_duplicates(transactions, date_tolerance_days, amount_tolerance) -> List[Tuple]` - Find duplicates
- `merge_transactions(transaction1, transaction2) -> Transaction` - Merge duplicates

### reporter.py

#### ReportGenerator

CSV and export report generation.

**Methods:**
- `__init__(analyzer: SpendingAnalyzer, output_dir: Path)` - Initialize
- `generate_monthly_summary(filename, start_date, end_date) -> Path` - Monthly summary CSV
- `generate_category_totals(filename, start_date, end_date) -> Path` - Category totals CSV
- `generate_top_merchants(filename, limit, start_date, end_date) -> Path` - Top merchants CSV
- `generate_spending_trends(filename) -> Path` - Spending trends CSV
- `generate_transaction_list(filename, start_date, end_date) -> Path` - Transaction list CSV
- `generate_budget_comparison(budget_manager, filename, start_date, end_date) -> Path` - Budget comparison CSV
- `export_to_json(filename, start_date, end_date) -> Path` - JSON export
- `export_to_pdf(filename, start_date, end_date) -> Optional[Path]` - PDF export (requires reportlab)
- `export_to_excel(filename, start_date, end_date) -> Optional[Path]` - Excel export (requires openpyxl)
- `generate_all_reports(start_date, end_date, budget_manager) -> Dict[str, Path]` - Generate all reports

### html_reporter.py

#### HTMLReportGenerator

HTML report generation.

**Methods:**
- `__init__(analyzer: SpendingAnalyzer, output_dir: Path)` - Initialize
- `generate_summary_report(filename, start_date, end_date, budget_manager) -> Path` - Summary HTML
- `generate_qa_comparison(filename, start_date, end_date) -> Path` - QA comparison HTML
- `generate_all_html_reports(start_date, end_date, include_qa, budget_manager) -> Dict[str, Path]` - Generate all HTML reports

### chart_generator.py

#### ChartGenerator

Chart and visualization generation.

**Methods:**
- `__init__(analyzer: SpendingAnalyzer, output_dir: Path)` - Initialize
- `generate_category_pie_chart(filename, start_date, end_date) -> Path` - Pie chart
- `generate_spending_trends_chart(filename, start_date, end_date) -> Path` - Line chart
- `generate_budget_comparison_chart(budget_manager, filename, start_date, end_date) -> Path` - Bar chart
- `generate_monthly_heatmap(filename, start_date, end_date) -> Path` - Heatmap

### recurring_detector.py

#### RecurringDetector

Recurring transaction detection.

**Methods:**
- `__init__(transactions: List[Transaction])` - Initialize
- `detect_recurring(min_occurrences, amount_tolerance, merchant_similarity) -> List[RecurringTransaction]` - Detect patterns
- `predict_future(recurring_transactions, months_ahead) -> List[Tuple]` - Predict future transactions
- `find_missing(recurring_transactions, current_date) -> List[RecurringTransaction]` - Find overdue transactions

### goals.py

#### GoalTracker

Financial goal tracking.

**Methods:**
- `__init__(goals_path: Path)` - Initialize
- `add_goal(name, goal_type, target, deadline, category) -> Goal` - Add goal
- `update_goal_progress(analyzer, start_date, end_date) -> None` - Update progress
- `get_goals() -> List[Goal]` - Get all goals
- `get_goal(name) -> Optional[Goal]` - Get goal by name
- `delete_goal(name) -> bool` - Delete goal

### alerts.py

#### AlertManager

Spending and budget alerts.

**Methods:**
- `__init__(analyzer: SpendingAnalyzer, budget_manager: Optional[BudgetManager])` - Initialize
- `check_budget_thresholds(start_date, end_date, thresholds) -> List[Alert]` - Budget alerts
- `detect_unusual_spending(start_date, end_date, std_dev_threshold) -> List[Alert]` - Unusual spending
- `detect_spending_spikes(start_date, end_date, spike_threshold) -> List[Alert]` - Spending spikes
- `get_all_alerts(start_date, end_date) -> List[Alert]` - Get all alerts

### data_manager.py

#### DataManager

Data import/export utilities.

**Methods:**
- `__init__(output_dir: Path)` - Initialize
- `export_transactions_to_csv(transactions, filename) -> Path` - Export to CSV
- `export_transactions_to_json(transactions, filename) -> Path` - Export to JSON
- `import_transactions_from_json(json_path) -> List[Transaction]` - Import from JSON
- `backup_data(transactions, backup_dir) -> Path` - Create backup
- `restore_from_backup(backup_path) -> List[Transaction]` - Restore from backup
