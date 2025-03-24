# Order Processing System

A microservices-based order processing system with hot key simulation capabilities.

## Project Structure

```
OrderProcessing/
├── api.py              # FastAPI backend server
├── producer.py         # Kafka message producer
├── consumer.py         # Kafka message consumer
├── cassandra_setup.py  # Database initialization
├── redis_service.py    # Redis hot key simulation
├── frontend/          # React frontend application
└── requirements.txt    # Python dependencies
```

## Quick Start

### 1. Install Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python packages
pip install -r requirements.txt

# Install frontend dependencies
cd frontend
npm install
```

### 2. Start Services

Ensure these services are running:
- Apache Kafka (with ZooKeeper)
- Apache Cassandra
- Redis Server

### 3. Initialize Database

```bash
python cassandra_setup.py
```

### 4. Start Application Components

Start each component in a separate terminal:

```bash
# Terminal 1: Start the consumer
python consumer.py

# Terminal 2: Start the API
python api.py

# Terminal 3: Start the frontend
cd frontend
npm start
```

## Component Details

### Backend (FastAPI)

- **API Server (api.py)**
  - Runs on: http://localhost:8000
  - Swagger UI: http://localhost:8000/docs
  - Handles order creation and retrieval
  - Manages Redis simulation controls

- **Message Queue (producer.py, consumer.py)**
  - Uses Kafka for message processing
  - Producer publishes new orders
  - Consumer processes orders and stores in Cassandra

- **Database (cassandra_setup.py)**
  - Initializes Cassandra schema
  - Creates required keyspace and tables

### Frontend (React)

- Modern UI built with Material-UI
- Real-time order management
- Redis simulation control panel
- Automatic data refresh

## Redis Hot Key Simulation

Test system performance under high load:

1. Access simulation panel at http://localhost:3000/simulation
2. Configure:
   - Hot clients (high-frequency requests)
   - Normal clients (regular traffic)
3. Monitor:
   - Memory usage
   - Response times
   - Key access patterns

## Development

### Backend Development

```bash
# Run API with auto-reload
uvicorn api:app --reload --port 8000

# Run tests (if available)
pytest
```

### Frontend Development

```bash
cd frontend

# Start development server
npm start

# Run tests
npm test

# Build for production
npm run build
```

## Environment Variables

Create a `.env` file in the root directory:

```env
KAFKA_BOOTSTRAP_SERVERS=localhost:9092
CASSANDRA_CONTACT_POINTS=["localhost"]
REDIS_HOST=localhost
REDIS_PORT=6379
```

## Common Issues

1. **Connection Errors**
   - Verify all services are running
   - Check port availability
   - Ensure correct connection strings

2. **CORS Issues**
   - Backend CORS is configured for localhost:3000
   - Check browser console for specific errors

3. **Database Errors**
   - Run cassandra_setup.py again
   - Verify Cassandra is running and accessible

## API Routes

```
Orders:
GET    /orders/            - List all orders
POST   /orders/            - Create new order
GET    /orders/{order_id}  - Get order details

Simulation:
POST   /simulation/start   - Start Redis simulation
POST   /simulation/stop    - Stop simulation
GET    /simulation/status  - Get simulation status 