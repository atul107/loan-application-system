import json
from kafka import KafkaProducer
from app.utils.logger import logger
from app.config import KAFKA_BROKER_URL
from app.utils.helper import json_serializer

# Create Kafka producer
producer = KafkaProducer(
    bootstrap_servers=KAFKA_BROKER_URL,
    value_serializer=lambda message: json.dumps(message, default=json_serializer).encode('utf-8')
)

def send_message(topic: str, message: dict):
    try:
        producer.send(topic, value=message)
        producer.flush()
        logger.info(f"Sent message to Kafka topic {topic}: {message}")
    except Exception as e:
        logger.error(f"Error sending message to Kafka: {e}")