from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base

class User(Base):
  __tablename__ = 'users'

  user_id = Column(Integer, primary_key=True, index=True)
  user_name = Column(String, index=True)
  user_email = Column(String, unique=True, index=True)
  is_active = Column(Boolean, index=True)
  products = relationship("Product", back_populates="owner")

class Product(Base):
  __tablename__ = 'products'

  product_id = Column(Integer, primary_key=True, index=True)
  product_name = Column(String, index=True)
  product_price = Column(Integer)
  product_description = Column(String)
  prodcut_quantity = Column(Integer)
  user_id = Column(Integer, ForeignKey('users.user_id'))

  owner = relationship("User", back_populates="products")


