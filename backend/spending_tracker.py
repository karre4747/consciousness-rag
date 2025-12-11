#!/usr/bin/env python3
"""
Track Claude API spending with monthly caps
"""

import sqlite3
from datetime import datetime, date
from typing import Dict, List, Optional, Any
import os

# Store database in a persistent system location, NOT in the code repository
# This prevents git operations/resets from deleting the data
DB_DIR = "/etc/evolve"
if not os.path.exists(DB_DIR):
    try:
        os.makedirs(DB_DIR, mode=0o755, exist_ok=True)
    except OSError:
        # Fallback for local development (mac/windows) where /etc/evolve might not be writable
        DB_DIR = os.path.join(os.path.expanduser("~"), ".evolve_data")
        os.makedirs(DB_DIR, mode=0o755, exist_ok=True)

DB_PATH = os.path.join(DB_DIR, "claude_spending.db")
DEFAULT_MONTHLY_CAP = 20.00  # $20/month default

class SpendingTracker:
    def __init__(self):
        self.init_database()

    def init_database(self):
        """Create tables if they don't exist"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            # Table 1: Spending history
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS spending_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    analysis_type TEXT,
                    document_count INTEGER,
                    chunk_count INTEGER,
                    input_tokens INTEGER,
                    output_tokens INTEGER,
                    input_cost REAL,
                    output_cost REAL,
                    total_cost REAL,
                    batch_count INTEGER,
                    duration_seconds INTEGER
                )
            ''')

            # Table 2: Monthly spending caps
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS monthly_caps (
                    month TEXT PRIMARY KEY,
                    cap_amount REAL,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            ''')

            conn.commit()

    def get_current_month_spending(self) -> float:
        """Get total spending for current month"""
        current_month = date.today().strftime("%Y-%m")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT COALESCE(SUM(total_cost), 0)
                FROM spending_history
                WHERE strftime('%Y-%m', timestamp) = ?
            ''', (current_month,))

            total = cursor.fetchone()[0]

        return round(total, 2)

    def get_monthly_cap(self) -> float:
        """Get spending cap for current month"""
        current_month = date.today().strftime("%Y-%m")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT cap_amount FROM monthly_caps WHERE month = ?
            ''', (current_month,))

            result = cursor.fetchone()

        if result:
            return result[0]
        else:
            # No cap set for this month, use default
            return DEFAULT_MONTHLY_CAP

    def set_monthly_cap(self, new_cap: float):
        """Set or update spending cap for current month"""
        current_month = date.today().strftime("%Y-%m")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT OR REPLACE INTO monthly_caps (month, cap_amount)
                VALUES (?, ?)
            ''', (current_month, new_cap))

            conn.commit()

    def can_afford(self, estimated_cost: float) -> Dict[str, Any]:
        """
        Check if we can afford this analysis within monthly cap

        Returns:
            {
                "can_proceed": bool,
                "current_spending": float,
                "monthly_cap": float,
                "remaining_budget": float,
                "would_exceed_by": float (if can_proceed=False)
            }
        """
        current_spending = self.get_current_month_spending()
        monthly_cap = self.get_monthly_cap()
        remaining_budget = monthly_cap - current_spending

        can_proceed = (current_spending + estimated_cost) <= monthly_cap
        would_exceed_by = 0 if can_proceed else (current_spending + estimated_cost - monthly_cap)

        return {
            "can_proceed": can_proceed,
            "current_spending": round(current_spending, 2),
            "monthly_cap": round(monthly_cap, 2),
            "remaining_budget": round(remaining_budget, 2),
            "would_exceed_by": round(would_exceed_by, 2)
        }

    def record_analysis(self, analysis_data: Dict):
        """Record a completed Claude analysis"""
        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                INSERT INTO spending_history (
                    analysis_type, document_count, chunk_count,
                    input_tokens, output_tokens, input_cost, output_cost,
                    total_cost, batch_count, duration_seconds
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                analysis_data.get('analysis_type'),
                analysis_data.get('document_count'),
                analysis_data.get('chunk_count'),
                analysis_data.get('input_tokens'),
                analysis_data.get('output_tokens'),
                analysis_data.get('input_cost'),
                analysis_data.get('output_cost'),
                analysis_data.get('total_cost'),
                analysis_data.get('batch_count'),
                analysis_data.get('duration_seconds')
            ))

            conn.commit()

    def get_monthly_history(self, month: Optional[str] = None) -> List[Dict]:
        """
        Get all analyses for a specific month

        Args:
            month: Format "2025-11", defaults to current month
        """
        if not month:
            month = date.today().strftime("%Y-%m")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    timestamp, analysis_type, document_count,
                    input_tokens, output_tokens, total_cost
                FROM spending_history
                WHERE strftime('%Y-%m', timestamp) = ?
                ORDER BY timestamp DESC
            ''', (month,))

            rows = cursor.fetchall()

        return [
            {
                "timestamp": row[0],
                "analysis_type": row[1],
                "document_count": row[2],
                "input_tokens": row[3],
                "output_tokens": row[4],
                "total_cost": row[5]
            }
            for row in rows
        ]

    def get_monthly_stats(self, month: Optional[str] = None) -> Dict:
        """Get aggregated stats for a month"""
        if not month:
            month = date.today().strftime("%Y-%m")

        with sqlite3.connect(DB_PATH) as conn:
            cursor = conn.cursor()

            cursor.execute('''
                SELECT
                    COUNT(*) as analysis_count,
                    SUM(document_count) as total_docs,
                    SUM(input_tokens) as total_input_tokens,
                    SUM(output_tokens) as total_output_tokens,
                    SUM(total_cost) as total_cost
                FROM spending_history
                WHERE strftime('%Y-%m', timestamp) = ?
            ''', (month,))

            row = cursor.fetchone()

        return {
            "month": month,
            "analysis_count": row[0] or 0,
            "total_documents_analyzed": row[1] or 0,
            "total_input_tokens": row[2] or 0,
            "total_output_tokens": row[3] or 0,
            "total_cost": round(row[4] or 0, 2),
            "monthly_cap": self.get_monthly_cap()
        }
