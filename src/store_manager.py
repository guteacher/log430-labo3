"""
Order manager application
SPDX - License - Identifier: LGPL - 3.0 - or -later
Auteurs : Gabriel C. Ullmann, Fabio Petrillo, 2025
"""
from graphene import Schema
from schemas.query import Query
from flask import Flask, request, jsonify
from controllers.order_controller import create_order, remove_order, get_report_highest_spending_users, get_report_best_selling_products
from controllers.product_controller import create_product
from controllers.user_controller import create_user
from controllers.product_stock_controller import get_stock, set_product_stock, get_stock_overview
 
app = Flask(__name__)
schema = Schema(query=Query)

@app.get('/health')
def health():
    """Return OK if app is up and running"""
    return jsonify({'status':'ok'})

# Write routes (Commands)
@app.post('/orders')
def post_orders():
    """Create a new order based on information on request body"""
    return create_order(request)

@app.post('/products')
def products():
    """Create a new product based on information on request body"""
    return create_product(request)

@app.post('/product_stocks')
def product_stocks():
    """Set product stock based on information on request body"""
    return set_product_stock(request)

@app.post('/users')
def users():
    """Create a new user based on information on request body"""
    return create_user(request)

@app.delete('/orders/<int:order_id>')
def delete_orders_id(order_id):
    """Delete an order with a given order_id"""
    return remove_order(order_id)

# Read routes (Queries) 
@app.get('/orders/<int:order_id>')
def get_order(order_id):
    """Get order with a given order_id"""
    return get_order(order_id)

@app.post('/product_stocks/<int:product_id>')
def get_product_stocks(product_id):
    """Get product stocks by product_id"""
    return get_stock(product_id)

@app.get('/orders/reports/highest_spenders')
def get_orders_highest_spending_users():
    """Get list of highest speding users, order by total expenditure"""
    rows = get_report_highest_spending_users()
    return jsonify(rows)

@app.get('/orders/reports/best_sellers')
def get_orders_report_best_selling_products():
    """Get list of best selling products, order by number of orders"""
    rows = get_report_best_selling_products()
    return jsonify(rows)

@app.get('/product_stocks/reports/overview')
def get_product_stocks_overview():
    """Get stocks for all products"""
    rows = get_stock_overview()
    return jsonify(rows)

# Vendor-managed inventory (VMI) route
@app.route('/product_stocks/graphql', methods=['POST'])
def graphql_supplier():
    data = request.get_json()
    result = schema.execute(data['query'], variables=data.get('variables'))
    
    return jsonify({
        'data': result.data,
        'errors': [str(e) for e in result.errors] if result.errors else None
    })

# Start Flask app
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
