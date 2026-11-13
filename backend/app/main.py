from fastapi import FastAPI,Request
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
from .database import Base,engine
from . import models
from .config import settings
from .routers import auth,users,crud,safety
app=FastAPI(title="Smart Women Security API",version="1.0.0")
@app.on_event("startup")
def create_development_schema():
    """Convenience for a first local run; production schema changes use Alembic."""
    Base.metadata.create_all(bind=engine)
app.add_middleware(CORSMiddleware,allow_origins=settings.cors_origins.split(","),allow_credentials=True,allow_methods=["*"],allow_headers=["*"])
@app.exception_handler(Exception)
async def errors(request:Request,exc:Exception): return JSONResponse(status_code=500,content={"success":False,"message":"An unexpected server error occurred.","error_code":"INTERNAL_ERROR"})
app.include_router(auth.router,prefix="/api");app.include_router(users.router,prefix="/api");app.include_router(crud.router,prefix="/api");app.include_router(safety.router,prefix="/api")
@app.get("/health")
def health():return {"status":"ok"}
