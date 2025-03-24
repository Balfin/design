import redis
import time
import threading
import random
import logging
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class RedisHotKeySimulator:
    def __init__(self, host='localhost', port=6379, db=0):
        self.redis_client = redis.Redis(host=host, port=port, db=db)
        self.hot_key = "hot_product"
        self.normal_keys = [f"product_{i}" for i in range(1, 11)]
        self.running = True

    def initialize_data(self):
        """Initialize product data in Redis"""
        try:
            # Set hot key (popular product)
            self.redis_client.set(self.hot_key, "Popular Product Stock: 1000")
            
            # Set normal keys (regular products)
            for key in self.normal_keys:
                self.redis_client.set(key, f"{key} Stock: 100")
                
            logger.info("Initialized Redis with product data")
        except Exception as e:
            logger.error(f"Error initializing Redis data: {e}")

    def simulate_hot_key_access(self):
        """Simulate heavy access to the hot key"""
        while self.running:
            try:
                # Simulate many reads on hot key
                value = self.redis_client.get(self.hot_key)
                # Simulate some writes (updates)
                if random.random() < 0.1:  # 10% chance of write
                    self.redis_client.set(self.hot_key, f"Popular Product Stock: {random.randint(0, 1000)}")
                time.sleep(0.01)  # 10ms between requests
            except Exception as e:
                logger.error(f"Error accessing hot key: {e}")

    def simulate_normal_access(self):
        """Simulate normal access to regular keys"""
        while self.running:
            try:
                # Random access to normal keys
                key = random.choice(self.normal_keys)
                value = self.redis_client.get(key)
                if random.random() < 0.05:  # 5% chance of write
                    self.redis_client.set(key, f"{key} Stock: {random.randint(0, 100)}")
                time.sleep(0.1)  # 100ms between requests
            except Exception as e:
                logger.error(f"Error accessing normal key: {e}")

    def monitor_key_stats(self):
        """Monitor and log statistics about key access"""
        while self.running:
            try:
                # Get memory usage for hot key
                hot_key_memory = self.redis_client.memory_usage(self.hot_key)
                
                # Log statistics
                logger.info(f"Hot Key Memory Usage: {hot_key_memory} bytes")
                logger.info(f"Time: {datetime.now().isoformat()}")
                
                time.sleep(5)  # Log every 5 seconds
            except Exception as e:
                logger.error(f"Error monitoring stats: {e}")

    def run_simulation(self, num_hot_clients=50, num_normal_clients=10):
        """Run the hot key simulation"""
        try:
            # Initialize data
            self.initialize_data()
            
            # Create threads for hot key access
            hot_threads = [
                threading.Thread(target=self.simulate_hot_key_access)
                for _ in range(num_hot_clients)
            ]
            
            # Create threads for normal access
            normal_threads = [
                threading.Thread(target=self.simulate_normal_access)
                for _ in range(num_normal_clients)
            ]
            
            # Create monitoring thread
            monitor_thread = threading.Thread(target=self.monitor_key_stats)
            
            # Start all threads
            all_threads = hot_threads + normal_threads + [monitor_thread]
            for thread in all_threads:
                thread.start()
                
            logger.info(f"Started simulation with {num_hot_clients} hot clients and {num_normal_clients} normal clients")
            
            # Wait for keyboard interrupt
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                logger.info("Stopping simulation...")
                self.running = False
                
            # Wait for all threads to complete
            for thread in all_threads:
                thread.join()
                
        except Exception as e:
            logger.error(f"Error in simulation: {e}")
        finally:
            self.running = False

if __name__ == "__main__":
    simulator = RedisHotKeySimulator()
    simulator.run_simulation() 