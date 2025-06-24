from fastapi import FastAPI
from contextlib import asynccontextmanager
import os

from backend.database import engine, Base # type: ignore
# Updated to include stocks_router
from backend.routers import auth_router, users_router, websockets_router, stocks_router
# Import other routers as they are created, e.g.:
# from backend.routers import forex_router

# Lifespan manager for startup/shutdown events (replaces on_event)
@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup: Create database tables if they do not exist
    print("FastAPI application startup: Creating database tables...")
    # Ensure data directory exists for SQLite before creating tables
    if "sqlite" in str(engine.url.drivername): # Convert drivername to string
        db_url_path = str(engine.url.database) # Ensure it is a string
        # Check for relative path like "./data/file.db"
        if db_url_path.startswith("./"):
            db_url_path = db_url_path[2:] # Remove leading "./"

        db_dir = os.path.dirname(db_url_path)
        if db_dir and not os.path.exists(db_dir): # Ensure db_dir is not empty string for root path
            os.makedirs(db_dir, exist_ok=True)
            print(f"Created directory for SQLite DB: {db_dir}")
    Base.metadata.create_all(bind=engine)
    print("Database tables checked/created.")
    yield
    # Shutdown: Any cleanup can go here
    print("FastAPI application shutdown.")

app = FastAPI(
    title="Financial Dashboard API",
    version="0.1.0",
    description="API for the Interactive Financial Dashboard",
    lifespan=lifespan
)

@app.get("/")
async def root():
    return {"message": "Welcome to the Financial Dashboard API. See /docs for API details."}

# Include routers
app.include_router(auth_router.router, prefix="/auth", tags=["Authentication"])
app.include_router(users_router.router, prefix="/users", tags=["Users"])
app.include_router(stocks_router.router, prefix="/stocks", tags=["Stock Prices"]) # Added stocks_router
app.include_router(websockets_router.router, prefix="/ws_example", tags=["WebSocket Example"])

# Example: app.include_router(forex_router.router, prefix="/forex", tags=["Forex"])

if __name__ == "__main__":
    import uvicorn
    # The uvicorn.run command is typically used when running the file directly.
    # For development, it is better to run from the command line:
    # uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
    # The lifespan event for creating DB dir/tables will be handled by FastAPI startup.

    # This uvicorn.run is mainly for easy execution if someone runs `python backend/main.py`
    # For production or robust dev, CLI uvicorn is preferred.
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True, app_dir="backend")
