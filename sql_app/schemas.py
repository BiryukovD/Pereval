from datetime import datetime
from typing import List, Optional
from pydantic_extra_types.phone_numbers import PhoneNumber
from pydantic import BaseModel, EmailStr, Field, AnyHttpUrl


class User(BaseModel):
    name: str
    fam: str
    otc: str
    email: EmailStr
    phone: PhoneNumber


class Coords(BaseModel):
    latitude: float
    longitude: float
    height: int


class Level(BaseModel):
    summer: Optional[str] = Field(max_length=2)
    spring: Optional[str] = Field(max_length=2)
    winter: Optional[str] = Field(max_length=2)
    autumn: Optional[str] = Field(max_length=2)


class Image(BaseModel):
    title: Optional[str] = Field(max_length=32)
    image_url: AnyHttpUrl


class Pereval(BaseModel):
    title: str = Field(max_length=32)
    other_title: Optional[str] = Field(max_length=32)
    user: User
    coords: Coords
    level: Level
    images: List[Image]


class PerevalOut(BaseModel):
    title: str
    other_title: Optional[str]
    status: str
    add_time: datetime
    latitude: float
    longitude: float
    height: int
    level: Level
    user: User
    images: List[Image]

class PerevalReplace(BaseModel):
    title: Optional[str] = None
    other_title: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    height: Optional[int] = None
    level: Optional[Level] = None
    image: Optional[List[Image]] = None



