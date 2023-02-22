from db import Base
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

class Users(Base):
     __tablename__ = 'Users'

     id = Column(Integer, primary_key=True, index=True)
     email = Column(String, unique=True, index=True)
     first_name = Column(String)
     last_name = Column(String)
     username = Column(String, unique=True, index=True)
     hashed_password = Column(String)
     is_active = Column(Boolean, default=True)

     todos = relationship("ToDo", back_populates="owner")


class ToDo(Base):
    __tablename__ = 'todos'
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    description = Column(String)
    priority = Column(Integer)
    complete = Column(Boolean, default=False)

    owner_id = Column(Integer, ForeignKey('users.id'))
    owner = relationship("Users", back_populates="todos")