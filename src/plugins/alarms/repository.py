from pymongo.collection import Collection
from src.utils import get_collection
from fastapi import Request
from typing import List
from .schema import AlarmDetail, AlarmInput, Alarm
from bson import ObjectId

async def getAlarms(uid: List[str], request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None) -> List[Alarm]:
    alarms_collection = get_collection(request, alarms_collection, "alarms")
    alarms = alarms_collection.find({ "user_id": uid })
    return [AlarmDetail(**alarm) async for alarm in alarms]

async def createAlarm(uid: str, item: AlarmInput, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    alarms_collection = get_collection(request, alarms_collection, "alarms")
    alarm = Alarm(
        kpi_id=ObjectId(item.kpi_id),
        user_id=uid,
        site_id=item.site_id,
        threshold=item.threshold,
        threshold_type=item.threshold_type
    )
    result = await alarms_collection.insert_one(alarm.model_dump(by_alias=True))
    alarm = await alarms_collection.find_one({"_id": result.inserted_id})
    return AlarmDetail(**alarm)