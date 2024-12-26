from src.custom_exceptions import AlarmNotFoundException
from pymongo.collection import Collection
from fastapi import Request
from .schema import NotificationDetail
from . import repository as alarm_repository

async def getNotifications(uid: str, request: Request | None = None, notifications_collection: Collection[NotificationDetail] | None = None):
    return await alarm_repository.getNotifications(uid, request=request, notifications_collection=notifications_collection)

async def setNotificationsAsSeen(uid: str, request: Request | None = None, notifications_collection: Collection[NotificationDetail] | None = None):
    return await alarm_repository.setNotificationsAsSeen(uid, request=request, notifications_collection=notifications_collection)
