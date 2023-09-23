from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.responses import JSONResponse

from sql_app import models
from sql_app.schemas import Pereval


async def create_pereval(db: AsyncSession, pereval: Pereval):
    db_user = await db.execute(select(models.User).where(models.User.email == pereval.user.email))

    if not db_user.scalars().all():
        db_user = models.User(**pereval.user.dict())
    else:
        db_user = await db.execute(select(models.User).where(models.User.email == pereval.user.email))
        db_user = db_user.scalars().one()

    db_list_of_images = []
    for image in pereval.images:
        db_list_of_images.append(models.Image(image_url=str(image.image_url), title=image.title))
    db_level = models.Level(**pereval.level.dict())
    db_pereval = models.Pereval(
        title=pereval.title,
        other_title=pereval.other_title,
        latitude=pereval.coords.latitude,
        longitude=pereval.coords.longitude,
        height=pereval.coords.height,
        user=db_user,
        level=db_level,
        image=db_list_of_images
    )
    db.add(db_pereval)
    await db.commit()
    await db.refresh(db_pereval)
    return db_pereval


async def get_pereval_by_id(db: AsyncSession, pereval_id: int):
    db_pereval = await db.execute(
        select(models.Pereval, models.User, models.Level).join(models.User).join(
            models.Level).filter(models.Pereval.id == pereval_id))
    db_images = await db.execute(select(models.Image).filter(models.Image.pereval_id == pereval_id))

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


async def replace_pereval_by_id(db: AsyncSession, pereval_id, pereval):
    # Если превал имеет статус "new"  (запрос на получение перевала по id)
    db_pereval = await db.execute(select(models.Pereval).filter(models.Pereval.id == pereval_id))
    if db_pereval.scalars().one().status == 'new':
        print('status new')
        # Если отправляются картинки, удаляем все картинки добавленные раннее, и добавляем список новых
        # Работает
        if pereval.image != None:
            lst_image_obj = []
            for image in pereval.image:
                lst_image_obj.append(
                    models.Image(title=image.title, image_url=str(image.image_url), pereval_id=pereval_id))
            stmt = delete(models.Image).where(models.Image.pereval_id == pereval_id)
            await db.execute(stmt)
            db.add_all(lst_image_obj)

        pereval_dict = pereval.dict(exclude_none=True)
        db_pereval = await db.execute(select(models.Pereval).filter(models.Pereval.id == pereval_id))

        # Если отправляется level, обновляем level
        if pereval.level != None:
            stmt = update(models.Level).where(models.Level.id == db_pereval.scalars().one().level_id).values(
                pereval_dict['level'])
            await db.execute(stmt)

        # Обновляем перевал
        pereval_dict.pop('image')
        pereval_dict.pop('level')
        stmt = update(models.Pereval).where(models.Pereval.id == pereval_id).values(pereval_dict)
        await db.execute(stmt)
        await db.commit()
        return {"state": 1, "message": 'Pereval updated successfully!'}
    else:
        raise HTTPException(status_code=404, detail={'state': 0, "message": "Unable to update entry!"})


async def get_perevals_by_email(db: AsyncSession, user_email):
    db_perevals = await db.execute(
        select(models.Pereval).where(models.Pereval.user.has(models.User.email == user_email)))
    return db_perevals.scalars().all()
