--- cake-marketplace/backend/app/api/routes.py (原始)


+++ cake-marketplace/backend/app/api/routes.py (修改后)
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.db.database import get_db
from app.models.models import User, Product, Order, OrderItem, OrderStatus, Review
from app.schemas.schemas import (
    UserCreate, UserResponse, UserLogin,
    ProductCreate, ProductResponse,
    OrderCreate, OrderResponse,
    ReviewCreate, ReviewResponse
)
from app.core.security import get_password_hash, verify_password
from app.core.auth import create_access_token, verify_token
from app.services.order_distribution import distribute_order_fairly, get_confectioner_stats

router = APIRouter()

# Dependency to get current user
def get_current_user(token: str, db: Session = Depends(get_db)):
    payload = verify_token(token)
    if not payload:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = db.query(User).filter(User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")
    return user

# Auth endpoints
@router.post("/register", response_model=UserResponse)
def register(user_ UserCreate, db: Session = Depends(get_db)):
    # Check if user exists
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Create user
    hashed_password = get_password_hash(user_data.password)
    db_user = User(
        email=user_data.email,
        hashed_password=hashed_password,
        full_name=user_data.full_name,
        phone=user_data.phone,
        role=user_data.role,
        address=user_data.address,
        latitude=user_data.latitude,
        longitude=user_data.longitude,
        is_approved=(user_data.role != "confectioner")  # Auto-approve non-confectioners
    )

    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

@router.post("/login")
def login(login_ UserLogin, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == login_data.email).first()
    if not user or not verify_password(login_data.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    if user.role == "confectioner" and not user.is_approved:
        raise HTTPException(status_code=403, detail="Account pending approval by admin")

    access_token = create_access_token(data={"sub": user.id})
    return {"access_token": access_token, "token_type": "bearer", "user": UserResponse.model_validate(user)}

# Product endpoints
@router.get("/products", response_model=List[ProductResponse])
def get_products(latitude: float = None, longitude: float = None, db: Session = Depends(get_db)):
    """Get all available products, optionally sorted by distance"""
    products = db.query(Product).filter(Product.is_available == True).all()

    if latitude and longitude:
        from app.services.order_distribution import calculate_distance
        # Add confectioner info and sort by distance
        product_list = []
        for product in products:
            confectioner = db.query(User).filter(User.id == product.confectioner_id).first()
            if confectioner and confectioner.latitude and confectioner.longitude:
                distance = calculate_distance(latitude, longitude, confectioner.latitude, confectioner.longitude)
                product_list.append({
                    "product": product,
                    "distance": distance,
                    "confectioner_name": confectioner.full_name
                })

        product_list.sort(key=lambda x: x["distance"])
        result = []
        for item in product_list:
            prod_dict = ProductResponse.model_validate(item["product"])
            prod_dict.confectioner_name = item["confectioner_name"]
            result.append(prod_dict)
        return result

    return [ProductResponse.model_validate(p) for p in products]

@router.post("/products", response_model=ProductResponse)
def create_product(
    product_ ProductCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "confectioner":
        raise HTTPException(status_code=403, detail="Only confectioners can create products")

    if not current_user.is_approved:
        raise HTTPException(status_code=403, detail="Account not approved yet")

    db_product = Product(**product_data.model_dump(), confectioner_id=current_user.id)
    db.add(db_product)
    db.commit()
    db.refresh(db_product)
    return ProductResponse.model_validate(db_product)

# Order endpoints
@router.post("/orders", response_model=OrderResponse)
def create_order(
    order_ OrderCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Calculate total price
    total_price = 0
    items_data = []

    for item in order_data.items:
        product = db.query(Product).filter(Product.id == item.product_id).first()
        if not product or not product.is_available:
            raise HTTPException(status_code=400, detail=f"Product {item.product_id} not available")

        item_total = product.price * item.quantity
        total_price += item_total
        items_data.append({
            "product_id": item.product_id,
            "quantity": item.quantity,
            "price": product.price
        })

    # Find best confectioner using fair distribution algorithm
    confectioner = None
    if order_data.delivery_latitude and order_data.delivery_longitude:
        confectioner = distribute_order_fairly(
            db,
            order_data.delivery_latitude,
            order_data.delivery_longitude
        )

    if not confectioner:
        raise HTTPException(status_code=400, detail="No available confectioners in your area")

    # Create order
    db_order = Order(
        customer_id=current_user.id,
        confectioner_id=confectioner.id,
        total_price=total_price,
        delivery_address=order_data.delivery_address,
        delivery_latitude=order_data.delivery_latitude,
        delivery_longitude=order_data.delivery_longitude,
        comment=order_data.comment
    )

    db.add(db_order)
    db.commit()
    db.refresh(db_order)

    # Create order items
    for item_data in items_
        db_item = OrderItem(
            order_id=db_order.id,
            **item_data
        )
        db.add(db_item)

    db.commit()
    db.refresh(db_order)

    return OrderResponse.model_validate(db_order)

@router.get("/orders", response_model=List[OrderResponse])
def get_orders(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    """Get orders for current user (as customer or confectioner)"""
    if current_user.role == "confectioner":
        orders = db.query(Order).filter(Order.confectioner_id == current_user.id).all()
    else:
        orders = db.query(Order).filter(Order.customer_id == current_user.id).all()

    return [OrderResponse.model_validate(o) for o in orders]

@router.put("/orders/{order_id}/status")
def update_order_status(
    order_id: int,
    status: str,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "confectioner":
        raise HTTPException(status_code=403, detail="Only confectioners can update order status")

    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.confectioner_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to update this order")

    order.status = status
    db.commit()

    return {"message": "Status updated", "order": OrderResponse.model_validate(order)}

# Admin endpoints
@router.get("/admin/confectioners")
def get_pending_confectioners(current_user: User = Depends(get_current_user), db: Session = Depends(get_db)):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    confectioners = db.query(User).filter(
        User.role == "confectioner",
        User.is_approved == False
    ).all()

    return [UserResponse.model_validate(c) for c in confectioners]

@router.put("/admin/confectioners/{confectioner_id}/approve")
def approve_confectioner(
    confectioner_id: int,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")

    confectioner = db.query(User).filter(User.id == confectioner_id).first()
    if not confectioner:
        raise HTTPException(status_code=404, detail="User not found")

    confectioner.is_approved = True
    db.commit()

    return {"message": "Confectioner approved"}

# Review endpoints
@router.post("/orders/{order_id}/review", response_model=ReviewResponse)
def create_review(
    order_id: int,
    review_ ReviewCreate,
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    # Check if order exists and belongs to user
    order = db.query(Order).filter(Order.id == order_id).first()
    if not order:
        raise HTTPException(status_code=404, detail="Order not found")

    if order.customer_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not authorized to review this order")

    if order.status != OrderStatus.COMPLETED:
        raise HTTPException(status_code=400, detail="Can only review completed orders")

    # Check if review already exists
    existing_review = db.query(Review).filter(Review.order_id == order_id).first()
    if existing_review:
        raise HTTPException(status_code=400, detail="Review already exists for this order")

    db_review = Review(
        order_id=order_id,
        author_id=current_user.id,
        confectioner_id=order.confectioner_id,
        rating=review_data.rating,
        comment=review_data.comment
    )

    db.add(db_review)
    db.commit()
    db.refresh(db_review)

    return ReviewResponse.model_validate(db_review)

@router.get("/confectioners/{confectioner_id}/stats")
def get_confectioner_statistics(
    confectioner_id: int,
    db: Session = Depends(get_db)
):
    stats = get_confectioner_stats(db, confectioner_id)
    return stats