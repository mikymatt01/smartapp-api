from src.custom_exceptions import AlarmNotFoundException
from pymongo.collection import Collection
from fastapi import Request
from .schema import AlarmDetail, AlarmInput, AlarmUpdate, AlarmOverview
from . import repository as alarm_repository

async def getAlarms(uid: str, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | Collection[AlarmOverview] | None = None):
    return await alarm_repository.getAlarms(uid, request=request, alarms_collection=alarms_collection)

async def createAlarm(uid: str, item: AlarmInput, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    return await alarm_repository.createAlarm(uid, item, request=request, alarms_collection=alarms_collection)

async def updateAlarm(id: str, item: AlarmUpdate, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    return await alarm_repository.updateAlarm(id, item, request=request, alarms_collection=alarms_collection)

async def deleteAlarm(id: str, request: Request | None = None, alarms_collection: Collection[AlarmDetail] | None = None):
    return await alarm_repository.deleteAlarm(id, request=request, alarms_collection=alarms_collection)