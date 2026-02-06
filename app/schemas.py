from pydantic import BaseModel
from typing import Optional

# This Pydantic model defines the structure of an incoming transaction.
# It includes all the features that the machine learning model was trained on.
class Transaction(BaseModel):
    Time: float
    V1: float
    V2: float
    V3: float
    V4: float
    V5: float
    V6: float
    V7: float
    V8: float
    V9: float
    V10: float
    V11: float
    V12: float
    V13: float
    V14: float
    V15: float
    V16: float
    V17: float
    V18: float
    V19: float
    V20: float
    V21: float
    V22: float
    V23: float
    V24: float
    V25: float
    V26: float
    V27: float
    V28: float
    Amount: float
    
    # The following fields are optional and are not used by the model,
    # but can be useful for logging and tracking.
    transaction_id: Optional[str] = None
    user_id: Optional[str] = None
