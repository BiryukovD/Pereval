from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from operations.crud import create_pereval, get_pereval_by_id, replace_pereval_by_id, get_perevals_by_email
from operations.schemas import Pereval, PerevalOut, PerevalReplace
from database import get_async_session

from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from operations.models import User, Image, Level, Pereval
from operations.schemas import Pereval as Pereval_Schema



router = APIRouter(
    prefix="/operations",
    tags=["Operations"]
)

@router.post('/pereval/')
async def submitData(pereval: Pereval_Schema, db: AsyncSession = Depends(get_async_session)):
    # db_pereval = await create_pereval(db, pereval)
    result = await db.execute(select(User).where(User.email == pereval.user.email))
    user = result.scalars().first()
    if user is None:
        user = User(**pereval.user.dict())
    db_list_of_images = []
    for image in pereval.images:
        db_list_of_images.append(Image(image_url=str(image.image_url), title=image.title))
    level = Level(**pereval.level.dict())
    pereval = Pereval(
        title=pereval.title,
        other_title=pereval.other_title,
        latitude=pereval.coords.latitude,
        longitude=pereval.coords.longitude,
        height=pereval.coords.height,
        user=user,
        level=level,
        image=db_list_of_images
    )
    db.add(pereval)
    await db.commit()
    # return pereval
    return {"status": 200, "message": 'Pereval created successfully!', "id_pereval": pereval.id}


@router.get('/pereval/{pereval_id}')
async def submitData(pereval_id: int, db: AsyncSession = Depends(get_async_session)):
    # db_pereval = await get_pereval_by_id(db, pereval_id)
    db_pereval = await db.execute(
        select(Pereval, User, Level).join(User).join(
            Level).filter(Pereval.id == pereval_id))
    if db_pereval.scalars().first() == None:
        raise HTTPException(status_code=404, detail="Pereval not found")



    db_images = await db.execute(select(Image).filter(Image.pereval_id == pereval_id))

    pereval_d = {}
    for pereval, user, level in db_pereval:
        pereval_d = {
            'title': pereval.title,
            'other_title': pereval.other_title,
            'add_time': pereval.add_time,
            'status': pereval.status,
            'latitude': pereval.latitude,
            'longitude': pereval.longitude,
            'height': pereval.height,
            'user': user,
            'level': level,
            'images': db_images.scalars().all()
        }

    return pereval_d

@router.patch('/pereval/{pereval_id}')
async def submitData(pereval_id: int, pereval: PerevalReplace, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await replace_pereval_by_id(db, pereval_id, pereval)
    if db_pereval is None:
        raise HTTPException(status_code=404, detail="Pereval not found")
    return db_pereval

@router.get('/pereval/')
async def submitData(user_email: str, db: AsyncSession = Depends(get_async_session)):
    db_perevals = await get_perevals_by_email(db, user_email)
    if db_perevals is None:
        raise HTTPException(status_code=404, detail='User with this email not found')
    return db_perevals