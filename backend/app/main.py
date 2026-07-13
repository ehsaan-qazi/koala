from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings

from app.routes.auth import router as auth_router
from app.routes.courses import router as courses_router
from app.routes.billing import router as billing_router

app = FastAPI(
    title="Koala API",
    description="Backend API for the Koala learning app",
    version="1.0.0",
)

# Set up CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {"status": "ok", "message": "Koala API is running"}
app.include_router(auth_router, prefix="/api/v1")
app.include_router(courses_router, prefix="/api/v1")
app.include_router(billing_router, prefix="/api/v1")
