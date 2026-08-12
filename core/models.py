from pydantic import BaseModel, Field
from typing import List, Optional

class RequestItem(BaseModel):
    id: str
    category: str = Field(description="automation, integration, analytics, support, consultation, or out_of_scope")
    target_department: Optional[str]
    priority: str = Field(description="low, medium, or high")
    short_summary: str
    requested_actions: List[str]
    needs_clarification: bool
    missing_info_reason: Optional[str]

class BatchResponse(BaseModel):
    items: List[RequestItem]