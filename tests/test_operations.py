from httpx import AsyncClient
from src.operations.models import Pereval, Level, User, Image
from conftest import async_session_maker


# @pytest.fixture()
# async def add_perevals():
#     async with async_session_maker() as session:
#         level_1 = Level(
#             summer='1a',
#             spring='2a',
#             winter='3e',
#             autumn='4r'
#         )
#
#         user_1 = User(
#             name='Dmitry',
#             fam='Biryukov',
#             otc='Sergeevich',
#             email='dim.bir2017@yandex.ru',
#             phone='+79008007070'
#         )
#
#         image_1 = Image(
#             title='image_1',
#             image_url='adresssss'
#         )
#
#         pereval_1 = Pereval(
#             title='Киллар',
#             other_title='Пиллар',
#             latitude=25.25,
#             longitude=26.26,
#             height=2350,
#             user=user_1,
#             level=level_1,
#             image=[image_1]
#         )
#         session.add(pereval_1)
#         await session.commit()




async def test_add_pereval(ac: AsyncClient):
    response = await ac.post("/perevals/", json=
    {
        "title": "Киллар",
        "other_title": "string",
        "user": {
            "name": "string",
            "fam": "string",
            "otc": "string",
            "email": "user@example.com",
            "phone": "+79055202585"
        },
        "coords": {
            "latitude": 0,
            "longitude": 0,
            "height": 0
        },
        "level": {
            "summer": "st",
            "spring": "st",
            "winter": "st",
            "autumn": "st"
        },
        "images": [
            {
                "title": "string",
                "image_url": "https://example.com/"
            }
        ]
    }
                             )

    assert response.status_code == 200
    assert response.json()['status'] == 200
    assert response.json()['message'] == 'Pereval created successfully!'


async def test_get_pereval_by_id(ac: AsyncClient):
    response = await ac.get("/perevals/1")
    assert response.status_code == 200


async def test_get_pereval_by_email(ac: AsyncClient):
    response = await ac.get("/perevals/", params={
        'user_email': 'user@example.com'
    })

    assert response.status_code == 200


async def test_patch_pereval_by_id(ac: AsyncClient):
    response = await ac.patch("/perevals/1", json=
    {
        "title": "aaaaaaaaaaaaaaaaaaaaaaa",
        "other_title": "string",
        "latitude": 0,
        "longitude": 0,
        "height": 0,
        "level": {
            "summer": "st",
            "spring": "st",
            "winter": "st",
            "autumn": "st"
        },
        "image": [
            {
                "title": "string",
                "image_url": "https://example.com/"
            }
        ]
    }
                              )
    assert response.status_code == 200
    assert response.json() == {"state": 1, "message": 'Pereval updated successfully!'}


