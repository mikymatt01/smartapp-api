"""Machine controller. This module defines the API routes for the Machine plugin."""
from fastapi import APIRouter, HTTPException, Depends, Query, Path, Security
from fastapi.requests import Request


from src.plugins.auth.firebase import verify_firebase_token_and_role, verify_firebase_token
from src.plugins.machine import repository
from .schema import MachineOverview, MachineDetail, MachineResponse

import os
import logging

API_VERSION = os.getenv("VERSION")
logger = logger = logging.getLogger('uvicorn.error')

router = APIRouter(prefix=f"/api/{API_VERSION}/machine", tags=["Machine"])

# list all machines
@router.get("/",status_code=200, response_model=MachineResponse, summary="Get all machines in the dataset")
async def get_all_machines(request:Request, user=Depends(verify_firebase_token)):
    """
    Get all machines in the dataset

    Returns:
    - MachineResponse: A response object containing the list of machines
    """
    try:
        machines = await repository.get_all(request)

        return MachineResponse(success=True, data=machines, message="Machines listed successfully")
    except Exception as e:
        logger.error(f"Error getting all machines: {e}")
        return MachineResponse(success=False, data=None, message=str(e))
        #raise HTTPException(status_code=500, detail=str(e))

@router.get("/site",status_code=200, response_model=MachineResponse, summary="Get all machines in the dataset")
async def get_all_machines(site: int, request:Request, user=Depends(verify_firebase_token)):
    """
    Get all machines in the dataset

    Returns:
    - MachineResponse: A response object containing the list of machines
    """
    try:
        machines = await repository.get_by_site(site, request)

        return MachineResponse(success=True, data=machines, message="Machines listed successfully")
    except Exception as e:
        logger.error(f"Error getting all machines: {e}")
        return MachineResponse(success=False, data=None, message=str(e))
        #raise HTTPException(status_code=500, detail=str(e))

# filter
@router.get("/filter", response_model=MachineResponse, status_code=201, summary="Filter machines by type or name")
async def filter_machines(request: Request, machine_name: str = None, machine_type: str = None, user=Depends(verify_firebase_token)):
    """
    Filter machines by type or name

    Args:
    - machine_name: The name of the machine to filter by
    - machine_type: The type of the machine to filter by

    Returns:
    - MachineResponse: A response object containing the list of machines that match the filter
    """
    try:
        if machine_name:
            machines = await repository.get_by_name(machine_name, machine_type=machine_type, request=request)
        elif machine_type:
            machines = await repository.get_by_type(machine_type, request=request)
        else:
            return MachineResponse(success=False, data=None, message="No filter provided")
        return MachineResponse(success=True, data=machines, message="Machines filtered successfully")
    except Exception as e:
        logger.error(f"Error filtering machines: {e}")
        return MachineResponse(success=False, data=None, message=str(e))

# get machine by ID
@router.get("/{machine_id}", response_model=MachineResponse, status_code=200, summary="Get machine by ID")
async def get_machine_by_id(request: Request, machine_id: str, user=Depends(verify_firebase_token)):
    """
    Get machine by ID

    Args:
    - machine_id: The ID of the machine to retrieve

    Returns:
    - MachineResponse: A response object containing the machine
    """
    try:

        machine = await repository.get_by_id(machine_id, request=request)

        return MachineResponse(success=True, data=machine, message="Machine retrieved successfully")
    except Exception as e:
        logger.error(f"Error getting machine by ID: {e}")
        return MachineResponse(success=False, data=None, message=str(e))
        # raise HTTPException(status_code=500, detail=str(e))