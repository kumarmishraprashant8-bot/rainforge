from unittest.mock import MagicMock, patch
import json
import pytest
from app.worker.mqtt_ingest import MQTTWorker

def test_mqtt_worker_process_message():
    # Mock DB session
    mock_db = MagicMock()
    
    with patch('app.worker.mqtt_ingest.SessionLocal', return_value=mock_db):
        worker = MQTTWorker(broker_host="localhost")
        
        # Test valid message
        payload = json.dumps({
            "flow_rate": 10.5,
            "total_volume": 100.0,
            "battery": 12.4
        })
        worker.process_message("dev123", payload)
        
        # Verify DB add called
        assert mock_db.add.called
        assert mock_db.commit.called
        
        # Verify Telemetry object
        args, _ = mock_db.add.call_args
        telemetry = args[0]
        assert telemetry.device_id == "dev123"
        assert telemetry.flow_rate == 10.5

def test_mqtt_worker_invalid_json():
    mock_db = MagicMock()
    with patch('app.worker.mqtt_ingest.SessionLocal', return_value=mock_db):
        worker = MQTTWorker()
        worker.process_message("dev123", "BAD JSON")
        
        # Should not throw, just log error
        assert not mock_db.add.called
