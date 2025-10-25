from pydantic import BaseModel
from typing import Literal

# This file contains shared Pydantic models (schemas) to avoid circular imports.

class Transaction(BaseModel):
    transaction_id: str
    user_id: str
    amount: float
    currency: str
    timestamp: str
    # New features for a more realistic model
    payment_method: Literal['credit_card', 'upi', 'wallet', 'net_banking']
    country: Literal['IN', 'US', 'GB', 'DE', 'AU'] # Example countries
