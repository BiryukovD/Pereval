from fastapi import FastAPI
from operations.router import router as router_operations

from fastapi_cache import FastAPICache
from fastapi_cache.backends.redis import RedisBackend
from fastapi_cache.decorator import cache
from redis import asyncio as aioredis

app = FastAPI(title='App')



app.include_router(
    router_operations
)

@app.on_event("startup")
async def startup():
    redis = aioredis.from_url("redis://172.17.0.2:6379")
    FastAPICache.init(RedisBackend(redis), prefix="fastapi-cache")