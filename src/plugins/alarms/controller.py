import os
import logging
from . import service
from .schema import AlarmResponse, AlarmDetail, AlarmInput, AlarmUpdate
from fastapi import APIRouter, Depends, Request
from src.plugins.auth.firebase import verify_firebase_token

logger = logging.getLogger('uvicorn.error')
API_VERSION = os.getenv("VERSION")
DEBUG = os.getenv("DEBUG")
CSV_FILE_PATH = os.getenv("CSV_FILE_PATH")

router = APIRouter(prefix=f"/api/{API_VERSION}/alarm", tags=["Alarms"])

@router.get("/", status_code=200, response_model=AlarmResponse, summary="Get all alarms")
async def getAlarms(
    request: Request,
    user=Depends(verify_firebase_token)
):
    try:
        alarms = await service.getAlarms(user.uid, request=request)
        return AlarmResponse(success=True, data=alarms, message="Alarms retrieved successfully")
    except Exception as e:
        print(e)
        return AlarmResponse(success=False, data=None, message=f"Error getting alarms: {str(e)}")
    
@router.post("/", status_code=200, response_model=AlarmResponse, summary="Create alarm")
async def createAlarm(
    item: AlarmInput,
    request: Request,
    user=Depends(verify_firebase_token)
):
    try:
        alarm = await service.createAlarm(user.uid, item, request=request)
        return AlarmResponse(success=True, data=alarm, message="Alarm created successfully")
    except Exception as e:
        return AlarmResponse(success=False, data=None, message=f"Error creating alarm: {str(e)}")
    
@router.put("/{id}", status_code=200, response_model=AlarmResponse, summary="Update alarm")
async def createAlarm(
    id: str,
    item: AlarmUpdate,
    request: Request,
    user=Depends(verify_firebase_token)
):
    try:
        alarm = await service.updateAlarm(id, item, request=request)
        return AlarmResponse(success=True, data=alarm, message="Alarm updated successfully")
    except Exception as e:
        return AlarmResponse(success=False, data=None, message=f"Error updating alarm: {str(e)}")
    
@router.delete("/{id}", status_code=200, response_model=AlarmResponse, summary="Delete alarm")
async def createAlarm(
    id: str,
    request: Request,
    user=Depends(verify_firebase_token)
):
    try:
        await service.deleteAlarm(id, request=request)
        return AlarmResponse(success=True, data={}, message="Alarm deleted successfully")
    except Exception as e:
        return AlarmResponse(success=False, data=None, message=f"Error deleting alarm: {str(e)}")
   