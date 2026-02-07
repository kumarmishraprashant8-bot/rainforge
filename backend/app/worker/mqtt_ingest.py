import logging
import json
import threading
import time
from datetime import datetime
import paho.mqtt.client as mqtt
from sqlalchemy.orm import Session
from app.core.database import SessionLocal
from app.models.telemetry import Telemetry

logger = logging.getLogger(__name__)

class MQTTWorker:
    def __init__(self, broker_host="broker.hivemq.com", broker_port=1883):
        self.broker_host = broker_host
        self.broker_port = broker_port
        self.client = mqtt.Client()
        self.client.on_connect = self.on_connect
        self.client.on_message = self.on_message
        self.running = False

    def on_connect(self, client, userdata, flags, rc):
        logger.info(f"Connected to MQTT broker with result code {rc}")
        # Subscribe to all rainforge telemetry topics
        client.subscribe("rainforge/+/telemetry")

    def on_message(self, client, userdata, msg):
        try:
            topic = msg.topic
            payload = msg.payload.decode()
            # Topic format: rainforge/{device_id}/telemetry
            parts = topic.split('/')
            if len(parts) >= 3:
                device_id = parts[1]
                self.process_message(device_id, payload)
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")

    def process_message(self, device_id: str, payload: str):
        db: Session = SessionLocal()
        try:
            data = json.loads(payload)
            telemetry = Telemetry(
                device_id=device_id,
                timestamp=datetime.now(), # In prod, use timestamp from payload if trustworthy
                flow_rate=data.get("flow_rate", 0.0),
                total_volume=data.get("total_volume", 0.0),
                battery_voltage=data.get("battery", 0.0),
                ph_level=data.get("ph", 7.0),
                turbidity=data.get("turbidity", 0.0)
            )
            db.add(telemetry)
            db.commit()
            logger.debug(f"Ingested telemetry for {device_id}")
        except json.JSONDecodeError:
            logger.warning(f"Invalid JSON from {device_id}: {payload}")
        except Exception as e:
            logger.error(f"DB Error ingestion: {e}")
        finally:
            db.close()

    def start(self):
        if not self.running:
            logger.info("Starting MQTT Worker...")
            try:
                self.client.connect(self.broker_host, self.broker_port, 60)
                self.client.loop_start()
                self.running = True
            except Exception as e:
                logger.error(f"Failed to connect to MQTT broker: {e}")

    def stop(self):
        if self.running:
            logger.info("Stopping MQTT Worker...")
            self.client.loop_stop()
            self.client.disconnect()
            self.running = False

# Global instance
mqtt_worker = MQTTWorker()

def get_mqtt_worker():
    return mqtt_worker
