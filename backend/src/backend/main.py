from contextlib import asynccontextmanager
import logging

import redis.asyncio as redis
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.core.config import LOG_LEVEL, REDIS_URL
from backend.graphql import context as graphql_context
from backend.graphql.schema import graphql_app  # type: ignore[import]
from backend.realtime.redis_pubsub_mux import RedisPubSubMultiplexer
from backend.websocket.router import router as websocket_router

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client
    if REDIS_URL:
        redis_client = redis.from_url(REDIS_URL, decode_responses=True)
        graphql_context.redis_client = redis_client
        app.state.mux = RedisPubSubMultiplexer(redis_client)

    yield

    mux: RedisPubSubMultiplexer | None = getattr(app.state, "mux", None)
    if mux is not None:
        await mux.aclose()
        app.state.mux = None
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None
        graphql_context.redis_client = None

app = FastAPI(title="Personal Book Tracker API", lifespan=lifespan)
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


app.include_router(graphql_app, prefix="/graphql")
app.include_router(websocket_router)


@app.get("/health")
async def health_check():
    return {"status": "ok"}

