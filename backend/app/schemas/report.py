from pydantic import BaseModel, ConfigDict
from typing import Optional, List, Dict, Any

class ReportRequest(BaseModel):
    """
    Schema validating reports generation/download request body or options.
    """
    include_detailed_amortization: Optional[bool] = False
    notes: Optional[str] = None

class ReportResponse(BaseModel):
    """
    Schema defining structure of generated report metadata.
    """
    report_type: str
    filename: str
    download_url: str
    generated_at: str

    model_config = ConfigDict(from_attributes=True)
