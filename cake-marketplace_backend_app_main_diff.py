--- cake-marketplace/backend/app/main.py (原始)


+++ cake-marketplace/backend/app/main.py (修改后)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.db.database import engine, Base
from app.api.routes import router

# Create database tables
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Cake Marketplace API",
    description="Marketplace for self-employed confectioners",
    version="1.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify exact origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(router, prefix="/api/v1")

@app.get("/")
def read_root():
    return {
        "message": "Welcome to Cake Marketplace API",
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def health_check():
    return {"status": "healthy"}