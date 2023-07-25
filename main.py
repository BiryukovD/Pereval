from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends
from sql_app.crud import create_pereval
from sql_app.schemas import Pereval
from sql_app.database import get_async_session
from fastapi import FastAPI, Response, status

app = FastAPI(title='App')


@app.post('/pereval/')
async def submitData(pereval: Pereval, response: Response, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await create_pereval(db, pereval)
    return {"status": 200, "message": 'Pereval created successfully!', "id_pereval": db_pereval.id}
