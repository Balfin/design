from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from producer import OrderProducer
from cassandra_setup import get_cassandra_session
import uvicorn
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Processing API")
producer = OrderProducer()
session = get_cassandra_session()

class OrderCreate(BaseModel):
    customer_name: str = Field(..., example="John Doe")
    item: str = Field(..., example="Product XYZ")
    quantity: int = Field(..., gt=0, example=1)

class Order(OrderCreate):
    order_id: str
    status: str
    created_at: str

@app.post("/orders/", response_model=Order)
async def create_order(order: OrderCreate):
    """Create a new order"""
    try:
        # Send order to Kafka
        order_data = producer.send_order(
            customer_name=order.customer_name,
            item=order.item,
            quantity=order.quantity
        )
        return order_data
    except Exception as e:
        logger.error(f"Failed to create order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get a specific order by ID"""
    try:
        row = session.execute(
            "SELECT * FROM orders WHERE order_id = %s", 
            (order_id,)
        ).one()
        if not row:
            raise HTTPException(status_code=404, detail="Order not found")
        return {
            "order_id": row.order_id,
            "customer_name": row.customer_name,
            "item": row.item,
            "quantity": row.quantity,
            "status": row.status,
            "created_at": row.created_at.isoformat()
        }
    except Exception as e:
        logger.error(f"Error fetching order {order_id}: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to fetch order")

@app.get("/orders/", response_model=List[Order])
async def list_orders(customer_name: Optional[str] = None):
    """List all orders, optionally filtered by customer name"""
    try:
        if customer_name:
            rows = session.execute(
                "SELECT * FROM orders WHERE customer_name = %s ALLOW FILTERING",
                (customer_name,)
            )
        else:
            rows = session.execute("SELECT * FROM orders")

        return [{
            "order_id": row.order_id,
            "customer_name": row.customer_name,
            "item": row.item,
            "quantity": row.quantity,
            "status": row.status,
            "created_at": row.created_at.isoformat()
        } for row in rows]
    except Exception as e:
        logger.error(f"Error listing orders: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to list orders")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown"""
    producer.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
