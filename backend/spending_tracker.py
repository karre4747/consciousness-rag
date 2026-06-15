"""
Spending Tracker Stub
Provides basic budget tracking for API usage.
"""
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class SpendingTracker:
    def __init__(self, monthly_cap=20.0):
        self.monthly_cap = monthly_cap
        self.current_spending = 0.0
        
    def record_analysis(self, data):
        """Record spending from an analysis job"""
        cost = data.get("total_cost", 0.0)
        self.current_spending += cost
        logger.info(f"Recorded spending: ${cost:.4f}. Total: ${self.current_spending:.2f}")
        
    def get_monthly_stats(self, month=None):
        """Get stats for the dashboard"""
        return {
            "total_cost": self.current_spending,
            "total_input_tokens": 0,  # Stubbed
            "total_output_tokens": 0, # Stubbed
            "monthly_cap": self.monthly_cap,
            "remaining": max(0, self.monthly_cap - self.current_spending),
            "percent_used": (self.current_spending / self.monthly_cap) * 100 if self.monthly_cap > 0 else 0
        }
        
    def get_monthly_history(self, month=None):
        """Mock history for the chart"""
        return []
        
    def get_spending_breakdown(self, month=None):
        """Mock breakdown by provider"""
        return {
            "openai": 0.0,
            "anthropic": self.current_spending,
            "google": 0.0
        }
        
    def set_monthly_cap(self, new_cap):
        """Update the budget cap"""
        self.monthly_cap = new_cap
        return True
        
    def can_afford(self, estimated_cost):
        """Check if within budget"""
        can = (self.current_spending + estimated_cost) <= self.monthly_cap
        return {
            "can_afford": can,
            "current_spending": self.current_spending,
            "estimated_cost": estimated_cost,
            "cap": self.monthly_cap
        }
