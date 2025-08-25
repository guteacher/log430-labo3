"""
Product stocks (write-only model)
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from sqlalchemy import text
from models.product_stock import ProductStock
from db import get_redis_conn, get_sqlalchemy_session

def set_stock_for_product(product_id, quantity):
    """Set stock quantity for product in MySQL"""
    session = get_sqlalchemy_session()
    try: 
        result = session.execute(
            text(f"""
                UPDATE product_stocks 
                SET quantity = :qty 
                WHERE product_id = :pid
            """),
            {"pid": product_id, "qty": quantity}
        )
        response_message = f"rows updated: {result.rowcount}"
        if result.rowcount == 0:
            new_product_stock = ProductStock(product_id=product_id, quantity=quantity)
            session.add(new_product_stock)
            session.flush() 
            session.commit()
            response_message = f"rows added: {new_product_stock.product_id}"
  
        r = get_redis_conn()
        r.hset(f"product_stock:{product_id}", "quantity", quantity)
        return response_message
    except Exception as e:
        session.rollback()
        raise e
    finally:
        session.close()
    
def update_stock_mysql(session, order_items, operation):
    """ Update stock quantities in MySQL according to a given operation (+/-) """
    try:
        for item in order_items:
            if hasattr(order_items[0], 'product_id'):
                pid = item.product_id
                qty = item.quantity
            else:
                pid = item['product_id']
                qty = item['quantity']
            session.execute(
                text(f"""
                    UPDATE product_stocks 
                    SET quantity = quantity {operation} :qty 
                    WHERE product_id = :pid
                """),
                {"pid": pid, "qty": qty}
            )
    except Exception as e:
        raise e
    
def check_out_items_from_stock(session, order_items):
    """ Decrease stock quantities in Redis """
    update_stock_mysql(session, order_items, "-")
    
def check_in_items_to_stock(session, order_items):
    """ Increase stock quantities in Redis """
    update_stock_mysql(session, order_items, "+")

def update_stock_redis(order_items, operation):
    """ Update stock quantities in Redis """
    if not order_items:
        return
    r = get_redis_conn()
    product_stock_keys = list(r.scan_iter("product_stock:*"))
    if product_stock_keys:
        pipeline = r.pipeline()
        for item in order_items:
            print(item)
            if hasattr(item, 'product_id'):
                product_id = item.product_id
                quantity = item.quantity
            else:
                product_id = item['product_id']
                quantity = item['quantity']
            
            current_stock = r.hget(f"product_stock:{product_id}", "quantity")
            current_stock = int(current_stock) if current_stock else 0
            
            if operation == '+':
                new_quantity = current_stock + quantity
            else:  
                new_quantity = current_stock - quantity
            
            pipeline.hset(f"product_stock:{product_id}", "quantity", new_quantity)
        
        pipeline.execute()
    
    else:
        _populate_redis_from_mysql(r)
        update_stock_redis(order_items, operation)

def _populate_redis_from_mysql(redis_conn):
    """ Helper function to populate Redis from MySQL product_stocks table """
    session = get_sqlalchemy_session()
    try:
        stocks = session.execute(
            text("SELECT product_id, quantity FROM product_stocks")
        ).fetchall()
        
        pipeline = redis_conn.pipeline()
        
        for product_id, quantity in stocks:
            pipeline.hset(
                f"product_stock:{product_id}", 
                mapping={ "quantity": quantity }
            )
        
        pipeline.execute()
        print(f"Populated Redis with {len(stocks)} stock records")
        
    except Exception as e:
        print(f"Error populating Redis from MySQL: {e}")
        raise e
    finally:
        session.close()