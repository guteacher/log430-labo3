"""
Orders (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_redis_conn
from collections import defaultdict

def get_order_by_id(order_id):
    """Get order by ID from Redis"""
    r = get_redis_conn()
    return r.hgetall(order_id)

def get_highest_spending_users():
    """Get report of highest spending users"""
    r = get_redis_conn()
    limit = 10
    result = []
    order_keys = r.keys("order:*")
    spending = defaultdict(float)
    
    for key in order_keys:
        order_data = r.hgetall(key)
        if "user_id" in order_data and "total_amount" in order_data:
            user_id = int(order_data["user_id"])
            total = float(order_data["total_amount"])
            spending[user_id] += total

    # trier par total dépensé (décroissant), limite X
    highest_spending_users = sorted(spending.items(), key=lambda x: x[1], reverse=True)[:limit]
    for user in highest_spending_users:
        result.append({
            "user_id": user[0],
            "total_expense": round(user[1], 2)
        })

    return result

def get_best_selling_products():
    """Get report of best selling products"""
    return []