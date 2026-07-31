from enum import Enum
from typing import List, Optional
from pydantic import BaseModel, Field

class Category(str, Enum):
    AUTOMATION = "автоматизація"
    INTEGRATION = "інтеграція"
    REPORT = "звіт/аналітика"
    BUG = "баг/підтримка"
    QUESTION = "питання/консультація"
    OUT_OF_SCOPE = "поза скоупом"

class Priority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"

class RawRequest(BaseModel):
    id: str
    channel: str
    timestamp: str
    raw_text: str

class ParsedRequest(BaseModel):
    id: str
    category: Category
    target_department: Optional[str] = None
    priority: Priority
    short_summary: str
    requested_actions: List[str] = Field(default_factory=list)
    needs_clarification: bool
    missing_info_reason: Optional[str] = None