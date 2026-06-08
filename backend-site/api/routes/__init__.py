from fastapi import APIRouter
from api.routes import google_form_api

api_router = APIRouter()
api_router.include_router(google_form_api.router, tags=["auto_fill"], prefix="/google_form")