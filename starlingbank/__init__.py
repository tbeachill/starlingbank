"""Provides limited access to the Starling bank API."""
from .address import Address
from .card import Card
from .direct_debit import DirectDebit
from .payee import Payee
from .round_up import RoundUp
from .savings_goal import SavingsGoal
from .spending_insights import SpendingInsights
from .spending_space import SpendingSpace
from .standing_order import StandingOrder
from .starling_account import StarlingAccount

__all__ = [
    "Address", "Card", "DirectDebit", "Payee",
    "RoundUp", "SavingsGoal", "SpendingInsights",
    "SpendingSpace", "StandingOrder", "StarlingAccount"
]
