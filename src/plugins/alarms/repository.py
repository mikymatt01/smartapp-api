from http.client import HTTPException
from pymongo.collection import Collection
from src.utils import get_collection
from fastapi import Request
from typing import List
from .schema import AlarmDetail, AlarmInput, Alarm, AlarmUpdate
from bson import ObjectId

async def getAlarms(uid: List[str], request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None) -> List[Alarm]:
    alarms_collection = get_collection(request, alarms_collection, "alarms")
    alarms = alarms_collection.find({ "user_id": uid }).sort('created_at', -1)
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

async def updateAlarm(id: str, item: AlarmUpdate, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    alarms_collection = get_collection(request, alarms_collection, "alarms")
    update_data = {k: v for k, v in item.dict().items() if v is not None}
    if not update_data:
        raise HTTPException(status_code=400, detail="No valid fields provided for update")  
    result = await alarms_collection.update_one(
        {"_id": ObjectId(id)},
        {"$set": update_data}
    )
    if result.matched_count == 0:
        raise HTTPException(status_code=404, detail="Document not found")
    alarm = await alarms_collection.find_one({"_id": ObjectId(id)})
    return AlarmDetail(**alarm)

async def deleteAlarm(id: str, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    alarms_collection = get_collection(request, alarms_collection, "alarms")
    result = alarms_collection.delete_one({"_id": ObjectId(id)})
    if result.deleted_count > 0:
        print("Document deleted successfully.")
    else:
        print("No document found with the given ID.")