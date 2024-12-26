from pymongo.collection import Collection
from src.utils import get_collection
from fastapi import Request
from typing import List
from .schema import NotificationDetail

async def getNotifications(uid: str, request: Request | None = None, notifications_collection: Collection[NotificationDetail] | None = None) -> List[NotificationDetail]:
    notifications_collection = get_collection(request, notifications_collection, "notifications")
    notifications = notifications_collection.find({ "user_id": uid })
    return [NotificationDetail(**notification) async for notification in notifications]

async def setNotificationsAsSeen(uid: str, request: Request | None = None, notifications_collection: Collection[NotificationDetail] | None = None) -> List[NotificationDetail]:
    notifications_collection = get_collection(request, notifications_collection, "notifications")
    await notifications_collection.update_many(
        { "user_id": uid }, 
        {
            "$set": { "seen": True } 
        }
    )
    return await getNotifications(uid, request=request, notifications_collection=notifications_collection)