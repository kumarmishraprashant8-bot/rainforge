"""
LoRaWAN Gateway Service
Long-range IoT for rural areas
"""
import logging
from datetime import datetime
from typing import Optional, Dict, List, Any
from dataclasses import dataclass
from enum import Enum
import json
import base64

logger = logging.getLogger(__name__)


class DeviceClass(str, Enum):
    """LoRaWAN device classes."""
    CLASS_A = "A"  # Battery-powered, lowest power
    CLASS_B = "B"  # Scheduled receive slots
    CLASS_C = "C"  # Continuous listening


class ActivationType(str, Enum):
    """LoRaWAN activation types."""
    OTAA = "otaa"  # Over-the-air activation
    ABP = "abp"    # Activation by personalization


@dataclass
class LoRaDevice:
    """LoRaWAN device registration."""
    dev_eui: str  # Device unique identifier
    app_key: str  # Application key for OTAA
    name: str
    device_class: DeviceClass
    activation: ActivationType
    project_id: Optional[int] = None
    last_seen: Optional[datetime] = None
    frame_counter_up: int = 0
    frame_counter_down: int = 0
    metadata: Dict[str, Any] = None


@dataclass
class UplinkMessage:
    """LoRaWAN uplink message."""
    dev_eui: str
    f_cnt: int
    f_port: int
    frm_payload: bytes
    rx_info: Dict[str, Any]  # Gateway reception info
    tx_info: Dict[str, Any]  # Transmission info
    timestamp: datetime


