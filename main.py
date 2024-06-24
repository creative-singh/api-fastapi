from fastapi import FastAPI, HTTPException, Depends
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
  user_name: str = Field(..., max_length=100)
  user_email: EmailStr
  is_active: bool = True

class User(UserBase):
  user_id: int
  class Config:
    orm_mode = True

class ProductBase(BaseModel):
  product_name: str = Field(..., max_length=100)
  product_price: int
  product_description: str = Field(..., max_length=500)
  product_quantity: int
  user_id: int

class Product(ProductBase):
  product_id: int
  class Config: 
    orm_mode = True


def get_db():
  db = SessionLocal()
  try:
    yield db
  finally:
    db.close()

db_dependency = Annotated[Session, Depends(get_db)]

# Health CheckUp
@app.get("/")
def health_check():
  return "The health check is successful!"

# Get All Users
@app.get("/users/")
async def read_users(db: db_dependency):
  return db.query(models.User).all()

# Create a New User
@app.post("/users/")
async def create_user(user: UserBase, db: db_dependency):
  db_user = models.User(
    user_name=user.user_name, 
    user_email=user.user_email, 
    is_active=user.is_active
  )
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return {"message": "User Created", "user": db_user}