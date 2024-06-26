from fastapi import FastAPI, HTTPException, Depends, Request
from pydantic import BaseModel, EmailStr, Field
from typing import Annotated
import models
from database import SessionLocal, engine
from sqlalchemy.orm import Session
from sqlalchemy import inspect
from uuid import UUID
from sqlalchemy.exc import NoResultFound
from typing import Any, Dict, Union

app = FastAPI()
models.Base.metadata.create_all(bind=engine)

class UserBase(BaseModel):
  name: str = Field(..., max_length=100)
  email: EmailStr
  is_active: bool = True

class User(UserBase):
  _id: UUID
  class Config:
    orm_mode = True

class ProductBase(BaseModel):
  name: str = Field(..., max_length=100)
  price: int
  description: str = Field(..., max_length=500)
  quantity: int
  user_id: UUID

class Product(ProductBase):
  product_id: UUID
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

# Get All the Tables from Schema
@app.get("/taxonomy/entities") 
async def list_tables():
  inspector = inspect(engine)
  tables = inspector.get_table_names(schema="public")
  return {"tables": tables}

# Get All the Tables with Fields from Schema
@app.get("/taxonomy/entities/fields")  
async def list_tables_fields():
  inspector = inspect(engine)
  tables = inspector.get_table_names(schema="public")
  
  tables_with_fields = {}
  for table in tables:
    columns = inspector.get_columns(table, schema="public")
    tables_with_fields[table] = [column["name"] for column in columns]
  
  return {"tables": tables_with_fields}

# Get All Users
@app.get("/users/")
async def read_users(db: db_dependency):
  return db.query(models.User).all()

# Create a New User
@app.post("/users/")
async def create_user(user: UserBase, db: db_dependency):
  db_user = models.User(
    name = user.name, 
    email = user.email, 
    is_active = user.is_active
  )
  db.add(db_user)
  db.commit()
  db.refresh(db_user)
  return {"message": "User Created Successfully.", "user": db_user}

# Get a user by ID
@app.get("/users/{id}")
async def read_userById(id: UUID, db: db_dependency):
  user = db.query(models.User).filter(models.User._id == id).first()
  if not user:
      raise HTTPException(status_code=404, detail="User not found")
  return user

# Create a New Product
@app.post("/products/")
async def create_product(product: ProductBase, db: db_dependency):
  db_product = models.Product(
    name = product.name, 
    price = product.price, 
    description = product.description, 
    quantity = product.quantity, 
    user_id = product.user_id
  )
  db.add(db_product)
  db.commit()
  db.refresh(db_product)
  return {"message": "Product Created", "product": db_product}

# Get All Products
@app.get("/products/")
async def read_products(db: db_dependency):
  return db.query(models.Product).all()

# Get a Product by ID
@app.get("/products/{id}")
async def read_productById(id: UUID, db: db_dependency):
  product = db.query(models.Product).filter(models.Product._id == id).first()
  if not product:
      raise HTTPException(status_code=404, detail="Product not found.")
  return product

# Update a User by ID
@app.put("/taxonomy/entities/{entity_name}/{id}")
async def update_user_by_id(id: UUID, entity_name: str, payload: Union[UserBase, ProductBase], db: db_dependency):
  if(entity_name == "user"):
    db_obj = db.query(models.User).filter(models.User._id == id).first()
    # Checking if user has any associated products
    associated_products = db.query(models.Product).filter(models.Product.user_id == id).all()
    if associated_products:
      raise HTTPException(status_code=400, detail="This user has associated products. Delete the products first.")
  else:
    db_obj = db.query(models.Product).filter(models.Product._id == id).first()

  if not db_obj:
    raise HTTPException(status_code=404, detail=f"{entity_name} not found")
  
  for key, value in payload:
    setattr(db_obj, key, value)

  db.commit()
  db.refresh(db_obj)
  return {"message": f"{entity_name} Updated Successfully.", "entity": db_obj}

# Delete a record by Table Name and Entity ID
@app.delete("/taxonomy/entities/{entity_name}/{id}")
async def delete_entity_by_id(id: UUID, entity_name: str, db: db_dependency):
  if(entity_name == "user"):
    db_object = db.query(models.User).filter(models.User._id == id).first()
    # Checking if user has any associated products
    associated_products = db.query(models.Product).filter(models.Product.user_id == id).all()
    if associated_products:
      raise HTTPException(status_code=400, detail="This user has associated products. Delete the products first.")
  else:
    db_object = db.query(models.Product).filter(models.Product._id == id).first()
  
  if not db_object:
    raise HTTPException(status_code=404, detail=f"{entity_name} not found")
    
  db.delete(db_object)
  db.commit()
  return {"message": f"{entity_name} Deleted Successfully."}

# Helper function to update an instance
# def update_instance(db: Session, model, instance_id: UUID, update_data: Dict[str, Any]):
#     print("db is here :: ", db)
#     print("model is here :: ", model)
#     print("instance_id is here :: ", instance_id)
#     print("update_data is here :: ", update_data)

#     instance = db.query(model).filter(model._id == instance_id).first() 

#     if not instance:
#         raise HTTPException(status_code=404, detail=f"{model.__name__} not found")
    
#     print("I REACHED HERE ...... ")
    
#     for key, value in update_data.items():
#         setattr(instance, key, value)
    
#     db.commit()
#     db.refresh(instance)
#     return instance

# @app.put("/update/{entity_name}/{instance_id}")
# async def update_any_table(
#     entity_name: str, 
#     instance_id: UUID, 
#     request: Union[UserBase, ProductBase],  
#     db: db_dependency
#   ):

#   print("I M AT 169")
  
#   ENTITY_MAP = list_tables()
#   if entity_name not in ENTITY_MAP["tables"]:
#     raise HTTPException(status_code=400, detail="Invalid ENTITY name")
  
#   print("I M AT 175", ENTITY_MAP)

#   if entity_name == "user":
#     model = model.User
#   else:
#     model = model.Product

#   update_data = request.dict(exclude_unset=True)

#   print(" UPDATE DATA :: ", update_data)
#   print("DB :: ", db)
#   print("MODEL ::: ", model)
#   print("INSTANCE ID :: ", instance_id)
#   print("REQUEST :: ", update_data)
  
  
#   try:
#     updated_instance = update_instance(db, model, instance_id, update_data)
#     return updated_instance
#   except NoResultFound:
#     raise HTTPException(status_code=404, detail=f"{entity_name.capitalize()} with id {instance_id} not found")

# Delete a record by Table Name and Entity ID
# @app.delete("/taxonomy/entities/{entity_name}/{id}")
# async def update_entityById(id: UUID, entity_name:str, db: db_dependency):
#   if(entity_name == "user"):
#     db_object = read_userById(id, db)
#     key = 'user'
    
#   else:
#     db_object = read_productById(id, db)
#     key = 'product'

#   db.delete(db_object)
#   db.commit()
#   return {"message": f"{key} Deleted Successfully."}