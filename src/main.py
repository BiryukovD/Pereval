
from fastapi import FastAPI
from operations.router import router as router_operations

app = FastAPI(title='App')



app.include_router(
    router_operations
)