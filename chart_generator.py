"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Chart generation for spending analysis visualizations
Dependencies: Python 3.6+, matplotlib
Usage: ChartGenerator class to create charts from analysis results
"""

from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import matplotlib
matplotlib.use('Agg')  # Non-interactive backend
import matplotlib.pyplot as plt
import matplotlib.dates as mdates

from analyzer import SpendingAnalyzer
from budget import BudgetManager


class ChartGenerator:
    """Generates charts and visualizations for spending analysis."""
    
    def __init__(self, analyzer: SpendingAnalyzer, output_dir: Path):
        """Initialize chart generator.
        
        Args:
            analyzer: SpendingAnalyzer instance with transaction data
            output_dir: Directory to save chart images
        """
        self.analyzer = analyzer
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)
        
        # Set style
        plt.style.use('seaborn-v0_8-darkgrid' if 'seaborn-v0_8-darkgrid' in plt.style.available else 'default')
    
    def generate_category_pie_chart(self, filename: str = "category_pie.png",
                                    start_date: Optional[datetime] = None,
                                    end_date: Optional[datetime] = None) -> Path:
        """Generate pie chart of spending by category.
        
        Args:
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated chart file
        """
        category_totals = self.analyzer.category_totals(start_date, end_date)
        
        # Filter out zero amounts and sort
        filtered_totals = {k: v for k, v in category_totals.items() if v > 0}
        sorted_totals = sorted(filtered_totals.items(), key=lambda x: x[1], reverse=True)
        
        if not sorted_totals:
            raise ValueError("No spending data to chart")
        
        categories, amounts = zip(*sorted_totals)
        
        fig, ax = plt.subplots(figsize=(10, 8))
        ax.pie(amounts, labels=categories, autopct='%1.1f%%', startangle=90)
        ax.set_title('Spending by Category', fontsize=16, fontweight='bold')
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_spending_trends_chart(self, filename: str = "spending_trends.png",
                                       start_date: Optional[datetime] = None,
                                       end_date: Optional[datetime] = None) -> Path:
        """Generate line chart of spending trends over time by category.
        
        Args:
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated chart file
        """
        trends = self.analyzer.spending_trends()
        
        if not trends:
            raise ValueError("No spending trends data to chart")
        
        fig, ax = plt.subplots(figsize=(12, 6))
        
        # Plot each category
        for category, data_points in trends.items():
            if not data_points:
                continue
            
            months, amounts = zip(*data_points)
            # Convert month strings to dates for plotting
            month_dates = [datetime.strptime(m, "%Y-%m") for m in months]
            ax.plot(month_dates, amounts, marker='o', label=category, linewidth=2)
        
        ax.set_xlabel('Month', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_title('Spending Trends by Category', fontsize=16, fontweight='bold')
        ax.legend(loc='best', fontsize=9)
        ax.grid(True, alpha=0.3)
        
        # Format x-axis dates
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m'))
        ax.xaxis.set_major_locator(mdates.MonthLocator())
        plt.xticks(rotation=45)
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_budget_comparison_chart(self, budget_manager: BudgetManager,
                                         filename: str = "budget_comparison.png",
                                         start_date: Optional[datetime] = None,
                                         end_date: Optional[datetime] = None) -> Path:
        """Generate bar chart comparing budget vs. actual spending.
        
        Args:
            budget_manager: BudgetManager instance with budget data
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated chart file
        """
        budget_comparison = self.analyzer.budget_vs_actual(
            budget_manager, start_date, end_date
        )
        
        # Filter to categories with budgets
        budgeted = {k: v for k, v in budget_comparison.items() if v['budget'] > 0}
        
        if not budgeted:
            raise ValueError("No budget data to chart")
        
        categories = list(budgeted.keys())
        budgets = [budgeted[cat]['budget'] for cat in categories]
        actuals = [budgeted[cat]['actual'] for cat in categories]
        
        x = range(len(categories))
        width = 0.35
        
        fig, ax = plt.subplots(figsize=(12, 6))
        ax.bar([i - width/2 for i in x], budgets, width, label='Budget', color='#3498db')
        ax.bar([i + width/2 for i in x], actuals, width, label='Actual', color='#e74c3c')
        
        ax.set_xlabel('Category', fontsize=12)
        ax.set_ylabel('Amount ($)', fontsize=12)
        ax.set_title('Budget vs. Actual Spending', fontsize=16, fontweight='bold')
        ax.set_xticks(x)
        ax.set_xticklabels(categories, rotation=45, ha='right')
        ax.legend()
        ax.grid(True, alpha=0.3, axis='y')
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
    
    def generate_monthly_heatmap(self, filename: str = "monthly_heatmap.png",
                                  start_date: Optional[datetime] = None,
                                  end_date: Optional[datetime] = None) -> Path:
        """Generate heatmap of monthly spending by category.
        
        Args:
            filename: Output filename
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            Path to generated chart file
        """
        monthly_data = self.analyzer.monthly_summary(start_date, end_date)
        
        if not monthly_data:
            raise ValueError("No monthly data to chart")
        
        # Collect all categories and months
        all_categories = set()
        for month_data in monthly_data.values():
            all_categories.update(month_data.keys())
        all_categories = sorted(all_categories)
        months = sorted(monthly_data.keys())
        
        # Build matrix
        matrix = []
        for month in months:
            row = [monthly_data[month].get(cat, 0.0) for cat in all_categories]
            matrix.append(row)
        
        fig, ax = plt.subplots(figsize=(max(12, len(all_categories) * 0.8), max(6, len(months) * 0.5)))
        im = ax.imshow(matrix, aspect='auto', cmap='YlOrRd')
        
        ax.set_xticks(range(len(all_categories)))
        ax.set_xticklabels(all_categories, rotation=45, ha='right')
        ax.set_yticks(range(len(months)))
        ax.set_yticklabels(months)
        ax.set_title('Monthly Spending Heatmap by Category', fontsize=16, fontweight='bold')
        
        # Add colorbar
        plt.colorbar(im, ax=ax, label='Amount ($)')
        
        output_path = self.output_dir / filename
        plt.tight_layout()
        plt.savefig(output_path, dpi=150, bbox_inches='tight')
        plt.close()
        
        return output_path
