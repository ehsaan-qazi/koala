import sys
import asyncio
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

from app.config import settings
import app.models  # Register all ORM models

from app.routes.auth import router as auth_router
from app.routes.courses import router as courses_router
from app.routes.billing import router as billing_router
from app.routes.documents import router as documents_router
from app.routes.topics import router as topics_router
from app.routes.admin import router as admin_router

app = FastAPI(
    title="Koala API",
    description="Backend API for the Koala learning app",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Koala API is running"}

# Register all routers
app.include_router(auth_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
app.include_router(documents_router, prefix="/api/v1")
app.include_router(topics_router, prefix="/api/v1")
app.include_router(admin_router, prefix="/api/v1")
