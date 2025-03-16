# Order Processing System

This system implements a distributed order processing pipeline using Apache Kafka and Apache Cassandra.

## Components

- `producer.py`: Kafka producer for publishing order events
- `consumer.py`: Kafka consumer for processing order events
- `api.py`: REST API for order submission and status queries
- `cassandra_setup.py`: Cassandra database setup and schema definitions

## Prerequisites

- Python 3.8+
- Apache Kafka
- Apache Cassandra
- Required Python packages (install via `pip install -r requirements.txt`):
  - kafka-python
  - cassandra-driver
  - fastapi
  - uvicorn
  - python-dotenv

## Setup

1. Start Kafka and Cassandra services
2. Run `python cassandra_setup.py` to initialize the database schema
3. Start the consumer: `python consumer.py`
4. Start the API server: `python api.py`
5. The producer will be automatically used by the API to publish orders

## Architecture

The system follows an event-driven architecture:
1. Orders are submitted through the REST API
2. The producer publishes order events to Kafka
3. The consumer processes these events and stores results in Cassandra
4. The API can be used to query order status from Cassandra 