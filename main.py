from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sql_app.crud import create_pereval, get_pereval_by_id
from sql_app.schemas import Pereval, PerevalOut
from sql_app.database import get_async_session
from fastapi import FastAPI, Response
from sql_app import models

app = FastAPI(title='App')


@app.post('/pereval/')
async def submitData(pereval: Pereval, response: Response, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await create_pereval(db, pereval)
    return {"status": 200, "message": 'Pereval created successfully!', "id_pereval": db_pereval.id}


@app.get('/pereval/{pereval_id}', response_model=PerevalOut)
async def submitData(pereval_id: int, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await get_pereval_by_id(db, pereval_id)
    return db_pereval
