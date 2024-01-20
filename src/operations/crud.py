from fastapi import HTTPException
from sqlalchemy import select, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from operations.models import User, Image, Level, Pereval
from operations.schemas import Pereval as Pereval_Schema


async def create_pereval(db: AsyncSession, pereval: Pereval_Schema):
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
    return pereval


async def get_pereval_by_id(db: AsyncSession, pereval_id: int):
    db_pereval = await db.execute(
        select(Pereval, User, Level).join(User).join(
            Level).filter(Pereval.id == pereval_id))
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


async def replace_pereval_by_id(db: AsyncSession, pereval_id, pereval):
    result = await db.execute(select(Pereval).filter(Pereval.id == pereval_id))
    db_pereval = result.scalars().first()

    if db_pereval is None:
        return None
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
        db_pereval = await db.execute(select(Pereval).filter(Pereval.id == pereval_id))

        # Если отправляется level, обновляем level
        if pereval.level != None:
            stmt = update(Level).where(Level.id == db_pereval.scalars().one().level_id).values(
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


async def get_perevals_by_email(db: AsyncSession, user_email):
    result = await db.execute(
        select(Pereval).where(Pereval.user.has(User.email == user_email)))
    db_perevals = result.scalars().all()
    if not db_perevals:
        return None
    return db_perevals