class LoRaWANService:
    """
    LoRaWAN gateway integration for remote sensors.
    
    Supports:
    - The Things Network (TTN)
    - ChirpStack
    - Custom LoRa gateways
    
    Use cases:
    - Remote rural tank monitoring
    - Agricultural rain gauges
    - Large-area deployments
    """
    
    # Payload decoders by device type
    PAYLOAD_DECODERS = {
        "tank_sensor": "_decode_tank_payload",
        "rain_gauge": "_decode_rain_payload",
        "flow_meter": "_decode_flow_payload"
    }
    
    def __init__(self):
        from app.core.config import settings
        
        self._devices: Dict[str, LoRaDevice] = {}
        
        # Gateway configuration
        self.network_server = getattr(settings, 'LORA_NETWORK_SERVER', 'chirpstack')
        self.api_url = getattr(settings, 'LORA_API_URL', None)
        self.api_key = getattr(settings, 'LORA_API_KEY', None)
    
    async def register_device(
        self,
        dev_eui: str,
        app_key: str,
        name: str,
        project_id: int,
        device_class: DeviceClass = DeviceClass.CLASS_A,
        device_type: str = "tank_sensor"
    ) -> LoRaDevice:
        """Register a new LoRaWAN device."""
        device = LoRaDevice(
            dev_eui=dev_eui.upper().replace(":", ""),
            app_key=app_key.upper(),
            name=name,
            device_class=device_class,
            activation=ActivationType.OTAA,
            project_id=project_id,
            metadata={"device_type": device_type}
        )
        
        self._devices[device.dev_eui] = device
        
        logger.info(f"Registered LoRa device: {dev_eui} ({name})")
        
        # In production, would also register with network server
        if self.api_url:
            await self._register_with_network_server(device)
        
        return device
    
    async def _register_with_network_server(self, device: LoRaDevice):
        """Register device with network server (ChirpStack/TTN)."""
        import httpx
        
        if not self.api_url or not self.api_key:
            logger.warning("Network server not configured")
            return
        
        try:
            async with httpx.AsyncClient() as client:
                if self.network_server == "chirpstack":
                    response = await client.post(
                        f"{self.api_url}/api/devices",
                        json={
                            "device": {
                                "devEUI": device.dev_eui,
                                "name": device.name,
                                "applicationID": "rainforge",
                                "description": f"RainForge sensor for project {device.project_id}",
                                "deviceProfileID": device.device_class.value,
                            }
                        },
                        headers={"Authorization": f"Bearer {self.api_key}"}
                    )
                    
                    if response.status_code == 200:
                        logger.info(f"Device registered with ChirpStack: {device.dev_eui}")
                    else:
                        logger.error(f"ChirpStack registration failed: {response.text}")
                        
        except Exception as e:
            logger.error(f"Network server registration failed: {e}")
    
    async def handle_uplink(
        self,
        message: UplinkMessage
    ) -> Dict[str, Any]:
        """
        Handle incoming LoRaWAN uplink message.
        Called by webhook from network server.
        """
        dev_eui = message.dev_eui.upper()
        
        if dev_eui not in self._devices:
            logger.warning(f"Unknown device: {dev_eui}")
            return {"error": "Unknown device"}
        
        device = self._devices[dev_eui]
        device.last_seen = message.timestamp
        device.frame_counter_up = message.f_cnt
        
        # Decode payload based on device type
        device_type = device.metadata.get("device_type", "tank_sensor")
        decoder = self.PAYLOAD_DECODERS.get(device_type)
        
        if decoder:
            decoded_data = getattr(self, decoder)(message.frm_payload)
        else:
            decoded_data = {"raw": base64.b64encode(message.frm_payload).decode()}
        
        # Extract signal info
        signal_info = self._extract_signal_info(message.rx_info)
        
        result = {
            "dev_eui": dev_eui,
            "project_id": device.project_id,
            "timestamp": message.timestamp.isoformat(),
            "data": decoded_data,
            "signal": signal_info,
            "frame_count": message.f_cnt
        }
        
        logger.info(f"LoRa uplink from {dev_eui}: {decoded_data}")
        
        # Store sensor reading
        await self._store_sensor_reading(device, decoded_data, message.timestamp)
        
        return result
    
    def _decode_tank_payload(self, payload: bytes) -> Dict[str, Any]:
        """Decode tank sensor payload."""
        # CayenneLPP-like format:
        # Byte 0: Channel (1 = tank level)
        # Byte 1: Data type (0x02 = analog input)
        # Bytes 2-3: Value (tank level * 100)
        # Byte 4: Channel (2 = battery)
        # Byte 5: Data type
        # Bytes 6-7: Value (battery mV)
        
        if len(payload) < 4:
            return {"error": "Payload too short"}
        
        try:
            tank_level = (payload[2] << 8 | payload[3]) / 100.0
            
            battery_mv = 0
            if len(payload) >= 8:
                battery_mv = payload[6] << 8 | payload[7]
            
            return {
                "tank_level_percent": round(tank_level, 1),
                "battery_mv": battery_mv,
                "battery_percent": self._mv_to_percent(battery_mv)
            }
        except Exception as e:
            logger.error(f"Tank payload decode error: {e}")
            return {"error": str(e)}
    
    def _decode_rain_payload(self, payload: bytes) -> Dict[str, Any]:
        """Decode rain gauge payload."""
        if len(payload) < 4:
            return {"error": "Payload too short"}
        
        try:
            # Rain count (tips) since last transmission
            rain_tips = payload[2] << 8 | payload[3]
            rain_mm = rain_tips * 0.2  # 0.2mm per tip
            
            return {
                "rain_tips": rain_tips,
                "rain_mm": round(rain_mm, 1)
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _decode_flow_payload(self, payload: bytes) -> Dict[str, Any]:
        """Decode flow meter payload."""
        if len(payload) < 6:
            return {"error": "Payload too short"}
        
        try:
            # Cumulative liters (4 bytes)
            total_liters = (
                payload[2] << 24 |
                payload[3] << 16 |
                payload[4] << 8 |
                payload[5]
            )
            
            return {
                "total_liters": total_liters
            }
        except Exception as e:
            return {"error": str(e)}
    
    def _extract_signal_info(self, rx_info: Dict) -> Dict[str, Any]:
        """Extract signal quality info."""
        if not rx_info:
            return {}
        
        # Handle list format (multiple gateways)
        if isinstance(rx_info, list) and rx_info:
            rx_info = rx_info[0]
        
        return {
            "rssi": rx_info.get("rssi", 0),
            "snr": rx_info.get("loRaSNR", 0),
            "gateway_id": rx_info.get("gatewayID", ""),
            "channel": rx_info.get("channel", 0)
        }
    
    def _mv_to_percent(self, mv: int) -> int:
        """Convert battery millivolts to percentage."""
        # Typical for 3.6V Li-SOCl2 battery
        if mv >= 3600:
            return 100
        elif mv <= 2800:
            return 0
        else:
            return int((mv - 2800) / 8)  # Linear approximation
    
    async def _store_sensor_reading(
        self,
        device: LoRaDevice,
        data: Dict[str, Any],
        timestamp: datetime
    ):
        """Store sensor reading (would integrate with telemetry service)."""
        # In production, would call telemetry service
        from app.services.telemetry_ingestion import get_telemetry_service
        
        try:
            telemetry = get_telemetry_service()
            
            if "tank_level_percent" in data:
                await telemetry.ingest_reading({
                    "sensor_id": f"lora_{device.dev_eui}",
                    "project_id": device.project_id,
                    "sensor_type": "tank_level",
                    "value": data["tank_level_percent"],
                    "timestamp": timestamp.isoformat()
                })
            
            if "rain_mm" in data:
                await telemetry.ingest_reading({
                    "sensor_id": f"lora_{device.dev_eui}",
                    "project_id": device.project_id,
                    "sensor_type": "rainfall",
                    "value": data["rain_mm"],
                    "timestamp": timestamp.isoformat()
                })
                
        except Exception as e:
            logger.error(f"Failed to store LoRa reading: {e}")
    
    async def send_downlink(
        self,
        dev_eui: str,
        payload: bytes,
        f_port: int = 1,
        confirmed: bool = False
    ) -> bool:
        """Send downlink message to device."""
        dev_eui = dev_eui.upper()
        
        if dev_eui not in self._devices:
            return False
        
        device = self._devices[dev_eui]
        device.frame_counter_down += 1
        
        logger.info(f"Sending downlink to {dev_eui}: {payload.hex()}")
        
        # In production, would send via network server
        return True
    
    def get_device_status(self, dev_eui: str) -> Optional[Dict]:
        """Get device status."""
        dev_eui = dev_eui.upper()
        device = self._devices.get(dev_eui)
        
        if not device:
            return None
        
        return {
            "dev_eui": device.dev_eui,
            "name": device.name,
            "project_id": device.project_id,
            "last_seen": device.last_seen.isoformat() if device.last_seen else None,
            "frame_counter_up": device.frame_counter_up,
            "device_class": device.device_class.value,
            "online": (
                device.last_seen and 
                (datetime.utcnow() - device.last_seen).seconds < 86400
            )
        }
    
    def list_devices(self, project_id: Optional[int] = None) -> List[Dict]:
        """List all LoRa devices."""
        devices = list(self._devices.values())
        
        if project_id:
            devices = [d for d in devices if d.project_id == project_id]
        
        return [self.get_device_status(d.dev_eui) for d in devices]


# Singleton
_lora_service: Optional[LoRaWANService] = None

def get_lora_service() -> LoRaWANService:
    global _lora_service
    if _lora_service is None:
        _lora_service = LoRaWANService()
    return _lora_service
