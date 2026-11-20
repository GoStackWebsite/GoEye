"""FastAPI application entry point."""
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import settings
from backend.core.database import create_tables, engine
from backend.core.exceptions import register_exception_handlers
from backend.core.responses import ApiResponse, ok
from backend.modules.auth.router import router as auth_router
from backend.modules.cameras.router import router as cameras_router
from backend.modules.events.router import router as events_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_tables()
    yield
    await engine.dispose()


app = FastAPI(title="goeye", lifespan=lifespan)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
register_exception_handlers(app)

app.include_router(auth_router)
app.include_router(cameras_router)
app.include_router(events_router)


@app.get("/health", tags=["health"], response_model=ApiResponse[None])
def health():
    return ok(message="ok")
