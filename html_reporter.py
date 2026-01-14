"""
Author: Perry Radau
Date: 2025-01-27
Brief description: HTML report generator for spending analysis
Dependencies: Python 3.6+
Usage: HTMLReportGenerator class to create HTML reports from analysis results
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from analyzer import SpendingAnalyzer
from budget import BudgetManager
from transaction import Transaction


class HTMLReportGenerator:
    """Generates HTML reports from spending analysis."""
    
    def __init__(self, analyzer: SpendingAnalyzer, output_dir: Path):
        """Initialize HTML report generator.
        
        Args:
            analyzer: SpendingAnalyzer instance with transaction data
            output_dir: Directory to write HTML reports
        """
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
    
    def _get_css_styles(self) -> str:
        """Get CSS styles for HTML reports.
        
        Returns:
            str: CSS stylesheet content
        """
        return """
        <style>
            body {
                font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, 'Helvetica Neue', Arial, sans-serif;
                margin: 0;
                padding: 20px;
                background-color: #f5f5f5;
                color: #333;
            }
            .container {
                max-width: 1200px;
                margin: 0 auto;
                background-color: white;
                padding: 30px;
                border-radius: 8px;
                box-shadow: 0 2px 4px rgba(0,0,0,0.1);
            }
            h1 {
                color: #2c3e50;
                border-bottom: 3px solid #3498db;
                padding-bottom: 10px;
                margin-bottom: 30px;
            }
            h2 {
                color: #34495e;
                margin-top: 40px;
                margin-bottom: 20px;
                border-bottom: 2px solid #ecf0f1;
                padding-bottom: 8px;
            }
            table {
                width: 100%;
                border-collapse: collapse;
                margin: 20px 0;
                font-size: 14px;
            }
            th {
                background-color: #3498db;
                color: white;
                padding: 12px;
                text-align: left;
                font-weight: 600;
            }
            td {
                padding: 10px 12px;
                border-bottom: 1px solid #ecf0f1;
            }
            tr:hover {
                background-color: #f8f9fa;
            }
            tr:nth-child(even) {
                background-color: #fafafa;
            }
            .amount {
                text-align: right;
                font-family: 'Courier New', monospace;
            }
            .positive {
                color: #27ae60;
            }
            .negative {
                color: #e74c3c;
            }
            .summary-box {
                display: flex;
                gap: 20px;
                margin: 20px 0;
                flex-wrap: wrap;
            }
            .summary-item {
                flex: 1;
                min-width: 200px;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 5px;
                border-left: 4px solid #3498db;
            }
            .summary-item h3 {
                margin: 0 0 10px 0;
                color: #7f8c8d;
                font-size: 12px;
                text-transform: uppercase;
                letter-spacing: 1px;
            }
            .summary-item .value {
                font-size: 24px;
                font-weight: bold;
                color: #2c3e50;
            }
            .category-badge {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 12px;
                font-weight: 500;
                background-color: #e8f4f8;
                color: #2c3e50;
            }
            .qa-highlight {
                background-color: #fff3cd;
            }
            .qa-other {
                background-color: #f8d7da;
            }
            .budget-status {
                display: inline-block;
                padding: 4px 8px;
                border-radius: 3px;
                font-size: 11px;
                font-weight: 600;
                text-transform: uppercase;
            }
            .budget-under {
                background-color: #d4edda;
                color: #155724;
            }
            .budget-on-track {
                background-color: #fff3cd;
                color: #856404;
            }
            .budget-over {
                background-color: #f8d7da;
                color: #721c24;
            }
            .budget-significantly-over {
                background-color: #dc3545;
                color: white;
            }
            .progress-bar {
                width: 100%;
                height: 20px;
                background-color: #e9ecef;
                border-radius: 10px;
                overflow: hidden;
                margin: 5px 0;
            }
            .progress-fill {
                height: 100%;
                transition: width 0.3s ease;
            }
            .progress-under {
                background-color: #28a745;
            }
            .progress-on-track {
                background-color: #ffc107;
            }
            .progress-over {
                background-color: #fd7e14;
            }
            .progress-significantly-over {
                background-color: #dc3545;
            }
            .footer {
                margin-top: 40px;
                padding-top: 20px;
                border-top: 1px solid #ecf0f1;
                text-align: center;
                color: #7f8c8d;
                font-size: 12px;
            }
            .collapsible {
                cursor: pointer;
                user-select: none;
            }
            .collapsible:hover {
                background-color: #f0f0f0;
            }
            .collapsible-content {
                display: none;
                overflow: hidden;
            }
            .collapsible-content.active {
                display: block;
            }
            .sortable th {
                cursor: pointer;
                user-select: none;
            }
            .sortable th:hover {
                background-color: #2980b9;
            }
        </style>
        """
    
    def _get_javascript(self) -> str:
        """Get JavaScript code for interactive features.
        
        Returns:
            str: JavaScript code
        """
        return """
        <script>
            // Collapsible sections
            document.addEventListener('DOMContentLoaded', function() {
                const collapsibles = document.querySelectorAll('.collapsible');
                collapsibles.forEach(function(collapsible) {
                    collapsible.addEventListener('click', function() {
                        const content = this.nextElementSibling;
                        if (content && content.classList.contains('collapsible-content')) {
                            content.classList.toggle('active');
                            this.textContent = content.classList.contains('active') 
                                ? this.textContent.replace('▼', '▲').replace('▶', '▼')
                                : this.textContent.replace('▼', '▶').replace('▲', '▶');
                        }
                    });
                });
                
                // Sortable tables
                const sortableTables = document.querySelectorAll('.sortable');
                sortableTables.forEach(function(table) {
                    const headers = table.querySelectorAll('th');
                    headers.forEach(function(header, index) {
                        header.addEventListener('click', function() {
                            const tbody = table.querySelector('tbody');
                            const rows = Array.from(tbody.querySelectorAll('tr'));
                            const isAscending = this.classList.contains('asc');
                            
                            // Remove sort indicators
                            headers.forEach(h => {
                                h.classList.remove('asc', 'desc');
                            });
                            
                            // Sort rows
                            rows.sort(function(a, b) {
                                const aText = a.cells[index].textContent.trim();
                                const bText = b.cells[index].textContent.trim();
                                
                                // Try numeric comparison
                                const aNum = parseFloat(aText.replace(/[^0-9.-]/g, ''));
                                const bNum = parseFloat(bText.replace(/[^0-9.-]/g, ''));
                                
                                if (!isNaN(aNum) && !isNaN(bNum)) {
                                    return isAscending ? bNum - aNum : aNum - bNum;
                                }
                                
                                // String comparison
                                return isAscending 
                                    ? bText.localeCompare(aText)
                                    : aText.localeCompare(bText);
                            });
                            
                            // Reorder rows
                            rows.forEach(row => tbody.appendChild(row));
                            
                            // Add sort indicator
                            this.classList.add(isAscending ? 'desc' : 'asc');
                        });
                    });
                });
            });
        </script>
        """
    
    def _format_amount(self, amount: float, show_sign: bool = False) -> str:
        """Format amount for display.
        
        Args:
            amount: Amount to format
            show_sign: Whether to show + sign for positive amounts
            
        Returns:
            str: Formatted amount string
        """
        if amount >= 0:
            sign = "+" if show_sign else ""
            return f'<span class="positive">{sign}${amount:,.2f}</span>'
        else:
            return f'<span class="negative">${amount:,.2f}</span>'
    
    def _get_budget_status_class(self, utilization: float) -> str:
        """Get CSS class for budget status based on utilization.
        
        Args:
            utilization: Budget utilization percentage
            
        Returns:
            str: CSS class name
        """
        if utilization <= 80:
            return 'budget-under'
        elif utilization <= 100:
            return 'budget-on-track'
        elif utilization <= 120:
            return 'budget-over'
        else:
            return 'budget-significantly-over'
    
    def _get_progress_class(self, utilization: float) -> str:
        """Get CSS class for progress bar based on utilization.
        
        Args:
            utilization: Budget utilization percentage
            
        Returns:
            str: CSS class name
        """
        if utilization <= 80:
            return 'progress-under'
        elif utilization <= 100:
            return 'progress-on-track'
        elif utilization <= 120:
            return 'progress-over'
        else:
            return 'progress-significantly-over'
    
    def _get_budget_status_text(self, utilization: float) -> str:
        """Get status text for budget utilization.
        
        Args:
            utilization: Budget utilization percentage
            
        Returns:
            str: Status text
        """
        if utilization <= 80:
            return 'Under Budget'
        elif utilization <= 100:
            return 'On Track'
        elif utilization <= 120:
            return 'Over Budget'
        else:
            return 'Significantly Over'
    
    def generate_summary_report(self, filename: str = "summary.html",
                               start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               budget_manager: Optional[BudgetManager] = None) -> Path:
        """Generate comprehensive summary HTML report.
        
        Args:
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated HTML file
        """
        income_expenses = self.analyzer.income_vs_expenses(start_date, end_date)
        category_totals = self.analyzer.category_totals(start_date, end_date)
        monthly_data = self.analyzer.monthly_summary(start_date, end_date)
        top_merchants = self.analyzer.top_merchants(20, start_date, end_date)
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n')
            f.write('<meta charset="UTF-8">\n')
            f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
            f.write('<title>Personal Finance Summary</title>\n')
            f.write(self._get_css_styles())
            f.write('</head>\n<body>\n')
            f.write(self._get_javascript())
            f.write('<div class="container">\n')
            
            # Header
            date_range = ""
            if start_date or end_date:
                start_str = start_date.strftime("%B %d, %Y") if start_date else "Beginning"
                end_str = end_date.strftime("%B %d, %Y") if end_date else "End"
                date_range = f" ({start_str} to {end_str})"
            
            f.write(f'<h1>Personal Finance Summary{date_range}</h1>\n')
            
            # Summary boxes
            f.write('<div class="summary-box">\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Total Income</h3>\n')
            f.write(f'<div class="value">{self._format_amount(income_expenses["income"])}</div>\n')
            f.write('</div>\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Total Expenses</h3>\n')
            f.write(f'<div class="value">{self._format_amount(income_expenses["expenses"])}</div>\n')
            f.write('</div>\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Net</h3>\n')
            net_class = "positive" if income_expenses["net"] >= 0 else "negative"
            f.write(f'<div class="value {net_class}">{self._format_amount(income_expenses["net"], show_sign=True)}</div>\n')
            f.write('</div>\n')
            f.write('</div>\n')
            
            # Category totals
            f.write('<h2>Spending by Category</h2>\n')
            sorted_totals = sorted(category_totals.items(), key=lambda x: x[1], reverse=True)
            f.write('<table class="sortable">\n')
            f.write('<thead><tr><th>Category</th><th class="amount">Total Amount</th></tr></thead>\n')
            f.write('<tbody>\n')
            for category, amount in sorted_totals:
                f.write(f'<tr><td><span class="category-badge">{category}</span></td>')
                f.write(f'<td class="amount">{self._format_amount(amount)}</td></tr>\n')
            f.write('</tbody>\n')
            f.write('</table>\n')
            
            # Monthly summary
            if monthly_data:
                f.write('<h2>Monthly Spending Summary</h2>\n')
                all_categories = set()
                for month_data in monthly_data.values():
                    all_categories.update(month_data.keys())
                all_categories = sorted(all_categories)
                
                f.write('<table>\n')
                f.write('<thead><tr><th>Month</th>')
                for category in all_categories:
                    f.write(f'<th class="amount">{category}</th>')
                f.write('<th class="amount">Total</th></tr></thead>\n')
                f.write('<tbody>\n')
                
                for month in sorted(monthly_data.keys()):
                    f.write(f'<tr><td><strong>{month}</strong></td>')
                    month_total = 0.0
                    for category in all_categories:
                        amount = monthly_data[month].get(category, 0.0)
                        f.write(f'<td class="amount">{self._format_amount(amount) if amount != 0 else "-"}</td>')
                        month_total += amount
                    f.write(f'<td class="amount"><strong>{self._format_amount(month_total)}</strong></td></tr>\n')
                
                f.write('</tbody>\n')
                f.write('</table>\n')
            
            # Top merchants
            if top_merchants:
                f.write('<h2>Top Merchants</h2>\n')
                f.write('<table>\n')
                f.write('<thead><tr><th>Merchant</th><th class="amount">Total Amount</th><th>Transactions</th></tr></thead>\n')
                f.write('<tbody>\n')
                for merchant, amount, count in top_merchants:
                    f.write(f'<tr><td>{merchant}</td>')
                    f.write(f'<td class="amount">{self._format_amount(amount)}</td>')
                    f.write(f'<td>{count}</td></tr>\n')
                f.write('</tbody>\n')
                f.write('</table>\n')
            
            # Budget comparison
            if budget_manager:
                budget_comparison = self.analyzer.budget_vs_actual(
                    budget_manager, start_date, end_date
                )
                
                # Filter to only categories with budgets
                budgeted_categories = {
                    cat: data for cat, data in budget_comparison.items()
                    if data['budget'] > 0
                }
                
                if budgeted_categories:
                    f.write('<h2>Budget vs. Actual Spending</h2>\n')
                    f.write('<table>\n')
                    f.write('<thead><tr><th>Category</th><th class="amount">Budget</th>')
                    f.write('<th class="amount">Actual</th><th class="amount">Difference</th>')
                    f.write('<th>Utilization</th><th>Status</th></tr></thead>\n')
                    f.write('<tbody>\n')
                    
                    # Sort by utilization (over budget first)
                    sorted_budget = sorted(
                        budgeted_categories.items(),
                        key=lambda x: x[1]['utilization'],
                        reverse=True
                    )
                    
                    for category, data in sorted_budget:
                        utilization = data['utilization']
                        status_class = self._get_budget_status_class(utilization)
                        status_text = self._get_budget_status_text(utilization)
                        
                        # Cap utilization at 200% for progress bar display
                        progress_width = min(utilization, 200.0)
                        
                        f.write(f'<tr>')
                        f.write(f'<td><span class="category-badge">{category}</span></td>')
                        f.write(f'<td class="amount">{self._format_amount(data["budget"])}</td>')
                        f.write(f'<td class="amount">{self._format_amount(data["actual"])}</td>')
                        f.write(f'<td class="amount">{self._format_amount(data["difference"])}</td>')
                        f.write(f'<td>')
                        f.write(f'<div class="progress-bar">')
                        f.write(f'<div class="progress-fill {self._get_progress_class(utilization)}" ')
                        f.write(f'style="width: {progress_width}%"></div>')
                        f.write(f'</div>')
                        f.write(f'{utilization:.1f}%')
                        f.write(f'</td>')
                        f.write(f'<td><span class="budget-status {status_class}">{status_text}</span></td>')
                        f.write(f'</tr>\n')
                    
                    f.write('</tbody>\n')
                    f.write('</table>\n')
            
            # Footer
            f.write('<div class="footer">\n')
            f.write(f'<p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>\n')
            f.write('</div>\n')
            
            f.write('</div>\n</body>\n</html>\n')
        
        return output_path
    
    def generate_qa_comparison(self, filename: str = "qa_comparison.html",
                              start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None) -> Path:
        """Generate QA comparison report showing all transactions with categories.
        
        This report helps review and verify transaction categorizations.
        
        Args:
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated HTML file
        """
        transactions = self.analyzer.filter_by_date_range(start_date, end_date)
        transactions = sorted(transactions, key=lambda t: (t.date, t.category))
        
        # Count transactions by category
        category_counts = {}
        for t in transactions:
            category_counts[t.category] = category_counts.get(t.category, 0) + 1
        
        output_path = self.output_dir / filename
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write('<!DOCTYPE html>\n<html lang="en">\n<head>\n')
            f.write('<meta charset="UTF-8">\n')
            f.write('<meta name="viewport" content="width=device-width, initial-scale=1.0">\n')
            f.write('<title>Transaction QA - Category Review</title>\n')
            f.write(self._get_css_styles())
            f.write('</head>\n<body>\n')
            f.write(self._get_javascript())
            f.write('<div class="container">\n')
            
            # Header
            date_range = ""
            if start_date or end_date:
                start_str = start_date.strftime("%B %d, %Y") if start_date else "Beginning"
                end_str = end_date.strftime("%B %d, %Y") if end_date else "End"
                date_range = f" ({start_str} to {end_str})"
            
            f.write(f'<h1>Transaction Category Review{date_range}</h1>\n')
            
            # Summary
            f.write('<div class="summary-box">\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Total Transactions</h3>\n')
            f.write(f'<div class="value">{len(transactions)}</div>\n')
            f.write('</div>\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Categories</h3>\n')
            f.write(f'<div class="value">{len(category_counts)}</div>\n')
            f.write('</div>\n')
            f.write(f'<div class="summary-item">\n')
            f.write('<h3>Uncategorized (Other)</h3>\n')
            other_count = category_counts.get("Other", 0)
            f.write(f'<div class="value">{other_count}</div>\n')
            f.write('</div>\n')
            f.write('</div>\n')
            
            # Category breakdown
            f.write('<h2>Transactions by Category</h2>\n')
            f.write('<table>\n')
            f.write('<thead><tr><th>Category</th><th>Count</th><th class="amount">Total Amount</th></tr></thead>\n')
            f.write('<tbody>\n')
            
            category_totals = {}
            for t in transactions:
                if t.is_expense():
                    category_totals[t.category] = category_totals.get(t.category, 0) + t.amount
            
            for category in sorted(category_counts.keys()):
                count = category_counts[category]
                total = category_totals.get(category, 0.0)
                row_class = 'qa-other' if category == 'Other' else ''
                f.write(f'<tr class="{row_class}">')
                f.write(f'<td><span class="category-badge">{category}</span></td>')
                f.write(f'<td>{count}</td>')
                f.write(f'<td class="amount">{self._format_amount(total)}</td>')
                f.write('</tr>\n')
            
            f.write('</tbody>\n')
            f.write('</table>\n')
            
            # Detailed transaction list
            f.write('<h2>All Transactions</h2>\n')
            f.write('<p>Review transactions below. Transactions in "Other" category are highlighted in red.</p>\n')
            f.write('<table>\n')
            f.write('<thead><tr><th>Date</th><th>Account</th><th>Description</th><th class="amount">Amount</th><th>Category</th></tr></thead>\n')
            f.write('<tbody>\n')
            
            current_category = None
            for transaction in transactions:
                # Add category header row when category changes
                if transaction.category != current_category:
                    f.write(f'<tr style="background-color: #e8f4f8;"><td colspan="5"><strong>{transaction.category}</strong></td></tr>\n')
                    current_category = transaction.category
                
                row_class = 'qa-other' if transaction.category == 'Other' else ''
                f.write(f'<tr class="{row_class}">')
                f.write(f'<td>{transaction.date.strftime("%Y-%m-%d")}</td>')
                f.write(f'<td>{transaction.account_type.title()}</td>')
                f.write(f'<td>{transaction.description}</td>')
                f.write(f'<td class="amount">{self._format_amount(transaction.amount)}</td>')
                f.write(f'<td><span class="category-badge">{transaction.category}</span></td>')
                f.write('</tr>\n')
            
            f.write('</tbody>\n')
            f.write('</table>\n')
            
            # Footer
            f.write('<div class="footer">\n')
            f.write('<p><strong>Note:</strong> Review transactions carefully. If you find miscategorizations,')
            f.write(' update the category keywords in config.json and re-run the analysis.</p>\n')
            f.write(f'<p>Generated on {datetime.now().strftime("%B %d, %Y at %I:%M %p")}</p>\n')
            f.write('</div>\n')
            
            f.write('</div>\n</body>\n</html>\n')
        
        return output_path
    
    def generate_all_html_reports(self, start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None,
                                  include_qa: bool = True,
                                  budget_manager: Optional[BudgetManager] = None) -> Dict[str, Path]:
        """Generate all HTML reports.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            include_qa: Whether to include QA comparison report
            budget_manager: Optional BudgetManager for budget reports
            
        Returns:
            Dict mapping report names to file paths
        """
        reports = {}
        
        reports['summary'] = self.generate_summary_report(
            start_date=start_date, end_date=end_date,
            budget_manager=budget_manager
        )
        
        if include_qa:
            reports['qa_comparison'] = self.generate_qa_comparison(
                start_date=start_date, end_date=end_date
            )
        
        return reports

