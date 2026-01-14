# Test Suite Documentation

## Overview

The test suite uses pytest as the testing framework and provides comprehensive coverage of all major modules in the Personal Finance Tracker.

## Running Tests

### Run All Tests

```bash
pytest
```

or

```bash
python -m pytest tests/
```

### Run with Verbose Output

```bash
pytest -v
```

### Run Specific Test File

```bash
pytest tests/test_transaction.py
```

### Run Specific Test

```bash
pytest tests/test_transaction.py::TestTransaction::test_transaction_creation
```

## Test Coverage

### test_transaction.py
Tests for the Transaction dataclass:
- Transaction creation and validation
- Expense/income detection
- Tags and notes functionality
- Invalid account type handling

**Test Count:** 5 tests

### test_budget.py
Tests for BudgetManager class:
- Budget loading from JSON
- Monthly and annual budget calculations
- Budget period calculations
- Budget validation
- Category budget queries

**Test Count:** 10 tests

### test_categorizer.py
Tests for CategoryClassifier class:
- Default category loading
- Keyword-based categorization
- Income transaction categorization
- Priority-based category matching
- Auto-tagging functionality

**Test Count:** 6 tests

### test_analyzer.py
Tests for SpendingAnalyzer class:
- Category totals calculation
- Monthly summary generation
- Income vs expenses calculation
- Date range filtering
- Top merchants calculation
- Budget comparison
- Advanced analytics (averages, forecasts, seasonal patterns)

**Test Count:** 11 tests

### test_transaction_filter.py
Tests for TransactionFilter class:
- Category filtering
- Account type filtering
- Date range filtering
- Amount range filtering
- Merchant filtering
- Keyword search
- Combined filtering

**Test Count:** 7 tests

### test_reporter.py
Tests for ReportGenerator class:
- CSV report generation (monthly summary, category totals, top merchants, etc.)
- Budget comparison reports
- JSON export
- All reports generation

**Test Count:** 7 tests

### test_transaction_manager.py
Tests for TransactionManager class:
- Manual transaction addition
- Transaction editing
- Transaction deletion
- Duplicate detection
- Transaction merging

**Test Count:** 6 tests

### test_data_manager.py
Tests for DataManager class:
- CSV export
- JSON export/import
- Backup creation
- Restore from backup

**Test Count:** 5 tests

## Total Test Count

**56 tests** covering all major functionality

## Test Results

All tests are currently passing:

```
============================== 56 passed in 0.22s ==============================
```

## Test Configuration

Test configuration is in `pytest.ini`:
- Test discovery pattern: `test_*.py`
- Test class pattern: `Test*`
- Test function pattern: `test_*`
- Verbose output enabled by default

## Writing New Tests

When adding new functionality, follow these guidelines:

1. Create test file: `tests/test_<module_name>.py`
2. Use unittest.TestCase as base class
3. Name test methods: `test_<functionality>`
4. Use setUp() and tearDown() for fixtures
5. Use descriptive test names
6. Test both success and failure cases
7. Use appropriate assertions (assertEqual, assertAlmostEqual, assertIn, etc.)

## Example Test Structure

```python
import unittest
from datetime import datetime

from transaction import Transaction

class TestMyModule(unittest.TestCase):
    """Test cases for MyModule class."""
    
    def setUp(self):
        """Set up test fixtures."""
        # Initialize test data
    
    def tearDown(self):
        """Clean up test fixtures."""
        # Clean up if needed
    
    def test_basic_functionality(self):
        """Test basic functionality."""
        # Test implementation
        self.assertEqual(expected, actual)
```

## Continuous Integration

Tests can be integrated into CI/CD pipelines:

```bash
# Install dependencies
pip install -r requirements.txt

# Run tests
pytest

# Generate coverage report (if pytest-cov installed)
pytest --cov=. --cov-report=html
```
