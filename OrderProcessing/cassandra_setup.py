from cassandra.cluster import Cluster
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def init_cassandra():
    """Initialize Cassandra keyspace and tables"""
    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect()

        # Create keyspace
        session.execute("""
            CREATE KEYSPACE IF NOT EXISTS orders
            WITH replication = {
                'class': 'SimpleStrategy',
                'replication_factor': 1
            }
        """)
        
        # Use keyspace
        session.set_keyspace('orders')
        
        # Drop existing table if exists to update schema
        session.execute("DROP TABLE IF EXISTS orders")
        
        # Create orders table with updated schema
        session.execute("""
            CREATE TABLE orders (
                order_id text PRIMARY KEY,
                customer_name text,
                item text,
                quantity int,
                status text,
                created_at timestamp,
                processed_at timestamp
            )
        """)
        
        logger.info("Cassandra initialization completed successfully")
        return session
        
    except Exception as e:
        logger.error(f"Failed to initialize Cassandra: {str(e)}")
        raise

def get_cassandra_session():
    """Get a session to the Cassandra database"""
    try:
        cluster = Cluster(['127.0.0.1'])
        session = cluster.connect('orders')
        return session
    except Exception as e:
        logger.error(f"Failed to connect to Cassandra: {str(e)}")
        raise

if __name__ == "__main__":
    init_cassandra()