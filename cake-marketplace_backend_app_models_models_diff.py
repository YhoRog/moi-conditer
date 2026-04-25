--- cake-marketplace/backend/app/models/models.py (原始)


+++ cake-marketplace/backend/app/models/models.py (修改后)
from sqlalchemy import Column, Integer, String, Float, Boolean, DateTime, ForeignKey, Text, Enum
from sqlalchemy.orm import relationship
from datetime import datetime
import enum

from app.db.database import Base

class UserRole(str, enum.Enum):
    CUSTOMER = "customer"
    CONFECTIONER = "confectioner"
    ADMIN = "admin"

class OrderStatus(str, enum.Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    IN_PROGRESS = "in_progress"
    READY = "ready"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    email = Column(String, unique=True, index=True, nullable=False)
    hashed_password = Column(String, nullable=False)
    full_name = Column(String, nullable=False)
    phone = Column(String, nullable=False)
    role = Column(String, default=UserRole.CUSTOMER)
    is_approved = Column(Boolean, default=False)  # Для кондитеров - подтверждение оператором
    latitude = Column(Float, nullable=True)  # Широта для геолокации
    longitude = Column(Float, nullable=True)  # Долгота для геолокации
    address = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    # Связи
    products = relationship("Product", back_populates="confectioner")
    orders = relationship("Order", back_populates="customer")
    confectioner_orders = relationship("Order", back_populates="confectioner")
    reviews = relationship("Review", back_populates="author")

class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=True)
    price = Column(Float, nullable=False)
    category = Column(String, nullable=False)  # торты, пирожные, капкейки и т.д.
    image_url = Column(String, nullable=True)
    is_available = Column(Boolean, default=True)
    confectioner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    confectioner = relationship("User", back_populates="products")
    order_items = relationship("OrderItem", back_populates="product")

class Order(Base):
    __tablename__ = "orders"

    id = Column(Integer, primary_key=True, index=True)
    customer_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confectioner_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    status = Column(String, default=OrderStatus.PENDING)
    total_price = Column(Float, nullable=False)
    delivery_address = Column(String, nullable=False)
    delivery_latitude = Column(Float, nullable=True)
    delivery_longitude = Column(Float, nullable=True)
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    customer = relationship("User", foreign_keys=[customer_id], back_populates="orders")
    confectioner = relationship("User", foreign_keys=[confectioner_id], back_populates="confectioner_orders")
    items = relationship("OrderItem", back_populates="order")
    review = relationship("Review", back_populates="order", uselist=False)

class OrderItem(Base):
    __tablename__ = "order_items"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), nullable=False)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False)
    quantity = Column(Integer, nullable=False, default=1)
    price = Column(Float, nullable=False)

    order = relationship("Order", back_populates="items")
    product = relationship("Product", back_populates="order_items")

class Review(Base):
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    order_id = Column(Integer, ForeignKey("orders.id"), unique=True, nullable=False)
    author_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    confectioner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    rating = Column(Integer, nullable=False)  # 1-5
    comment = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    order = relationship("Order", back_populates="review")
    author = relationship("User", foreign_keys=[author_id], back_populates="reviews")