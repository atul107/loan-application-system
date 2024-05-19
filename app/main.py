import uvicorn
from fastapi import FastAPI
from api import routes
from fastapi.middleware.cors import CORSMiddleware
from models.database import Base, engine, get_db
import threading
from sqlalchemy.orm import Session
from workers.kafka_consumer import KafkaConsumerService 

app = FastAPI()

# Include routes
app.include_router(routes.router, prefix="/api/v1")

# Configure CORS (Cross-Origin Resource Sharing)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# Create the database tables
Base.metadata.create_all(bind=engine)

def start_consumer():
    db_session: Session = next(get_db())
    kafka_consumer_service = KafkaConsumerService(db_session)
    kafka_consumer_service.consume_messages()

if __name__ == "__main__":
    # Start Kafka consumer in a separate thread
    consumer_thread = threading.Thread(target=start_consumer)
    consumer_thread.start()

    # Start FastAPI server
    uvicorn.run(app, host="0.0.0.0", port=8080)
