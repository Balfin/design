from kafka import KafkaProducer
import json
import uuid
import time
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderProducer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.producer = KafkaProducer(
            bootstrap_servers=bootstrap_servers,
            value_serializer=lambda v: json.dumps(v).encode('utf-8')
        )

    def send_order(self, customer_name: str, item: str, quantity: int) -> dict:
        """Send an order to Kafka topic"""
        try:
            order = {
                "order_id": str(uuid.uuid4()),
                "customer_name": customer_name,
                "item": item,
                "quantity": quantity,
                "status": "NEW",
                "created_at": datetime.utcnow().isoformat()
            }
            
            self.producer.send('orders', order)
            self.producer.flush()  # Ensure the message is sent
            logger.info(f"Order sent successfully: {order['order_id']}")
            return order
            
        except Exception as e:
            logger.error(f"Failed to send order: {str(e)}")
            raise

    def close(self):
        """Close the producer connection"""
        self.producer.close()

def simulate_orders(num_orders: int = 5, delay: int = 1):
    """Simulate sending multiple orders"""
    producer = OrderProducer()
    try:
        for i in range(num_orders):
            order = producer.send_order(
                customer_name=f'Customer-{i}',
                item=f'Item-{i}',
                quantity=i + 1
            )
            logger.info(f"Simulated order: {order}")
            time.sleep(delay)
    finally:
        producer.close()

if __name__ == "__main__":
    simulate_orders()
