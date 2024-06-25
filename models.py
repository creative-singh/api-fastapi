import uuid
from sqlalchemy import Boolean, Column, Integer, String, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from sqlalchemy.dialects.postgresql import UUID

class User(Base):
  __tablename__ = 'users'

  _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, index=True)
  email = Column(String, unique=True, index=True)
  is_active = Column(Boolean, index=True)
  products = relationship("Product", back_populates="owner")

class Product(Base):
  __tablename__ = 'products'

  _id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
  name = Column(String, index=True)
  price = Column(Integer)
  description = Column(String)
  quantity = Column(Integer)
  user_id = Column(UUID(as_uuid=True), ForeignKey('users._id'))

  owner = relationship("User", back_populates="products")


