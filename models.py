from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = 'User'
    id = Column(Integer, primary_key=True)
    username = Column(String, unique=True)
    password = Column(String)
    is_active = Column(Boolean, default=True)
    token = relationship('Token', back_populates='user')


class Token(Base):
    __tablename__ = 'Token'
    id = Column(Integer, primary_key=True)
    token = Column(String)
    user_id = Column(Integer, ForeignKey('User'))
    user = relationship('User', back_populates='token')
