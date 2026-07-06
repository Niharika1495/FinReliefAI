from pydantic import BaseModel, ConfigDict
from datetime import datetime

class NotificationResponse(BaseModel):
    """
    Schema validating the structured notifications response.
    """
    id: int
    user_id: int
    title: str
    message: str
    type: str
    is_read: bool
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
