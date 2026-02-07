/**
 * IoT Device Manager Component
 * Device pairing, calibration, and monitoring
 */

import React, { useState, useEffect } from 'react';

interface IoTDevice {
    device_id: string;
    device_type: string;
    device_name: string;
    device_serial: string;
    status: string;
    battery_level: number | null;
    signal_strength: number | null;
    calibrated: boolean;
    last_seen: string | null;
}

interface Alert {
    alert_id: string;
    alert_type: string;
    message: string;
    severity: string;
    created_at: string;
    acknowledged: boolean;
}

interface IoTDeviceManagerProps {
    projectId: number;
}

export const IoTDeviceManager: React.FC<IoTDeviceManagerProps> = ({
    projectId,
}) => {
    const [activeView, setActiveView] = useState<'devices' | 'pair' | 'alerts'>('devices');
    const [devices, setDevices] = useState<IoTDevice[]>([]);
    const [alerts, setAlerts] = useState<Alert[]>([]);
    const [pairingQR, setPairingQR] = useState<string | null>(null);
    const [pairingDeviceType, setPairingDeviceType] = useState('tank_level');
    const [calibrating, setCalibrating] = useState<string | null>(null);
    const [calibrationStep, setCalibrationStep] = useState(0);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchDevices();
        fetchAlerts();
    }, [projectId]);

    const fetchDevices = async () => {
        setLoading(true);
        try {
            // Demo data
            setDevices([
                {
                    device_id: 'DEV001',
                    device_type: 'tank_level',
                    device_name: 'Main Tank Sensor',
                    device_serial: 'TL-2024-001234',
                    status: 'online',
                    battery_level: 85,
                    signal_strength: 92,
                    calibrated: true,
                    last_seen: new Date().toISOString(),
                },
                {
                    device_id: 'DEV002',
                    device_type: 'flow_meter',
                    device_name: 'Inlet Flow Meter',
                    device_serial: 'FM-2024-005678',
                    status: 'online',
                    battery_level: 72,
                    signal_strength: 88,
                    calibrated: true,
                    last_seen: new Date().toISOString(),
                },
                {
                    device_id: 'DEV003',
                    device_type: 'water_quality',
                    device_name: 'Quality Monitor',
                    device_serial: 'WQ-2024-009876',
                    status: 'offline',
                    battery_level: 15,
                    signal_strength: null,
                    calibrated: true,
                    last_seen: new Date(Date.now() - 86400000).toISOString(),
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const fetchAlerts = async () => {
        setAlerts([
            {
                alert_id: 'ALT001',
                alert_type: 'tank_low',
                message: 'Tank level below 20%. Consider conserving water.',
                severity: 'warning',
                created_at: new Date(Date.now() - 3600000).toISOString(),
                acknowledged: false,
            },
            {
                alert_id: 'ALT002',
                alert_type: 'sensor_offline',
                message: 'Quality Monitor has been offline for 24 hours',
                severity: 'high',
                created_at: new Date(Date.now() - 86400000).toISOString(),
                acknowledged: false,
            },
            {
                alert_id: 'ALT003',
                alert_type: 'first_flush',
                message: 'First flush triggered - 15L diverted',
                severity: 'info',
                created_at: new Date(Date.now() - 172800000).toISOString(),
                acknowledged: true,
            },
        ]);
    };

    const handleGeneratePairingQR = async () => {
        setLoading(true);
        try {
            // In production, this would call the API
            await new Promise(resolve => setTimeout(resolve, 1000));
            // Mock QR code (in production, this would be an actual QR code image)
            setPairingQR(`RAINFORGE-PAIR:${projectId}:${pairingDeviceType}:${Date.now()}`);
        } finally {
            setLoading(false);
        }
    };

    const handleStartCalibration = (deviceId: string) => {
        setCalibrating(deviceId);
        setCalibrationStep(1);
    };

    const handleCalibrationNext = () => {
        if (calibrationStep < 5) {
            setCalibrationStep(calibrationStep + 1);
        } else {
            // Complete calibration
            setCalibrating(null);
            setCalibrationStep(0);
            // Update device as calibrated
            setDevices(devices.map(d =>
                d.device_id === calibrating ? { ...d, calibrated: true } : d
            ));
        }
    };

    const handleAcknowledgeAlert = (alertId: string) => {
        setAlerts(alerts.map(a =>
            a.alert_id === alertId ? { ...a, acknowledged: true } : a
        ));
    };

    const getDeviceIcon = (type: string) => {
        switch (type) {
            case 'tank_level': return '📊';
            case 'flow_meter': return '💧';
            case 'water_quality': return '🔬';
            case 'rain_gauge': return '🌧️';
            case 'first_flush': return '🚿';
            default: return '📡';
        }
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'online': return '#22c55e';
            case 'offline': return '#ef4444';
            case 'pairing': return '#f59e0b';
            default: return '#64748b';
        }
    };

    const getSeverityColor = (severity: string) => {
        switch (severity) {
            case 'critical': return '#dc2626';
            case 'high': return '#ef4444';
            case 'warning': return '#f59e0b';
            case 'info': return '#3b82f6';
            default: return '#64748b';
        }
    };

    const getSeverityIcon = (severity: string) => {
        switch (severity) {
            case 'critical': return '🚨';
            case 'high': return '❗';
            case 'warning': return '⚠️';
            case 'info': return 'ℹ️';
            default: return '📌';
        }
    };

    return (
        <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            padding: '24px',
        }}>
            <h2 style={{
                fontSize: '24px',
                fontWeight: 700,
                marginBottom: '8px',
                color: '#1a1a2e',
            }}>
                📡 IoT Device Manager
            </h2>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
                Manage your smart sensors and monitoring devices
            </p>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'devices', label: `Devices (${devices.length})`, icon: '📡' },
                    { id: 'pair', label: 'Add Device', icon: '➕' },
                    { id: 'alerts', label: `Alerts (${alerts.filter(a => !a.acknowledged).length})`, icon: '🔔' },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveView(tab.id as any)}
                        style={{
                            flex: 1,
                            padding: '12px 16px',
                            background: activeView === tab.id
                                ? 'linear-gradient(135deg, #3b82f6, #2563eb)'
                                : 'white',
                            color: activeView === tab.id ? 'white' : '#64748b',
                            border: activeView === tab.id ? 'none' : '1px solid #e2e8f0',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            transition: 'all 0.2s ease',
                        }}
                    >
                        <span style={{ marginRight: '8px' }}>{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Devices View */}
            {activeView === 'devices' && (
                <div>
                    {devices.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '48px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📡</div>
                            <h3 style={{ marginBottom: '8px' }}>No Devices Connected</h3>
                            <p style={{ color: '#64748b', marginBottom: '16px' }}>
                                Add your first IoT sensor to start monitoring
                            </p>
                            <button
                                onClick={() => setActiveView('pair')}
                                style={{
                                    padding: '12px 24px',
                                    background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                    border: 'none',
                                    borderRadius: '10px',
                                    color: 'white',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                }}
                            >
                                + Add Device
                            </button>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {devices.map(device => (
                                <div
                                    key={device.device_id}
                                    style={{
                                        background: 'white',
                                        borderRadius: '12px',
                                        padding: '20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: `1px solid ${device.status === 'offline' ? '#fecaca' : '#e2e8f0'}`,
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ display: 'flex', gap: '16px', alignItems: 'center' }}>
                                            <div style={{
                                                width: '56px',
                                                height: '56px',
                                                borderRadius: '12px',
                                                background: device.status === 'online' ? '#dcfce7' : '#fee2e2',
                                                display: 'flex',
                                                alignItems: 'center',
                                                justifyContent: 'center',
                                                fontSize: '28px',
                                            }}>
                                                {getDeviceIcon(device.device_type)}
                                            </div>
                                            <div>
                                                <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                                                    {device.device_name}
                                                </h4>
                                                <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '13px' }}>
                                                    Serial: {device.device_serial}
                                                </p>
                                            </div>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                            <span style={{
                                                width: '8px',
                                                height: '8px',
                                                borderRadius: '50%',
                                                background: getStatusColor(device.status),
                                                animation: device.status === 'online' ? 'pulse 2s infinite' : 'none',
                                            }} />
                                            <span style={{
                                                color: getStatusColor(device.status),
                                                fontWeight: 600,
                                                fontSize: '14px',
                                            }}>
                                                {device.status.charAt(0).toUpperCase() + device.status.slice(1)}
                                            </span>
                                        </div>
                                    </div>

                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(4, 1fr)',
                                        gap: '16px',
                                        marginTop: '16px',
                                        padding: '12px',
                                        background: '#f8fafc',
                                        borderRadius: '8px',
                                    }}>
                                        <div>
                                            <div style={{ fontSize: '11px', color: '#64748b' }}>Battery</div>
                                            <div style={{
                                                fontWeight: 600,
                                                color: device.battery_level !== null
                                                    ? device.battery_level > 50 ? '#22c55e' : device.battery_level > 20 ? '#f59e0b' : '#ef4444'
                                                    : '#64748b',
                                            }}>
                                                {device.battery_level !== null ? `${device.battery_level}%` : '--'}
                                                {device.battery_level !== null && device.battery_level <= 20 && ' ⚠️'}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '11px', color: '#64748b' }}>Signal</div>
                                            <div style={{ fontWeight: 600, color: device.signal_strength ? '#22c55e' : '#64748b' }}>
                                                {device.signal_strength !== null ? `${device.signal_strength}%` : '--'}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '11px', color: '#64748b' }}>Calibrated</div>
                                            <div style={{ fontWeight: 600, color: device.calibrated ? '#22c55e' : '#f59e0b' }}>
                                                {device.calibrated ? '✓ Yes' : '✗ No'}
                                            </div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '11px', color: '#64748b' }}>Last Seen</div>
                                            <div style={{ fontWeight: 600, fontSize: '12px' }}>
                                                {device.last_seen
                                                    ? new Date(device.last_seen).toLocaleString('en-IN', {
                                                        hour: '2-digit',
                                                        minute: '2-digit',
                                                        hour12: true,
                                                    })
                                                    : 'Never'
                                                }
                                            </div>
                                        </div>
                                    </div>

                                    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                                        {!device.calibrated && (
                                            <button
                                                onClick={() => handleStartCalibration(device.device_id)}
                                                style={{
                                                    padding: '8px 16px',
                                                    background: 'linear-gradient(135deg, #f59e0b, #d97706)',
                                                    border: 'none',
                                                    borderRadius: '8px',
                                                    color: 'white',
                                                    fontWeight: 600,
                                                    cursor: 'pointer',
                                                    fontSize: '13px',
                                                }}
                                            >
                                                🔧 Calibrate
                                            </button>
                                        )}
                                        <button
                                            style={{
                                                padding: '8px 16px',
                                                background: 'white',
                                                border: '1px solid #e2e8f0',
                                                borderRadius: '8px',
                                                color: '#64748b',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                                fontSize: '13px',
                                            }}
                                        >
                                            ⚙️ Settings
                                        </button>
                                        {device.status === 'offline' && (
                                            <button
                                                style={{
                                                    padding: '8px 16px',
                                                    background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                                    border: 'none',
                                                    borderRadius: '8px',
                                                    color: 'white',
                                                    fontWeight: 600,
                                                    cursor: 'pointer',
                                                    fontSize: '13px',
                                                }}
                                            >
                                                🔄 Troubleshoot
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Pair Device View */}
            {activeView === 'pair' && (
                <div>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        border: '1px solid #e2e8f0',
                    }}>
                        <h3 style={{ marginBottom: '20px' }}>🔗 Pair New Device</h3>

                        <div style={{ marginBottom: '20px' }}>
                            <label style={{
                                display: 'block',
                                marginBottom: '8px',
                                fontSize: '14px',
                                fontWeight: 500,
                                color: '#374151',
                            }}>
                                Device Type
                            </label>
                            <select
                                value={pairingDeviceType}
                                onChange={(e) => setPairingDeviceType(e.target.value)}
                                style={{
                                    width: '100%',
                                    padding: '12px 14px',
                                    fontSize: '15px',
                                    border: '1px solid #e2e8f0',
                                    borderRadius: '10px',
                                    outline: 'none',
                                }}
                            >
                                <option value="tank_level">📊 Tank Level Sensor</option>
                                <option value="flow_meter">💧 Flow Meter</option>
                                <option value="water_quality">🔬 Water Quality Sensor</option>
                                <option value="rain_gauge">🌧️ Rain Gauge</option>
                                <option value="first_flush">🚿 First Flush Controller</option>
                            </select>
                        </div>

                        {!pairingQR ? (
                            <button
                                onClick={handleGeneratePairingQR}
                                disabled={loading}
                                style={{
                                    width: '100%',
                                    padding: '14px',
                                    background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                    border: 'none',
                                    borderRadius: '10px',
                                    color: 'white',
                                    fontWeight: 600,
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                }}
                            >
                                {loading ? '⏳ Generating...' : '📱 Generate Pairing QR Code'}
                            </button>
                        ) : (
                            <div style={{ textAlign: 'center' }}>
                                <div style={{
                                    display: 'inline-block',
                                    padding: '24px',
                                    background: 'white',
                                    borderRadius: '12px',
                                    boxShadow: '0 4px 20px rgba(0,0,0,0.1)',
                                    marginBottom: '16px',
                                }}>
                                    {/* Mock QR Code - in production, use a real QR library */}
                                    <div style={{
                                        width: '200px',
                                        height: '200px',
                                        background: `repeating-linear-gradient(
                      0deg,
                      #000 0px,
                      #000 8px,
                      #fff 8px,
                      #fff 16px
                    ),
                    repeating-linear-gradient(
                      90deg,
                      #000 0px,
                      #000 8px,
                      #fff 8px,
                      #fff 16px
                    )`,
                                        backgroundBlendMode: 'difference',
                                        borderRadius: '8px',
                                    }} />
                                </div>
                                <p style={{ color: '#64748b', marginBottom: '8px' }}>
                                    Scan this QR code with the RainForge IoT app
                                </p>
                                <p style={{ fontSize: '12px', color: '#94a3b8' }}>
                                    Code expires in 10 minutes
                                </p>
                                <button
                                    onClick={() => setPairingQR(null)}
                                    style={{
                                        marginTop: '16px',
                                        padding: '10px 20px',
                                        background: 'white',
                                        border: '1px solid #e2e8f0',
                                        borderRadius: '8px',
                                        color: '#64748b',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                    }}
                                >
                                    Generate New Code
                                </button>
                            </div>
                        )}

                        <div style={{
                            marginTop: '24px',
                            padding: '16px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <h4 style={{ marginBottom: '12px', fontSize: '14px' }}>📋 Pairing Instructions:</h4>
                            <ol style={{ margin: 0, paddingLeft: '20px', color: '#64748b', fontSize: '14px' }}>
                                <li>Power on your IoT device</li>
                                <li>Download the RainForge IoT app</li>
                                <li>Open the app and tap "Pair Device"</li>
                                <li>Scan the QR code above</li>
                                <li>Follow the on-screen instructions</li>
                            </ol>
                        </div>
                    </div>
                </div>
            )}

            {/* Alerts View */}
            {activeView === 'alerts' && (
                <div>
                    {alerts.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '48px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <div style={{ fontSize: '48px', marginBottom: '16px' }}>✅</div>
                            <h3 style={{ marginBottom: '8px' }}>No Active Alerts</h3>
                            <p style={{ color: '#64748b' }}>
                                All systems are operating normally
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {alerts.map(alert => (
                                <div
                                    key={alert.alert_id}
                                    style={{
                                        background: 'white',
                                        borderRadius: '12px',
                                        padding: '16px 20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: `1px solid ${alert.acknowledged ? '#e2e8f0' : getSeverityColor(alert.severity) + '40'}`,
                                        opacity: alert.acknowledged ? 0.7 : 1,
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-start' }}>
                                            <div style={{ fontSize: '24px' }}>
                                                {getSeverityIcon(alert.severity)}
                                            </div>
                                            <div>
                                                <div style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                                    <span style={{
                                                        padding: '2px 8px',
                                                        borderRadius: '12px',
                                                        fontSize: '11px',
                                                        fontWeight: 600,
                                                        background: getSeverityColor(alert.severity) + '20',
                                                        color: getSeverityColor(alert.severity),
                                                        textTransform: 'uppercase',
                                                    }}>
                                                        {alert.severity}
                                                    </span>
                                                    <span style={{ fontSize: '12px', color: '#94a3b8' }}>
                                                        {alert.alert_type.replace(/_/g, ' ')}
                                                    </span>
                                                </div>
                                                <p style={{ margin: '8px 0 0', fontSize: '14px' }}>
                                                    {alert.message}
                                                </p>
                                                <p style={{ margin: '4px 0 0', fontSize: '12px', color: '#94a3b8' }}>
                                                    {new Date(alert.created_at).toLocaleString()}
                                                </p>
                                            </div>
                                        </div>
                                        {!alert.acknowledged && (
                                            <button
                                                onClick={() => handleAcknowledgeAlert(alert.alert_id)}
                                                style={{
                                                    padding: '6px 12px',
                                                    background: 'white',
                                                    border: '1px solid #e2e8f0',
                                                    borderRadius: '6px',
                                                    color: '#64748b',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                    cursor: 'pointer',
                                                }}
                                            >
                                                ✓ Acknowledge
                                            </button>
                                        )}
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Calibration Modal */}
            {calibrating && (
                <div style={{
                    position: 'fixed',
                    top: 0,
                    left: 0,
                    right: 0,
                    bottom: 0,
                    background: 'rgba(0,0,0,0.5)',
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    zIndex: 1000,
                }}>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '32px',
                        maxWidth: '500px',
                        width: '90%',
                    }}>
                        <h3 style={{ marginBottom: '20px' }}>🔧 Calibration Wizard</h3>

                        {/* Progress */}
                        <div style={{
                            display: 'flex',
                            gap: '8px',
                            marginBottom: '24px',
                        }}>
                            {[1, 2, 3, 4, 5].map(step => (
                                <div
                                    key={step}
                                    style={{
                                        flex: 1,
                                        height: '4px',
                                        borderRadius: '2px',
                                        background: step <= calibrationStep ? '#3b82f6' : '#e2e8f0',
                                    }}
                                />
                            ))}
                        </div>

                        <div style={{ marginBottom: '24px' }}>
                            {calibrationStep === 1 && (
                                <>
                                    <h4>Step 1: Empty Tank Reference</h4>
                                    <p style={{ color: '#64748b' }}>
                                        Ensure your tank is empty. The sensor will take a reference reading.
                                    </p>
                                </>
                            )}
                            {calibrationStep === 2 && (
                                <>
                                    <h4>Step 2: 25% Full</h4>
                                    <p style={{ color: '#64748b' }}>
                                        Fill the tank to 25% capacity and take a reading.
                                    </p>
                                </>
                            )}
                            {calibrationStep === 3 && (
                                <>
                                    <h4>Step 3: 50% Full</h4>
                                    <p style={{ color: '#64748b' }}>
                                        Fill the tank to 50% capacity and take a reading.
                                    </p>
                                </>
                            )}
                            {calibrationStep === 4 && (
                                <>
                                    <h4>Step 4: 75% Full</h4>
                                    <p style={{ color: '#64748b' }}>
                                        Fill the tank to 75% capacity and take a reading.
                                    </p>
                                </>
                            )}
                            {calibrationStep === 5 && (
                                <>
                                    <h4>Step 5: Full Tank Reference</h4>
                                    <p style={{ color: '#64748b' }}>
                                        Fill the tank completely for the final reference reading.
                                    </p>
                                </>
                            )}
                        </div>

                        <div style={{ display: 'flex', gap: '12px' }}>
                            <button
                                onClick={() => { setCalibrating(null); setCalibrationStep(0); }}
                                style={{
                                    flex: 1,
                                    padding: '12px',
                                    background: 'white',
                                    border: '1px solid #e2e8f0',
                                    borderRadius: '10px',
                                    color: '#64748b',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                }}
                            >
                                Cancel
                            </button>
                            <button
                                onClick={handleCalibrationNext}
                                style={{
                                    flex: 2,
                                    padding: '12px',
                                    background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                    border: 'none',
                                    borderRadius: '10px',
                                    color: 'white',
                                    fontWeight: 600,
                                    cursor: 'pointer',
                                }}
                            >
                                {calibrationStep < 5 ? '📸 Take Reading & Next' : '✓ Complete Calibration'}
                            </button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
};

export default IoTDeviceManager;
