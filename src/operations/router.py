from fastapi import APIRouter
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from operations.schemas import Pereval, PerevalOut, PerevalReplace
from database import get_async_session
from tasks.tasks import send_email
from fastapi import HTTPException,  BackgroundTasks
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from operations.models import User, Image, Level, Pereval
from operations.schemas import Pereval as Pereval_Schema
from fastapi_cache.decorator import cache

from sqlalchemy.exc import IntegrityError

router = APIRouter(
    prefix="/operations",
    tags=["Operations"]
)


# @router.get('/long')
# @cache(expire=30)
# def long():
#     time.sleep(3)
#     return "Много данных!!!"

@router.post('/pereval/')
async def submitData(pereval: Pereval_Schema, db: AsyncSession = Depends(get_async_session)):
    try:
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
        send_email.delay(pereval.user.name, pereval.user.email)
        return {"status": 200, "message": 'Pereval created successfully!', "id_pereval": pereval.id}
    except IntegrityError as exc:
        raise HTTPException(status_code=400, detail=f'{exc}')


@router.get('/pereval/{pereval_id}')
@cache(expire=60)
async def submitData(background_tasks: BackgroundTasks, pereval_id: int, db: AsyncSession = Depends(get_async_session)):
    db_pereval = await db.execute(
        select(Pereval, User, Level).join(User).join(
            Level).filter(Pereval.id == pereval_id))
    db_pereval = db_pereval.all()

    if db_pereval == []:
        raise HTTPException(status_code=404, detail="Pereval not found")

    db_images = await db.execute(select(Image).filter(Image.pereval_id == pereval_id))

    for pereval, user, level in db_pereval:
        return {
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


@router.patch('/pereval/{pereval_id}')
async def submitData(pereval_id: int, pereval: PerevalReplace, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(select(Pereval).filter(Pereval.id == pereval_id))
    db_pereval = result.scalars().first()

    if db_pereval is None:
        raise HTTPException(status_code=404, detail="Pereval not found")

    if db_pereval.status == 'new':
        # Если отправляются картинки, удаляем все картинки добавленные раннее, и добавляем список новых
        if pereval.image != None:
            lst_image_obj = []
            for image in pereval.image:
                lst_image_obj.append(
                    Image(title=image.title, image_url=str(image.image_url), pereval_id=pereval_id))
            stmt = delete(Image).where(Image.pereval_id == pereval_id)
            await db.execute(stmt)
            db.add_all(lst_image_obj)

        pereval_dict = pereval.dict(exclude_none=True)

        # Если отправляется level, обновляем level
        if pereval.level != None:
            # stmt = update(Level).where(Level.id == db_pereval.scalars().one().level_id).values(
            #     pereval_dict['level'])
            stmt = update(Level).where(Level.id == db_pereval.level_id).values(
                pereval_dict['level'])
            await db.execute(stmt)

        # Обновляем перевал
        pereval_dict.pop('image')
        pereval_dict.pop('level')
        stmt = update(Pereval).where(Pereval.id == pereval_id).values(pereval_dict)
        await db.execute(stmt)
        await db.commit()
        return {"state": 1, "message": 'Pereval updated successfully!'}
    else:
        raise HTTPException(status_code=400,
                            detail={'state': 0, "message": "Updating a pereval is possible only in new status!"})


@router.get('/pereval/')
@cache(expire=60)
async def submitData(user_email: str, db: AsyncSession = Depends(get_async_session)):
    result = await db.execute(
        select(Pereval, User, Level).join(User).join(
            Level).where(Pereval.user.has(User.email == user_email)))
    perevals = result.all()

    if perevals == []:
        raise HTTPException(status_code=400,
                            detail={'state': 0, "message": "Not found user with this email"})

    # все картинки добавленные пользователем
    result = await db.execute(
        select(Image).where(Image.pereval.has(Pereval.user.has(User.email == user_email))))

    images = result.scalars().all()
    perevals_out = []

    for pereval, user, level in perevals:
        perevals_out.append({
            'title': pereval.title,
            'other_title': pereval.other_title,
            'add_time': pereval.add_time,
            'status': pereval.status,
            'latitude': pereval.latitude,
            'longitude': pereval.longitude,
            'height': pereval.height,
            'user': user,
            'level': level,
            'images': [image for image in images if image.pereval_id == pereval.id]
        })
    return perevals_out
