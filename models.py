from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
from pydantic import BaseModel

Base = declarative_base()


class User(Base):
    __tablename__ = "users"
    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(50), unique=True, index=True)
    password = Column(String(255))


class TodoItem(Base):
    __tablename__ = "todo_items"
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(255), index=True)
    description = Column(String(255))
    created_at = Column(DateTime, default=datetime.now)
    user_id = Column(Integer)



class UserCreate(BaseModel):
    username: str
    password: str


class TodoItemCreate(BaseModel):
    title: str
    description: str
    user_id: int

class TodoItemUpdate(BaseModel):
    title: str
    description: str

class TodoItemResponse(BaseModel):
    id: int
    title: str
    description: str
    user_id : int