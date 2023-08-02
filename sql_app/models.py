from datetime import datetime
from sqlalchemy import Column, ForeignKey, Integer, String, Float, TIMESTAMP
from sqlalchemy.orm import relationship
from sql_app.database import Base


class User(Base):
    __tablename__ = 'user'
    id = Column(Integer, primary_key=True)
    name = Column(String(32), nullable=False)
    fam = Column(String(32), nullable=False)
    otc = Column(String(32), nullable=False)
    email = Column(String(32), nullable=False, unique=True)
    phone = Column(String(32), nullable=False, unique=True)

    pereval = relationship('Pereval', back_populates='user')


class Pereval(Base):
    __tablename__ = 'pereval'
    id = Column(Integer, primary_key=True)
    title = Column(String(32), nullable=False)
    other_title = Column(String(32), nullable=True)
    add_time = Column(TIMESTAMP, default=datetime.utcnow)
    latitude = Column(Float, nullable=False)
    longitude = Column(Float, nullable=False)
    height = Column(Integer, nullable=False)
    status = Column(String(32), default='new')
    user_id = Column(ForeignKey('user.id'))
    level_id = Column(ForeignKey('level.id'))

    user = relationship('User', back_populates='pereval')
    level = relationship('Level', back_populates='pereval', uselist=False)
    image = relationship('Image', back_populates='pereval')


class Image(Base):
    __tablename__ = 'image'
    id = Column(Integer, primary_key=True)
    image_url = Column(String())
    title = Column(String(32), nullable=True)
    pereval_id = Column(ForeignKey('pereval.id'))

    pereval = relationship('Pereval', back_populates='image')


class Level(Base):
    __tablename__ = 'level'
    id = Column(Integer, primary_key=True)
    winter = Column(String(2))
    summer = Column(String(2))
    autumn = Column(String(2))
    spring = Column(String(2))

    pereval = relationship('Pereval', back_populates='level', uselist=False)
