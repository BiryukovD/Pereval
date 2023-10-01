from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sql_app.crud import create_pereval, get_pereval_by_id, replace_pereval_by_id, get_perevals_by_email
from sql_app.schemas import Pereval, PerevalOut, PerevalReplace
from sql_app.database import get_async_session
from fastapi import FastAPI, Response

app = FastAPI(title='App')

@app.post('/pereval/')
async def submitData(pereval: Pereval, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await create_pereval(db, pereval)
    return {"status": 200, "message": 'Pereval created successfully!', "id_pereval": db_pereval.id}


@app.get('/pereval/{pereval_id}', response_model=PerevalOut)
async def submitData(pereval_id: int, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await get_pereval_by_id(db, pereval_id)
    if db_pereval is None:
        raise HTTPException(status_code=404, detail="Pereval not found")
    return db_pereval

@app.patch('/pereval/{pereval_id}')
async def submitData(pereval_id: int, pereval: PerevalReplace, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await replace_pereval_by_id(db, pereval_id, pereval)
    if db_pereval is None:
        raise HTTPException(status_code=404, detail="Pereval not found")
    return db_pereval

@app.get('/pereval/')
async def submitData(user_email: str, db: AsyncSession = Depends(get_async_session)):
    db_perevals = await get_perevals_by_email(db, user_email)
    if db_perevals is None:
        raise HTTPException(status_code=404, detail='User with this email not found')
    return db_perevals