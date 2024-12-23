from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime
from enum import Enum

class ThresholdType(str, Enum):
    UPPER_BOUND = "UPPER_BOUND"
    LOWER_BOUND = "LOWER_BOUND"

class NotificationDetail(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    user_id: str = Field(...)
    alarm_id: str = Field(...)
    title: str = Field(...)
    message: str = Field(...)
    created_at: datetime

class NotificationResponse(BaseModel):
    success: bool
    data: Optional[NotificationDetail | List[NotificationDetail]] = None
    message: Optional[str] = None