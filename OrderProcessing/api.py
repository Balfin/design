from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime
from producer import OrderProducer
from cassandra_setup import get_cassandra_session
from redis_service import RedisHotKeySimulator
import uvicorn
import logging
import redis
import json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(title="Order Processing API")

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # React app origin
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

producer = OrderProducer()
session = get_cassandra_session()
redis_client = redis.Redis(host='localhost', port=6379, db=0)
redis_simulator = None

class OrderCreate(BaseModel):
    customer_name: str = Field(..., example="John Doe")
    item: str = Field(..., example="Product XYZ")
    quantity: int = Field(..., gt=0, example=1)

class Order(OrderCreate):
    order_id: str
    status: str
    created_at: str

class SimulationConfig(BaseModel):
    hot_clients: int = Field(default=50, gt=0)
    normal_clients: int = Field(default=10, gt=0)

def get_cached_order(order_id: str):
    """Try to get order from Redis cache"""
    cached = redis_client.get(f"order:{order_id}")
    if cached:
        return json.loads(cached)
    return None

def cache_order(order_id: str, order_data: dict):
    """Cache order in Redis with 5 minute expiry"""
    redis_client.setex(
        f"order:{order_id}",
        300,  # 5 minutes
        json.dumps(order_data)
    )

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
        # Cache the order
        cache_order(order_data['order_id'], order_data)
        return order_data
    except Exception as e:
        logger.error(f"Failed to create order: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to create order")

@app.get("/orders/{order_id}", response_model=Order)
async def get_order(order_id: str):
    """Get a specific order by ID"""
    try:
        # Try cache first
        cached_order = get_cached_order(order_id)
        if cached_order:
            logger.info(f"Cache hit for order: {order_id}")
            return cached_order

        # If not in cache, get from Cassandra
        row = session.execute(
            "SELECT * FROM orders WHERE order_id = %s", 
            (order_id,)
        ).one()
        
        if not row:
            raise HTTPException(status_code=404, detail="Order not found")
        
        order_data = {
            "order_id": row.order_id,
            "customer_name": row.customer_name,
            "item": row.item,
            "quantity": row.quantity,
            "status": row.status,
            "created_at": row.created_at.isoformat()
        }
        
        # Cache the result
        cache_order(order_id, order_data)
        logger.info(f"Cache miss for order: {order_id}")
        return order_data
        
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

@app.post("/simulation/start")
async def start_simulation(config: SimulationConfig, background_tasks: BackgroundTasks):
    """Start the Redis hot key simulation"""
    global redis_simulator
    
    if redis_simulator:
        raise HTTPException(status_code=400, detail="Simulation already running")
    
    try:
        redis_simulator = RedisHotKeySimulator()
        background_tasks.add_task(
            redis_simulator.run_simulation,
            num_hot_clients=config.hot_clients,
            num_normal_clients=config.normal_clients
        )
        return {"message": "Simulation started", "config": config.dict()}
    except Exception as e:
        logger.error(f"Failed to start simulation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to start simulation")

@app.post("/simulation/stop")
async def stop_simulation():
    """Stop the Redis hot key simulation"""
    global redis_simulator
    
    if not redis_simulator:
        raise HTTPException(status_code=400, detail="No simulation running")
    
    try:
        redis_simulator.running = False
        redis_simulator = None
        return {"message": "Simulation stopped"}
    except Exception as e:
        logger.error(f"Failed to stop simulation: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to stop simulation")

@app.get("/simulation/status")
async def get_simulation_status():
    """Get current simulation status"""
    global redis_simulator
    
    if not redis_simulator:
        return {"status": "stopped"}
    
    try:
        hot_key_memory = redis_client.memory_usage(redis_simulator.hot_key)
        return {
            "status": "running",
            "hot_key_memory": hot_key_memory,
            "hot_key": redis_simulator.hot_key,
            "hot_key_value": redis_client.get(redis_simulator.hot_key)
        }
    except Exception as e:
        logger.error(f"Failed to get simulation status: {str(e)}")
        raise HTTPException(status_code=500, detail="Failed to get simulation status")

@app.on_event("shutdown")
async def shutdown_event():
    """Cleanup connections on shutdown"""
    global redis_simulator
    
    if redis_simulator:
        redis_simulator.running = False
    producer.close()
    redis_client.close()

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
