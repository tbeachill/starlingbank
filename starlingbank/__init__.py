"""Provides limited access to the Starling bank API."""
from .saving_space import SavingSpace
from .starling_account import StarlingAccount
from .spending_space import SpendingSpace

__all__ = ["StarlingAccount", "SavingSpace", "SpendingSpace"]
