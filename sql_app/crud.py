from sqlalchemy.ext.asyncio import AsyncSession
from sql_app import models
from sql_app.schemas import Pereval


async def create_pereval(db: AsyncSession, pereval: Pereval):
    db_user = models.User(**pereval.user.dict())
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
        status=pereval.status,
        user=db_user,
        level=db_level,
        image=db_list_of_images
    )
    db.add(db_pereval)
    await db.commit()
    await db.refresh(db_pereval)
    return db_pereval
