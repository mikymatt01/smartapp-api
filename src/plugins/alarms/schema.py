from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime
from enum import Enum

class ThresholdType(str, Enum):
    UPPER_BOUND = "UPPER_BOUND"
    LOWER_BOUND = "LOWER_BOUND"

class AlarmDetail(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    kpi_id: PydanticObjectId
    user_id: str = Field(...)
    site_id: int = Field(...)
    machine_id: Optional[PydanticObjectId] = None
    threshold: float = Field(...)
    threshold_type: ThresholdType
    notified: bool = False
    enabled: bool = True
    created_at: datetime
    
class AlarmInput(BaseModel):
    kpi_id: PydanticObjectId
    site_id: int = Field(...)
    machine_id: Optional[PydanticObjectId] = None
    threshold: float = Field(...)
    threshold_type: ThresholdType
    
class Alarm(BaseModel):
    kpi_id: PydanticObjectId
    user_id: str = Field(...)
    site_id: int = Field(...)
    threshold: float = Field(...)
    threshold_type: ThresholdType
    notified: bool = False
    machine_id: Optional[PydanticObjectId] = None
    enabled: bool = True
    created_at: datetime = datetime.now()

class AlarmResponse(BaseModel):
    success: bool
    data: Optional[AlarmDetail | List[AlarmDetail]] = None
    message: Optional[str] = None