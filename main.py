from fastapi import Depends, FastAPI, HTTPException
from mysqlx import DatabaseError
from typing import List
from passlib.context import CryptContext
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from models import User, TodoItem, Base,UserCreate,TodoItemCreate,TodoItemUpdate,TodoItemResponse
from db import db
import jwt
from datetime import datetime, timedelta
from auth import verify_token
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

# Database Setup
db_connection_string = db()
engine = create_engine(db_connection_string)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

security = HTTPBearer()
# Password Hashing
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


# Create Tables
Base.metadata.create_all(bind=engine)

app = FastAPI()

# Helper Functions
def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()




# Create User
@app.post("/users", status_code=201)
def create_user(user: UserCreate):
    db = SessionLocal()
    try:
        hashed_password = get_password_hash(user.password)
        new_user = User(username=user.username, password=hashed_password)
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        return {"id": new_user.id, "username": new_user.username}
    finally:
        db.close()


# Get User by ID
@app.get("/users/{user_id}")
def get_user(user_id: int, db=Depends(get_db)):
    try:
        user = db.query(User).filter(User.id == user_id).first()
        if user is None:
            raise HTTPException(status_code=404, detail="User not found")
        return {"id": user.id, "username": user.username}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")



@app.post("/login")
def login_user(user_credentials: UserCreate, db=Depends(get_db)):
    try:
        user = db.query(User).filter(User.username == user_credentials.username).first()
        if not user:
            raise HTTPException(status_code=404, detail="User not found")

        if not verify_password(user_credentials.password, user.password):
            raise HTTPException(status_code=401, detail="Incorrect password")

        # Generate a JWT token
        access_token_expires = timedelta(minutes=30)
        access_token_data = {
            "sub": user.username,
            "exp": datetime.utcnow() + access_token_expires
        }
        access_token = jwt.encode(access_token_data, "your-secret-key", algorithm="HS256")

        return {"access_token": access_token, "token_type": "bearer"}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")




# CRUD Operations
@app.post("/todos", status_code=201)
def create_todo_item(todo_item: TodoItemCreate, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    try:
        new_todo_item = TodoItem(
            title=todo_item.title,
            description=todo_item.description,
            user_id=todo_item.user_id
        )
        db.add(new_todo_item)
        db.commit()
        db.refresh(new_todo_item)
        return {"id": new_todo_item.id, "title": new_todo_item.title}
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")




# Get Todo Item by ID
@app.get("/todos/{todo_id}")
def get_todo_item(todo_id: int, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    try:
        todo_item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo_item is None:
            raise HTTPException(status_code=404, detail="Todo item not found")
        return {"id": todo_item.id, "title": todo_item.title, "description": todo_item.description}
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")


# Get All Todo Items
@app.get("/todos", response_model=List[TodoItemResponse])  # Use List[TodoItem] as response_model
def get_all_todo_items(db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    try:

        todo_items = db.query(TodoItem).all()
        return [{"id": item.id, "title": item.title, "description": item.description, "user_id": item.user_id} for item in todo_items]
    except DatabaseError as e:
        raise HTTPException(status_code=500, detail="Internal server error")



# Update
@app.put("/todos/update/{todo_id}")
def update_todo_item(todo_id: int, todo_item_update: TodoItemUpdate, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    try:
        todo_item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo_item is None:
            raise HTTPException(status_code=404, detail="Todo item not found")
        todo_item.title = todo_item_update.title
        todo_item.description = todo_item_update.description
        db.commit()
        return {"message": "Todo item updated successfully"}
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")


# Delete
@app.delete("/todos/delete/{todo_id}")
def delete_todo_item(todo_id: int, db=Depends(get_db),credentials: HTTPAuthorizationCredentials = Depends(security)):
    if not verify_token(credentials.credentials):
        raise HTTPException(status_code=401, detail="Invalid authentication token.")
    try:
        todo_item = db.query(TodoItem).filter(TodoItem.id == todo_id).first()
        if todo_item is None:
            raise HTTPException(status_code=404, detail="Todo item not found")
        db.delete(todo_item)
        db.commit()
        return {"message": "Todo item deleted successfully"}
    except DatabaseError as e:
        db.rollback()
        raise HTTPException(status_code=500, detail="Internal server error")