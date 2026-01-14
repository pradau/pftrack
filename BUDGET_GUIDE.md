# Personal Finance Tracker - Budget Guide

## Introduction

The budget management system allows you to set spending limits for categories and track your progress throughout the month or year. This guide covers budget setup, configuration, and usage.

## Budget Configuration

Budgets are stored in `budgets.json`. The file supports three types of budgets:

1. **Monthly Budgets**: Fixed monthly spending limits per category
2. **Annual Budgets**: Yearly spending limits (prorated for date ranges)
3. **Category Budgets**: Custom budget configurations per category

## Budget File Format

### Basic Structure

```json
{
  "monthly_budgets": {
    "Groceries": 500.00,
    "Restaurants": 200.00,
    "Gas/Transportation": 150.00
  },
  "annual_budgets": {
    "Travel": 3000.00
  },
  "category_budgets": {}
}
```

### Monthly Budgets

Monthly budgets are the most common type. They represent a fixed amount you plan to spend per month in each category.

**Example:**
```json
{
  "monthly_budgets": {
    "Groceries": 500.00,
    "Restaurants": 200.00,
    "Entertainment": 100.00,
    "Shopping": 200.00,
    "Health": 100.00,
    "Utilities": 200.00,
    "Housing": 1500.00
  }
}
```

### Annual Budgets

Annual budgets are useful for categories with irregular spending (e.g., travel, large purchases). The system automatically prorates annual budgets for any date range.

**Example:**
```json
{
  "annual_budgets": {
    "Travel": 3000.00,
    "Computer": 2000.00
  }
}
```

### Category Budgets

Category budgets allow for more complex budget configurations (future enhancement).

## Creating Your Budget

### Step 1: Review Historical Spending

Before setting budgets, analyze your past spending:

```bash
python pftrack.py --html
```

Review the category totals in the summary report to understand your current spending patterns.

### Step 2: Set Initial Budgets

Create or edit `budgets.json` with your target spending amounts:

```json
{
  "monthly_budgets": {
    "Groceries": 500.00,
    "Restaurants": 200.00,
    "Gas/Transportation": 150.00,
    "Entertainment": 100.00,
    "Shopping": 200.00,
    "Health": 100.00,
    "Utilities": 200.00,
    "Housing": 1500.00
  },
  "annual_budgets": {},
  "category_budgets": {}
}
```

### Step 3: Run Analysis with Budgets

```bash
python pftrack.py --html --budget-config budgets.json
```

## Budget Reports

### HTML Summary Report

The HTML summary report includes a "Budget vs. Actual Spending" section showing:

- **Budget**: Your budgeted amount for the period
- **Actual**: Your actual spending
- **Difference**: Budget minus actual (positive = under budget)
- **Utilization**: Percentage of budget used
- **Status**: Visual indicator (Under Budget, On Track, Over Budget, Significantly Over)

### Budget Status Indicators

- **Under Budget** (green): Less than 80% of budget used
- **On Track** (yellow): 80-100% of budget used
- **Over Budget** (orange): 100-120% of budget used
- **Significantly Over** (red): More than 120% of budget used

### CSV Budget Report

The `budget_comparison.csv` file provides detailed budget data:

```csv
Category,Budget,Actual,Difference,Utilization %,Status
Groceries,500.00,450.00,50.00,90.0,On Track
Restaurants,200.00,250.00,-50.00,125.0,Over Budget
```

## Budget Calculations

### Monthly Budgets

For monthly budgets, the system calculates the budget for a date range by:

1. Determining the number of months (including partial months)
2. Multiplying monthly budget by number of months

**Example:**
- Monthly budget: $500
- Date range: 15 days (half a month)
- Budget for period: $500 × 0.5 = $250

### Annual Budgets

For annual budgets, the system prorates based on days:

1. Calculate days in the date range
2. Divide by 365.25 (average days per year)
3. Multiply annual budget by the ratio

**Example:**
- Annual budget: $3000
- Date range: 30 days
- Budget for period: $3000 × (30 / 365.25) = $246.58

## Budget Best Practices

### 1. Start Conservative

Begin with budgets slightly lower than your average spending to encourage savings.

### 2. Review Monthly

Update budgets monthly based on:
- Actual spending patterns
- Life changes (new job, moving, etc.)
- Seasonal variations

### 3. Use Annual Budgets for Irregular Expenses

Categories like Travel, Home Repairs, or Large Purchases work well with annual budgets.

### 4. Track Progress Regularly

Run budget reports weekly or bi-weekly to stay on track:

```bash
python pftrack.py --html --start-date 01/01/2025 --end-date 01/15/2025
```

### 5. Adjust as Needed

Budgets are guidelines, not strict limits. Adjust them based on:
- Unexpected expenses
- Income changes
- Financial goals

## Budget Alerts

The alert system automatically monitors budget utilization:

- **80% Threshold**: Warning when approaching budget limit
- **100% Threshold**: Alert when budget is exceeded
- **120% Threshold**: Critical alert for significant over-budget

View alerts in reports or use the AlertManager programmatically.

## Examples

### Monthly Budget Example

```json
{
  "monthly_budgets": {
    "Groceries": 500.00,
    "Restaurants": 200.00,
    "Gas/Transportation": 150.00,
    "Entertainment": 100.00,
    "Shopping": 200.00,
    "Health": 100.00,
    "Utilities": 200.00,
    "Housing": 1500.00,
    "Cell Phone": 80.00,
    "Internet": 60.00
  }
}
```

### Mixed Budget Example

```json
{
  "monthly_budgets": {
    "Groceries": 500.00,
    "Restaurants": 200.00,
    "Utilities": 200.00,
    "Housing": 1500.00
  },
  "annual_budgets": {
    "Travel": 3000.00,
    "Computer": 2000.00,
    "Home Repairs": 5000.00
  }
}
```

## Troubleshooting

### Budget Not Showing in Reports

- Ensure `budgets.json` exists in the project directory
- Check JSON syntax is valid
- Verify category names match exactly (case-sensitive)

### Incorrect Budget Calculations

- Check date range is correct
- Verify budget amounts are positive numbers
- Ensure budget type (monthly/annual) is appropriate

### Budget Status Not Updating

- Re-run analysis with `--budget-config` flag
- Check that transactions fall within the date range
- Verify category names match between budgets and transactions

## Advanced Usage

### Programmatic Budget Access

```python
from budget import BudgetManager
from pathlib import Path

budget_manager = BudgetManager(Path('budgets.json'))
monthly_budget = budget_manager.get_monthly_budget("Groceries")
budget_for_period = budget_manager.get_budget_for_period(
    "Groceries",
    start_date=datetime(2025, 1, 1),
    end_date=datetime(2025, 1, 31)
)
```

### Budget Analysis

```python
from analyzer import SpendingAnalyzer
from budget import BudgetManager

analyzer = SpendingAnalyzer(transactions)
budget_manager = BudgetManager(Path('budgets.json'))

# Get budget comparison
comparison = analyzer.budget_vs_actual(budget_manager)

# Check remaining budget
remaining = analyzer.budget_remaining(budget_manager, "Groceries")

# Get utilization percentage
utilization = analyzer.budget_utilization(budget_manager, "Groceries")
```

## Tips

1. **Be Realistic**: Set budgets based on actual needs, not wishful thinking
2. **Track Regularly**: Check budget status weekly
3. **Adjust Gradually**: Don't make drastic changes; adjust incrementally
4. **Use Categories Wisely**: Group similar expenses into categories
5. **Plan for Irregular Expenses**: Use annual budgets for one-time or seasonal expenses
