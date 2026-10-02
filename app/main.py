import asyncio
from contextlib import asynccontextmanager, suppress

from fastapi import FastAPI
from fastapi.responses import Response
from prometheus_client import CONTENT_TYPE_LATEST, generate_latest

from app.batch_service import run_batch_loop
from app.config import settings
from app.db import create_all
from app.routers import couriers, orders


@asynccontextmanager
async def lifespan(app: FastAPI):
    await create_all()
    worker = asyncio.create_task(run_batch_loop()) if settings.matcher_strategy == "batch" else None
    yield
    if worker:
        worker.cancel()
        with suppress(asyncio.CancelledError):
            await worker


app = FastAPI(title="Courier Dispatch", lifespan=lifespan)

app.include_router(orders.router)
app.include_router(couriers.router)


@app.get("/health")
async def health():
    return {"status": "ok"}


@app.get("/metrics")
async def metrics():
    return Response(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)
