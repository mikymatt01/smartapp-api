import os
import logging
from . import service
from .schema import NotificationResponse, NotificationDetail
from fastapi import APIRouter, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token

logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

router = APIRouter(prefix=f"/api/{API_VERSION}/notification", tags=["Notifications"])

@router.get("/", status_code=200, response_model=NotificationResponse, summary="Get all notifications")
async def getNotifications(
    request: Request,
    user=Depends(verify_firebase_token)
):
    try:
        alarms = await service.getNotifications(user.uid, request=request)
        return NotificationResponse(success=True, data=alarms, message="Notifications retrieved successfully")
    except Exception as e:
        print(e)
        return NotificationResponse(success=False, data=None, message=f"Error getting notifications: {str(e)}")
    