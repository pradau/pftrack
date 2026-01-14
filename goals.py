"""
Author: Perry Radau
Date: 2025-01-27
Brief description: Goal tracking for savings and spending reduction
Dependencies: Python 3.6+
Usage: GoalTracker class to track progress toward financial goals
"""

import json
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional

from analyzer import SpendingAnalyzer
from transaction import Transaction


class Goal:
    """Represents a financial goal."""
    
    def __init__(self, name: str, goal_type: str, target: float,
                 deadline: Optional[datetime] = None,
                 category: Optional[str] = None,
                 current_amount: float = 0.0):
        """Initialize a goal.
        
        Args:
            name: Goal name
            goal_type: Type of goal ('savings' or 'spending_reduction')
            target: Target amount or percentage
            deadline: Optional deadline date
            category: Category name (for spending reduction goals)
            current_amount: Current progress amount
        """
        self.name = name
        self.goal_type = goal_type
        self.target = target
        self.deadline = deadline
        self.category = category
        self.current_amount = current_amount
    
    def progress_percentage(self) -> float:
        """Calculate progress as percentage.
        
        Returns:
            float: Progress percentage (0-100+)
        """
        if self.target == 0:
            return 0.0
        
        if self.goal_type == 'savings':
            return (self.current_amount / self.target) * 100.0
        elif self.goal_type == 'spending_reduction':
            # For spending reduction, target is percentage reduction
            # Progress is inverse: 100% means fully achieved
            return min(100.0, (self.current_amount / self.target) * 100.0)
        
        return 0.0
    
    def is_complete(self) -> bool:
        """Check if goal is complete.
        
        Returns:
            bool: True if goal is achieved
        """
        if self.goal_type == 'savings':
            return self.current_amount >= self.target
        elif self.goal_type == 'spending_reduction':
            return self.progress_percentage() >= 100.0
        
        return False
    
    def days_remaining(self) -> Optional[int]:
        """Calculate days remaining until deadline.
        
        Returns:
            Optional[int]: Days remaining, or None if no deadline
        """
        if self.deadline is None:
            return None
        
        delta = self.deadline - datetime.now()
        return max(0, delta.days)
    
    def to_dict(self) -> Dict:
        """Convert goal to dictionary for JSON serialization.
        
        Returns:
            Dict: Goal data
        """
        return {
            'name': self.name,
            'goal_type': self.goal_type,
            'target': self.target,
            'deadline': self.deadline.isoformat() if self.deadline else None,
            'category': self.category,
            'current_amount': self.current_amount
        }
    
    @classmethod
    def from_dict(cls, data: Dict) -> 'Goal':
        """Create Goal from dictionary.
        
        Args:
            data: Goal data dictionary
            
        Returns:
            Goal: Goal object
        """
        deadline = None
        if data.get('deadline'):
            deadline = datetime.fromisoformat(data['deadline'])
        
        return cls(
            name=data['name'],
            goal_type=data['goal_type'],
            target=data['target'],
            deadline=deadline,
            category=data.get('category'),
            current_amount=data.get('current_amount', 0.0)
        )


class GoalTracker:
    """Tracks progress toward financial goals."""
    
    def __init__(self, goals_path: Path = Path('goals.json')):
        """Initialize goal tracker.
        
        Args:
            goals_path: Path to JSON file storing goals
        """
        self.goals_path = Path(goals_path)
        self.goals: List[Goal] = []
        self._load_goals()
    
    def _load_goals(self) -> None:
        """Load goals from JSON file."""
        if self.goals_path.exists():
            try:
                with open(self.goals_path, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.goals = [Goal.from_dict(g) for g in data.get('goals', [])]
            except (json.JSONDecodeError, IOError, KeyError):
                self.goals = []
        else:
            self.goals = []
    
    def _save_goals(self) -> None:
        """Save goals to JSON file."""
        self.goals_path.parent.mkdir(parents=True, exist_ok=True)
        data = {
            'goals': [g.to_dict() for g in self.goals]
        }
        with open(self.goals_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, default=str)
    
    def add_goal(self, name: str, goal_type: str, target: float,
                 deadline: Optional[datetime] = None,
                 category: Optional[str] = None) -> Goal:
        """Add a new goal.
        
        Args:
            name: Goal name
            goal_type: Type of goal ('savings' or 'spending_reduction')
            target: Target amount or percentage
            deadline: Optional deadline date
            category: Category name (for spending reduction goals)
            
        Returns:
            Goal: Created goal
        """
        goal = Goal(name, goal_type, target, deadline, category)
        self.goals.append(goal)
        self._save_goals()
        return goal
    
    def update_goal_progress(self, analyzer: SpendingAnalyzer,
                            start_date: Optional[datetime] = None,
                            end_date: Optional[datetime] = None) -> None:
        """Update goal progress based on transaction analysis.
        
        Args:
            analyzer: SpendingAnalyzer with transaction data
            start_date: Start date for progress calculation
            end_date: End date for progress calculation
        """
        for goal in self.goals:
            if goal.goal_type == 'savings':
                # For savings goals, track income minus expenses
                income_expenses = analyzer.income_vs_expenses(start_date, end_date)
                goal.current_amount = income_expenses['net']
            
            elif goal.goal_type == 'spending_reduction':
                # For spending reduction, compare current spending to baseline
                if goal.category:
                    category_totals = analyzer.category_totals(start_date, end_date)
                    current_spending = category_totals.get(goal.category, 0.0)
                    
                    # Target is percentage reduction, so calculate progress
                    # This is simplified - in practice, you'd need baseline data
                    goal.current_amount = current_spending
        
        self._save_goals()
    
    def get_goals(self) -> List[Goal]:
        """Get all goals.
        
        Returns:
            List[Goal]: List of all goals
        """
        return self.goals
    
    def get_goal(self, name: str) -> Optional[Goal]:
        """Get a goal by name.
        
        Args:
            name: Goal name
            
        Returns:
            Optional[Goal]: Goal if found, None otherwise
        """
        for goal in self.goals:
            if goal.name == name:
                return goal
        return None
    
    def delete_goal(self, name: str) -> bool:
        """Delete a goal by name.
        
        Args:
            name: Goal name
            
        Returns:
            bool: True if goal was deleted, False if not found
        """
        for i, goal in enumerate(self.goals):
            if goal.name == name:
                del self.goals[i]
                self._save_goals()
                return True
        return False
