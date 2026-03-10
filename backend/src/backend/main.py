import logging

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import LOG_LEVEL, REDIS_URL
from backend.graphql.schema import graphql_app  # type: ignore[import]


app = FastAPI(title="Personal Book Tracker API")
logging.basicConfig(level=LOG_LEVEL)

redis_client: redis.Redis | None = None

origins = [
    "http://localhost:3000",
    "http://localhost:5173",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
async def _startup() -> None:
    global redis_client
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)


@app.on_event("shutdown")
async def _shutdown() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

