"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Spending alerts and notifications
Dependencies: Python 3.6+
Usage: AlertManager class to generate spending and budget alerts
"""

from datetime import datetime
from typing import Dict, List, Optional

from analyzer import SpendingAnalyzer
from budget import BudgetManager


class Alert:
    """Represents a spending alert."""
    
    def __init__(self, alert_type: str, severity: str, message: str,
                 category: Optional[str] = None, amount: Optional[float] = None):
        """Initialize an alert.
        
        Args:
            alert_type: Type of alert ('budget_threshold', 'unusual_spending', 'spending_spike')
            severity: Alert severity ('info', 'warning', 'critical')
            message: Alert message
            category: Category name (if applicable)
            amount: Amount related to alert (if applicable)
        """
        self.alert_type = alert_type
        self.severity = severity
        self.message = message
        self.category = category
        self.amount = amount
    
    def __str__(self) -> str:
        """String representation of alert.
        
        Returns:
            str: Alert message
        """
        return self.message


class AlertManager:
    """Manages spending alerts and notifications."""
    
    def __init__(self, analyzer: SpendingAnalyzer, budget_manager: Optional[BudgetManager] = None):
        """Initialize alert manager.
        
        Args:
            analyzer: SpendingAnalyzer instance
            budget_manager: Optional BudgetManager for budget alerts
        """
        self.analyzer = analyzer
        self.budget_manager = budget_manager
    
    def check_budget_thresholds(self, start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None,
                                thresholds: List[float] = [80.0, 100.0, 120.0]) -> List[Alert]:
        """Check budget utilization thresholds and generate alerts.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            thresholds: List of utilization percentages to alert on
            
        Returns:
            List of Alert objects
        """
        alerts = []
        
        if not self.budget_manager:
            return alerts
        
        budget_comparison = self.analyzer.budget_vs_actual(
            self.budget_manager, start_date, end_date
        )
        
        for category, data in budget_comparison.items():
            if data['budget'] == 0:
                continue
            
            utilization = data['utilization']
            
            if utilization >= 120.0:
                alerts.append(Alert(
                    alert_type='budget_threshold',
                    severity='critical',
                    message=f"{category} is significantly over budget ({utilization:.1f}% used)",
                    category=category,
                    amount=data['actual']
                ))
            elif utilization >= 100.0:
                alerts.append(Alert(
                    alert_type='budget_threshold',
                    severity='warning',
                    message=f"{category} is over budget ({utilization:.1f}% used)",
                    category=category,
                    amount=data['actual']
                ))
            elif utilization >= 80.0:
                alerts.append(Alert(
                    alert_type='budget_threshold',
                    severity='info',
                    message=f"{category} is approaching budget limit ({utilization:.1f}% used)",
                    category=category,
                    amount=data['actual']
                ))
        
        return alerts
    
    def detect_unusual_spending(self, start_date: Optional[datetime] = None,
                               end_date: Optional[datetime] = None,
                               std_dev_threshold: float = 2.0) -> List[Alert]:
        """Detect unusual spending using statistical analysis.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            std_dev_threshold: Number of standard deviations for outlier detection
            
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # Get monthly spending by category
        monthly_data = self.analyzer.monthly_summary(start_date, end_date)
        
        if not monthly_data:
            return alerts
        
        # Calculate statistics for each category
        for category in set(cat for month_data in monthly_data.values() for cat in month_data.keys()):
            amounts = [month_data.get(category, 0.0) 
                      for month_data in monthly_data.values() 
                      if category in month_data]
            
            if len(amounts) < 3:  # Need at least 3 data points
                continue
            
            # Calculate mean and standard deviation
            mean = sum(amounts) / len(amounts)
            variance = sum((x - mean) ** 2 for x in amounts) / len(amounts)
            std_dev = variance ** 0.5
            
            if std_dev == 0:
                continue
            
            # Check for outliers
            for amount in amounts:
                z_score = abs((amount - mean) / std_dev) if std_dev > 0 else 0
                
                if z_score > std_dev_threshold:
                    alerts.append(Alert(
                        alert_type='unusual_spending',
                        severity='warning',
                        message=f"Unusual spending detected in {category}: ${amount:,.2f} "
                               f"(average: ${mean:,.2f}, {z_score:.1f} std dev)",
                        category=category,
                        amount=amount
                    ))
                    break  # Only alert once per category
        
        return alerts
    
    def detect_spending_spikes(self, start_date: Optional[datetime] = None,
                              end_date: Optional[datetime] = None,
                              spike_threshold: float = 1.5) -> List[Alert]:
        """Detect spending spikes (sudden increases).
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            spike_threshold: Multiplier for spike detection (1.5 = 50% increase)
            
        Returns:
            List of Alert objects
        """
        alerts = []
        
        # Get monthly spending by category
        monthly_data = self.analyzer.monthly_summary(start_date, end_date)
        
        if len(monthly_data) < 2:
            return alerts
        
        # Sort months
        sorted_months = sorted(monthly_data.keys())
        
        for category in set(cat for month_data in monthly_data.values() for cat in month_data.keys()):
            for i in range(1, len(sorted_months)):
                prev_month = sorted_months[i-1]
                curr_month = sorted_months[i]
                
                prev_amount = monthly_data[prev_month].get(category, 0.0)
                curr_amount = monthly_data[curr_month].get(category, 0.0)
                
                if prev_amount > 0 and curr_amount > prev_amount * spike_threshold:
                    increase_pct = ((curr_amount - prev_amount) / prev_amount) * 100
                    alerts.append(Alert(
                        alert_type='spending_spike',
                        severity='warning',
                        message=f"Spending spike in {category}: ${curr_amount:,.2f} in {curr_month} "
                               f"({increase_pct:.1f}% increase from {prev_month})",
                        category=category,
                        amount=curr_amount
                    ))
        
        return alerts
    
    def get_all_alerts(self, start_date: Optional[datetime] = None,
                      end_date: Optional[datetime] = None) -> List[Alert]:
        """Get all alerts.
        
        Args:
            start_date: Start date filter (inclusive)
            end_date: End date filter (inclusive)
            
        Returns:
            List of Alert objects, sorted by severity
        """
        alerts = []
        
        alerts.extend(self.check_budget_thresholds(start_date, end_date))
        alerts.extend(self.detect_unusual_spending(start_date, end_date))
        alerts.extend(self.detect_spending_spikes(start_date, end_date))
        
        # Sort by severity (critical > warning > info)
        severity_order = {'critical': 0, 'warning': 1, 'info': 2}
        alerts.sort(key=lambda a: severity_order.get(a.severity, 3))
        
        return alerts
