"""Provides limited access to the Starling bank API."""
from .saving_space import SavingSpace
from .starling_account import StarlingAccount
from .spending_space import SpendingSpace
from .spending_insights import SpendingInsights
from .direct_debit import DirectDebit
from .standing_order import StandingOrder

__all__ = ["StarlingAccount", "SavingSpace", "SpendingSpace",
            "SpendingInsights", "DirectDebit", "StandingOrder"]
