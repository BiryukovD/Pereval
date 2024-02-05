from fastapi import FastAPI
from operations.router import router as router_operations

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from redis import asyncio as aioredis
from config import REDIS_HOST, REDIS_PORT

app = FastAPI(title='App')



app.include_router(
    router_operations
)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url(f"redis://{REDIS_HOST}:{REDIS_PORT}")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")