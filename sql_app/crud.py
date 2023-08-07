from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
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
            'latitude': pereval.latitude,
            'longitude': pereval.longitude,
            'height': pereval.height,
            'user': user,
            'level': level,
            'images': db_images.scalars().all()

        }
