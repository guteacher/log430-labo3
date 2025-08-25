import graphene
from graphene import ObjectType, String, Int
from schemas.product import Product
from db import get_redis_conn

class Query(ObjectType):       
    product = graphene.Field(Product, id=String(required=True))
    stock_level = Int(product_id=String(required=True))
    
    def resolve_product(self, info, id):
        redis_client = get_redis_conn()
        product_data = redis_client.hgetall(f"product_stock:{id}")
        if product_data:
            return Product(
                id=id,
                name=f"Product {id}",
                quantity=int(product_data['quantity'])
            )
        return None
    
    def resolve_stock_level(self, info, product_id):
        redis_client = get_redis_conn()
        quantity = redis_client.hget(f"product_stock:{product_id}", "quantity")
        return int(quantity) if quantity else 0