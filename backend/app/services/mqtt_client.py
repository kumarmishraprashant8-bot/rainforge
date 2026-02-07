"""MQTT Client for RainForge IoT Integration."""
import asyncio
import json
import logging
from datetime import datetime
from typing import Callable, Optional, Dict, Any
from dataclasses import dataclass
import paho.mqtt.client as mqtt

from app.core.config import settings

logger = logging.getLogger(__name__)


@dataclass
class SensorReading:
    """Represents a single sensor reading from an IoT device."""
    device_id: str
    project_id: int
    sensor_type: str  # tank_level, flow_rate, rainfall, temperature
    value: float
    unit: str
    timestamp: datetime
    battery_percent: Optional[int] = None
    signal_strength: Optional[int] = None  # RSSI


class MQTTClient:
    """
    MQTT Client for receiving sensor data from IoT devices.
    
    Topic Structure:
        rainforge/sensors/{project_id}/{sensor_type}
        rainforge/devices/{device_id}/status
        rainforge/alerts/{project_id}
    """
    
    TOPIC_SENSORS = "rainforge/sensors/#"
    TOPIC_DEVICES = "rainforge/devices/#"
    
    def __init__(
        self,
        broker_host: str = None,
        broker_port: int = None,
        username: Optional[str] = None,
        password: Optional[str] = None,
        client_id: str = "rainforge-backend"
    ):
        self.broker_host = broker_host or settings.MQTT_BROKER_HOST
        self.broker_port = broker_port or settings.MQTT_BROKER_PORT
        self.client_id = client_id
        
        # Create MQTT client
        self.client = mqtt.Client(
            client_id=client_id,
            protocol=mqtt.MQTTv5,
            callback_api_version=mqtt.CallbackAPIVersion.VERSION2
        )
        
        # Set credentials if provided
        if username and password:
            self.client.username_pw_set(username, password)
        elif settings.MQTT_USERNAME and settings.MQTT_PASSWORD:
            self.client.username_pw_set(settings.MQTT_USERNAME, settings.MQTT_PASSWORD)
        
        # Callbacks
        self.client.on_connect = self._on_connect
        self.client.on_message = self._on_message
        self.client.on_disconnect = self._on_disconnect
        self.client.on_subscribe = self._on_subscribe
        
        # Message handler
        self._message_handler: Optional[Callable[[SensorReading], None]] = None
        self._connected = False
    
    def _on_connect(self, client, userdata, flags, reason_code, properties=None):
        """Handle connection to MQTT broker."""
        if reason_code == 0:
            logger.info(f"✅ Connected to MQTT broker at {self.broker_host}:{self.broker_port}")
            self._connected = True
            # Subscribe to sensor topics
            client.subscribe(self.TOPIC_SENSORS, qos=1)
            client.subscribe(self.TOPIC_DEVICES, qos=1)
        else:
            logger.error(f"❌ MQTT connection failed with code: {reason_code}")
            self._connected = False
    
    def _on_disconnect(self, client, userdata, disconnect_flags, reason_code, properties=None):
        """Handle disconnection from MQTT broker."""
        logger.warning(f"⚠️ Disconnected from MQTT broker: {reason_code}")
        self._connected = False
    
    def _on_subscribe(self, client, userdata, mid, reason_codes, properties=None):
        """Handle subscription confirmation."""
        logger.info(f"📡 Subscribed to topics (mid: {mid})")
    
    def _on_message(self, client, userdata, msg):
        """Process incoming MQTT messages."""
        try:
            topic = msg.topic
            payload = json.loads(msg.payload.decode("utf-8"))
            
            logger.debug(f"📨 Received message on {topic}: {payload}")
            
            # Parse topic: rainforge/sensors/{project_id}/{sensor_type}
            topic_parts = topic.split("/")
            
            if len(topic_parts) >= 4 and topic_parts[1] == "sensors":
                project_id = int(topic_parts[2])
                sensor_type = topic_parts[3]
                
                reading = SensorReading(
                    device_id=payload.get("device_id", "unknown"),
                    project_id=project_id,
                    sensor_type=sensor_type,
                    value=float(payload["value"]),
                    unit=payload.get("unit", ""),
                    timestamp=datetime.fromisoformat(
                        payload.get("timestamp", datetime.utcnow().isoformat())
                    ),
                    battery_percent=payload.get("battery"),
                    signal_strength=payload.get("rssi")
                )
                
                # Call handler if registered
                if self._message_handler:
                    self._message_handler(reading)
                    
        except json.JSONDecodeError as e:
            logger.error(f"Invalid JSON in MQTT message: {e}")
        except Exception as e:
            logger.error(f"Error processing MQTT message: {e}")
    
    def set_message_handler(self, handler: Callable[[SensorReading], None]):
        """Set the callback for processing sensor readings."""
        self._message_handler = handler
    
    def connect(self) -> bool:
        """Connect to the MQTT broker."""
        try:
            self.client.connect(self.broker_host, self.broker_port, keepalive=60)
            self.client.loop_start()
            return True
        except Exception as e:
            logger.error(f"Failed to connect to MQTT broker: {e}")
            return False
    
    def disconnect(self):
        """Disconnect from the MQTT broker."""
        self.client.loop_stop()
        self.client.disconnect()
        self._connected = False
        logger.info("Disconnected from MQTT broker")
    
    def publish(self, topic: str, payload: Dict[str, Any], qos: int = 1) -> bool:
        """Publish a message to a topic."""
        try:
            result = self.client.publish(topic, json.dumps(payload), qos=qos)
            return result.rc == mqtt.MQTT_ERR_SUCCESS
        except Exception as e:
            logger.error(f"Failed to publish to {topic}: {e}")
            return False
    
    def is_connected(self) -> bool:
        """Check if connected to broker."""
        return self._connected
    
    @staticmethod
    def get_topic(project_id: int, sensor_type: str) -> str:
        """Generate topic string for a sensor."""
        return f"rainforge/sensors/{project_id}/{sensor_type}"


# Singleton instance
_mqtt_client: Optional[MQTTClient] = None


def get_mqtt_client() -> MQTTClient:
    """Get or create the MQTT client singleton."""
    global _mqtt_client
    if _mqtt_client is None:
        _mqtt_client = MQTTClient()
    return _mqtt_client
