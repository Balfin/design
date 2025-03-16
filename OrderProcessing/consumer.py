from kafka import KafkaConsumer
import json
import logging
import signal
from datetime import datetime
from cassandra_setup import get_cassandra_session

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class OrderConsumer:
    def __init__(self, bootstrap_servers='localhost:9092'):
        self.running = True
        self.consumer = KafkaConsumer(
            'orders',
            bootstrap_servers=bootstrap_servers,
            value_deserializer=lambda v: json.loads(v.decode('utf-8')),
            group_id='order_processing_group',
            auto_offset_reset='earliest'
        )
        self.session = get_cassandra_session()
        
        # Setup signal handlers
        signal.signal(signal.SIGINT, self.shutdown)
        signal.signal(signal.SIGTERM, self.shutdown)

    def process_order(self, order):
        """Process a single order and store in Cassandra"""
        try:
            # Parse the timestamp
            created_at = datetime.fromisoformat(order['created_at'])
            processed_at = datetime.utcnow()

            # Insert into Cassandra
            self.session.execute("""
                INSERT INTO orders (
                    order_id, customer_name, item, 
                    quantity, status, created_at, processed_at
                ) VALUES (%s, %s, %s, %s, %s, %s, %s)
            """, (
                order['order_id'],
                order['customer_name'],
                order['item'],
                order['quantity'],
                'PROCESSED',
                created_at,
                processed_at
            ))
            logger.info(f"Processed order: {order['order_id']}")
            
        except Exception as e:
            logger.error(f"Error processing order {order.get('order_id', 'unknown')}: {str(e)}")
            logger.error(f"Order data: {order}")

    def run(self):
        """Main consumer loop"""
        logger.info("Starting order consumer...")
        
        while self.running:
            try:
                # Poll for messages with timeout
                messages = self.consumer.poll(timeout_ms=1000)
                
                for topic_partition, records in messages.items():
                    for record in records:
                        self.process_order(record.value)
                        
            except Exception as e:
                logger.error(f"Error consuming messages: {str(e)}")
                if not self.running:
                    break

    def shutdown(self, signum, frame):
        """Graceful shutdown handler"""
        logger.info("Shutting down consumer...")
        self.running = False
        self.consumer.close()

if __name__ == "__main__":
    consumer = OrderConsumer()
    consumer.run()
