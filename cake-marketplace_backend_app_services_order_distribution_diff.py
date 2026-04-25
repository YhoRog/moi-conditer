--- cake-marketplace/backend/app/services/order_distribution.py (原始)


+++ cake-marketplace/backend/app/services/order_distribution.py (修改后)
from geopy.distance import geodesic
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime, timedelta

from app.models.models import User, Order, OrderStatus

def calculate_distance(lat1: float, lon1: float, lat2: float, lon2: float) -> float:
    """Calculate distance between two points in kilometers"""
    return geodesic((lat1, lon1), (lat2, lon2)).kilometers

def get_nearby_confectioners(db: Session, latitude: float, longitude: float, max_distance: float = 50.0):
    """Get all approved confectioners sorted by distance"""
    confectioners = db.query(User).filter(
        User.role == "confectioner",
        User.is_approved == True,
        User.latitude.isnot(None),
        User.longitude.isnot(None)
    ).all()

    # Calculate distance for each confectioner
    results = []
    for conf in confectioners:
        distance = calculate_distance(latitude, longitude, conf.latitude, conf.longitude)
        if distance <= max_distance:
            results.append({
                "confectioner": conf,
                "distance": distance
            })

    # Sort by distance
    results.sort(key=lambda x: x["distance"])
    return results

def distribute_order_fairly(db: Session, latitude: float, longitude: float):
    """
    Fair order distribution algorithm.

    Methodology:
    1. Find all nearby approved confectioners within max distance
    2. Calculate their current workload (active orders in last 7 days)
    3. Calculate their average rating from reviews
    4. Use weighted scoring:
       - Lower workload = higher priority
       - Higher rating = higher priority
       - Closer distance = higher priority
    5. Select confectioner with highest score

    This ensures:
    - All confectioners get orders over time
    - Quality is rewarded (better ratings)
    - Efficiency is maintained (closer confectioners preferred)
    - No one gets overloaded
    """
    confectioners_data = get_nearby_confectioners(db, latitude, longitude)

    if not confectioners_
        return None

    # Get current date for workload calculation
    week_ago = datetime.utcnow() - timedelta(days=7)

    scored_confectioners = []

    for conf_data in confectioners_
        confectioner = conf_data["confectioner"]
        distance = conf_data["distance"]

        # Calculate workload (orders in last 7 days)
        workload = db.query(Order).filter(
            Order.confectioner_id == confectioner.id,
            Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS, OrderStatus.READY]),
            Order.created_at >= week_ago
        ).count()

        # Calculate average rating
        from app.models.models import Review
        avg_rating_result = db.query(func.avg(Review.rating)).filter(
            Review.confectioner_id == confectioner.id
        ).first()
        avg_rating = avg_rating_result[0] if avg_rating_result[0] else 0

        # Calculate score (higher is better)
        # Normalize factors:
        # - Distance: closer is better (inverse)
        # - Workload: less busy is better (inverse)
        # - Rating: higher is better (direct)

        distance_score = 1 / (distance + 1)  # Add 1 to avoid division by zero
        workload_score = 1 / (workload + 1)
        rating_score = avg_rating / 5.0  # Normalize to 0-1

        # Weighted combination (adjust weights as needed)
        total_score = (
            distance_score * 0.3 +      # 30% weight for distance
            workload_score * 0.4 +      # 40% weight for fair distribution
            rating_score * 0.3          # 30% weight for quality
        )

        scored_confectioners.append({
            "confectioner": confectioner,
            "score": total_score,
            "distance": distance,
            "workload": workload,
            "rating": avg_rating
        })

    # Sort by score (highest first)
    scored_confectioners.sort(key=lambda x: x["score"], reverse=True)

    # Return the best confectioner
    if scored_confectioners:
        return scored_confectioners[0]["confectioner"]

    return None

def get_confectioner_stats(db: Session, confectioner_id: int):
    """Get statistics for a confectioner"""
    week_ago = datetime.utcnow() - timedelta(days=7)

    # Active orders
    active_orders = db.query(Order).filter(
        Order.confectioner_id == confectioner_id,
        Order.status.in_([OrderStatus.PENDING, OrderStatus.CONFIRMED, OrderStatus.IN_PROGRESS, OrderStatus.READY])
    ).count()

    # Completed orders (last 30 days)
    month_ago = datetime.utcnow() - timedelta(days=30)
    completed_orders = db.query(Order).filter(
        Order.confectioner_id == confectioner_id,
        Order.status == OrderStatus.COMPLETED,
        Order.created_at >= month_ago
    ).count()

    # Average rating
    from app.models.models import Review
    avg_rating = db.query(func.avg(Review.rating)).filter(
        Review.confectioner_id == confectioner_id
    ).scalar() or 0

    # Total reviews
    total_reviews = db.query(Review).filter(
        Review.confectioner_id == confectioner_id
    ).count()

    return {
        "active_orders": active_orders,
        "completed_orders": completed_orders,
        "average_rating": round(avg_rating, 2),
        "total_reviews": total_reviews
    }