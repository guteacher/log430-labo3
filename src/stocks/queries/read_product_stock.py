"""
Product (read-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""

from db import get_sqlalchemy_session
from stocks.models.product import Product
from stocks.models.product_stock import ProductStock

def get_product_stock_by_id(product_id):
    """Get stock by product ID """
    session = get_sqlalchemy_session()
    return session.query(ProductStock).filter_by(product_id=product_id).all()

def get_stock_for_all_products():
    """Get stock quantity for all products"""
    session = get_sqlalchemy_session()
    results = session.query(
        ProductStock.product_id,
        ProductStock.quantity,
        Product.sku,
        Product.name,
        Product.price
    ).join(
        Product, ProductStock.product_id == Product.id
    ).all()
    stock_data = []
    for row in results:
        stock_data.append({
            'Article': row.name,
            'Numéro SKU': row.sku,
            'Prix unitaire': float(row.price),
            'Unités en stock': int(row.quantity),
        })
    
    return stock_data
