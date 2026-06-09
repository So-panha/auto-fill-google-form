# import os
# import sys

# # Tell Python to look inside the 'backend-site' directory for modules
# current_dir = os.path.dirname(os.path.abspath(__file__))
# if current_dir not in sys.path:
#     sys.path.insert(0, current_dir)

# from fastapi import FastAPI
# from fastapi.middleware.cors import CORSMiddleware
# from core import settings, app_exception_handler, AppException
# from api.routes import api_router

# app = FastAPI(
#     title=settings.PROJECT_NAME,
#     version=settings.VERSION,
#     openapi_url=f"{settings.API_V1_STR}/openapi.json"
# )   

# app.add_exception_handler(AppException, app_exception_handler)

# # Set all CORS enabled origins
# if settings.BACKEND_CORS_ORIGINS:
#     app.add_middleware(
#         CORSMiddleware,
#         allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
#         allow_credentials=True,
#         allow_methods=["*"],
#         allow_headers=["*"],
#     )

# # Include core API router   
# app.include_router(api_router, prefix=settings.API_V1_STR)

# @app.get("/check")
# def root():
#     return {"message": "Welcome to auto fill google form API"}








import os
import sys

# Tell Python to look inside the 'backend-site' directory for modules
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.insert(0, current_dir)

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core import settings, app_exception_handler, AppException
from api.routes import api_router

# CRITICAL FIX FOR VERCEL: Add root_path="/api"
app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    root_path="/api"  
)   

app.add_exception_handler(AppException, app_exception_handler)

# Set all CORS enabled origins
if settings.BACKEND_CORS_ORIGINS:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=[str(origin) for origin in settings.BACKEND_CORS_ORIGINS],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

# Include core API router   
app.include_router(api_router, prefix=settings.API_V1_STR)

# Move your check route under the FastAPI app context correctly
@app.get("/check")
def check_route():
    return {"message": "Welcome to auto fill google form API"}