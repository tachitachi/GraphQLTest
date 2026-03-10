import logging
import os

import redis.asyncio as redis
from fastapi import Depends, FastAPI
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from strawberry.fastapi import GraphQLRouter

from database import get_session
from schema import schema


app = FastAPI(title="Personal Book Tracker API")
logging.basicConfig(level=os.getenv("LOG_LEVEL", "INFO"))

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
    redis_url = os.getenv("REDIS_URL")
    if redis_url:
        redis_client = redis.from_url(redis_url, decode_responses=True)


@app.on_event("shutdown")
async def _shutdown() -> None:
    global redis_client
    if redis_client is not None:
        await redis_client.aclose()
        redis_client = None


async def get_context(session: AsyncSession = Depends(get_session)):
    return {
        "session": session,
        "redis": redis_client
    }


graphql_app = GraphQLRouter(schema, context_getter=get_context)

app.include_router(graphql_app, prefix="/graphql")


@app.get("/health")
async def health_check():
    return {"status": "ok"}

