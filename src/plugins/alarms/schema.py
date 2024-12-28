from typing import List
from pydantic import BaseModel, Field
from pydantic_mongo import PydanticObjectId
from typing import Optional
from datetime import datetime
from enum import Enum

class ThresholdType(str, Enum):
    UPPER_BOUND = "UPPER_BOUND"
    LOWER_BOUND = "LOWER_BOUND"
    
class OperationType(str, Enum):
    sum = "sum"
    avg = "avg"
    min = "min"
    max = "max"
    std = "std"

class AlarmOverview(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    kpi_id: PydanticObjectId
    op: OperationType
    kpi_name: Optional[str] = None
    user_id: str = Field(...)
    site_id: int = Field(...)
    machine_id: Optional[PydanticObjectId] = None
    machine_name: Optional[str] = None
    threshold: float = Field(...)
    threshold_type: ThresholdType
    notified: bool = False
    enabled: bool = True
    created_at: datetime
   
class AlarmDetail(BaseModel):
    id: PydanticObjectId = Field(alias="_id")
    kpi_id: PydanticObjectId
    op: OperationType
    user_id: str = Field(...)
    site_id: int = Field(...)
    machine_id: Optional[PydanticObjectId] = None
    threshold: float = Field(...)
    threshold_type: ThresholdType
    notified: bool = False
    enabled: bool = True
    created_at: datetime 
class AlarmInput(BaseModel):
    op: OperationType
    kpi_id: str
    site_id: int = Field(...)
    machine_id: Optional[str] = None
    threshold: float = Field(...)
    threshold_type: ThresholdType
    
class AlarmUpdate(BaseModel):
    op: Optional[OperationType] = None
    kpi_id: Optional[str] = None
    site_id: Optional[int] = None
    machine_id: Optional[str] = None
    threshold: Optional[float] = None
    threshold_type: Optional[ThresholdType] = None
    enabled: Optional[bool] = None
    
class Alarm(BaseModel):
    kpi_id: PydanticObjectId
    op: OperationType
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
    data: Optional[AlarmDetail | List[AlarmDetail] | List[AlarmOverview]] = None
    message: Optional[str] = None