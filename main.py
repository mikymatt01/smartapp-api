import sys, os
from fastapi import Depends, FastAPI, APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import HTMLResponse, RedirectResponse
from contextlib import asynccontextmanager
from fastapi.requests import Request
from fastapi_utilities import repeat_at, repeat_every

sys.path.append(os.path.abspath("."))
from src.plugins.auth.firebase import verify_firebase_token
from src.plugins.machine import controller as machine_controller
from src.plugins.user import controller as user_controller
from src.plugins.kpi import controller as kpi_controller
from src.plugins.site import controller as site_controller
from src.plugins.report import controller as report_controller
# from src.plugins.chat import controller as chat_controller
# from src.plugins.anomalies import controller as anomalies_controller
from utils import description
from src.config.firebase_config import initialize_firebase
from src.config.db_config import AsyncDatabase, SyncDatabase
from reports.tests_report_mongodb import mock_reports

import logging
from dotenv import load_dotenv
load_dotenv()

logger = logger = logging.getLogger('uvicorn.error')

initialize_firebase()


@asynccontextmanager
async def startup_shutdown_db(app: FastAPI):

    async_db_obj = AsyncDatabase("DATABASE_URL", "DATABASE_NAME")
    app.mongodb = async_db_obj.get_db()
    app.mongodb_obj = async_db_obj

    # await app.mongodb['reports'].drop()
    # await create_report_collection(mongodb=app.mongodb)

    # app.mongodb['reports'].insert_many(report.model_dump() for report in mock_reports)

    yield
    async_db_obj.client.close()

API_VERSION = os.getenv("VERSION")

app = FastAPI(
    title="Industry 5.0 RESTful API",
    description=description,
    version=API_VERSION,
    docs_url=f"/api/{API_VERSION}/docs",
    redoc_url=f"/api/{API_VERSION}/redoc",
    lifespan=startup_shutdown_db
)

# CORS settings for local development
origins = [
    "http://localhost.tiangolo.com",
    "https://localhost.tiangolo.com",
    "http://localhost",
    "http://localhost:8080",
    "http://localhost:3000",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")

@app.get("/docs", summary="Redirect to Swagger docs")
async def redirect_to_docs():
    return RedirectResponse(url=f"/api/{API_VERSION}/docs")

@app.get("/redoc", summary="Redirect to ReDoc docs")
async def redirect_to_redoc():
    return RedirectResponse(url=f"/api/{API_VERSION}/redoc")

@app.get("/health/mongodb", summary="Check MongoDB connection")
async def check_mongodb_connection(request: Request):

    if isinstance(request.app.mongodb_obj, AsyncDatabase):
        return await request.app.mongodb_obj.check_mongodb_connection()
    else:
        return request.app.mongodb_obj.check_mongodb_connection()

@app.get(
        "/mongodb/list_all_data",
        summary="List all data in MongoDB",
        response_class=HTMLResponse,
        # include_in_schema=False

    )
async def list_all_data(request: Request, user=Depends(verify_firebase_token)):

    return await request.app.mongodb_obj.list_all_data()

router = APIRouter(prefix=f"/api/{API_VERSION}", tags=["API"])

app.include_router(router)
app.include_router(machine_controller.router)
app.include_router(user_controller.router)
app.include_router(kpi_controller.router)
app.include_router(site_controller.router)
app.include_router(report_controller.router)
# app.include_router(chat_controller.router)
# app.include_router(anomalies_controller.router)