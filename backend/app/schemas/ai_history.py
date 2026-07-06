from pydantic import BaseModel, ConfigDict, Field
from typing import Optional
from datetime import datetime

class AIHistoryBase(BaseModel):
    """
    Base properties shared between AI history log request and response schemas.
    """
    user_id: int = Field(..., description="Foreign key referencing the associated User")
    generated_content: str = Field(..., description="Generative AI output markdown or plaintext copy")
    query_type: str = Field(..., max_length=100, description="Context classification category (e.g. settlement_letter, summary)")
    timestamp: datetime = Field(..., description="DateTime stamp recording request execution time")

class AIHistoryCreate(AIHistoryBase):
    """
    Schema for creating an AIHistory record.
    """
    pass

class AIHistoryUpdate(BaseModel):
    """
    Schema for updating an existing AIHistory record. All fields are optional.
    """
    generated_content: Optional[str] = None
    query_type: Optional[str] = Field(None, max_length=100)
    timestamp: Optional[datetime] = None

class AIHistoryResponse(AIHistoryBase):
    """
    Schema for reading AIHistory log details. Includes DB IDs and audit timestamps.
    """
    id: int
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)
