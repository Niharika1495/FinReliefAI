from pydantic import BaseModel, ConfigDict
from typing import Optional
from datetime import datetime

class DocumentResponse(BaseModel):
    id: int
    user_id: int
    filename: str
    file_path: str
    file_type: str
    
    extracted_lender: Optional[str] = None
    extracted_amount: Optional[float] = None
    extracted_emi: Optional[float] = None
    extracted_interest_rate: Optional[float] = None
    extracted_due_date: Optional[str] = None
    extracted_loan_type: Optional[str] = None
    
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
