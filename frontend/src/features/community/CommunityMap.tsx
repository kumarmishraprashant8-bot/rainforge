import { useState, useEffect } from 'react';
import './CommunityMap.css';

interface NearbySystem {
    system_id: string;
    owner: string;
    address: string;
    distance_km: number;
    availability: 'surplus' | 'balanced' | 'deficit' | 'critical';
    level_pct: number;
    available_liters: number;
}

interface CommunityStats {
    total_systems: number;
    systems_with_surplus: number;
    systems_in_deficit: number;
    total_capacity_liters: number;
    community_fill_percent: number;
    last_30_days: {
        sharing_events: number;
        total_liters_shared: number;
    };
}

export default function CommunityMap() {
    const [systems, setSystems] = useState<NearbySystem[]>([]);
    const [stats, setStats] = useState<CommunityStats | null>(null);
    const [selectedSystem, setSelectedSystem] = useState<NearbySystem | null>(null);
    const [showRequest, setShowRequest] = useState(false);
    const [requestLiters, setRequestLiters] = useState(500);
    const [loading, setLoading] = useState(true);
    const [viewMode, setViewMode] = useState<'list' | 'map'>('list');

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        // Mock data - replace with actual API calls
        setTimeout(() => {
            setSystems([
                { system_id: 'sys_1', owner: 'Sharma Residence', address: '123 Green Park', distance_km: 0.3, availability: 'surplus', level_pct: 85, available_liters: 2000 },
                { system_id: 'sys_2', owner: 'Patel Family', address: '45 Lake View', distance_km: 0.5, availability: 'surplus', level_pct: 78, available_liters: 1500 },
                { system_id: 'sys_3', owner: 'Khan House', address: '78 Main Street', distance_km: 0.8, availability: 'balanced', level_pct: 55, available_liters: 500 },
                { system_id: 'sys_4', owner: 'Gupta Villa', address: '22 Hill Road', distance_km: 1.2, availability: 'deficit', level_pct: 25, available_liters: 0 },
                { system_id: 'sys_5', owner: 'Singh Complex', address: '99 Park Lane', distance_km: 1.5, availability: 'surplus', level_pct: 92, available_liters: 3500 },
            ]);
            setStats({
                total_systems: 47,
                systems_with_surplus: 18,
                systems_in_deficit: 12,
                total_capacity_liters: 235000,
                community_fill_percent: 62,
                last_30_days: { sharing_events: 23, total_liters_shared: 15600 }
            });
            setLoading(false);
        }, 500);
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'surplus': return '#22c55e';
            case 'balanced': return '#f59e0b';
            case 'deficit': return '#ef4444';
            case 'critical': return '#dc2626';
            default: return '#6b7280';
        }
    };

    const getStatusIcon = (status: string) => {
        switch (status) {
            case 'surplus': return '💧';
            case 'balanced': return '⚖️';
            case 'deficit': return '🏜️';
            case 'critical': return '🚨';
            default: return '❓';
        }
    };

    const handleRequestWater = (system: NearbySystem) => {
        setSelectedSystem(system);
        setShowRequest(true);
    };

    const submitRequest = () => {
        if (!selectedSystem) return;
        alert(`Request sent to ${selectedSystem.owner} for ${requestLiters} liters!`);
        setShowRequest(false);
        setSelectedSystem(null);
    };

    if (loading) {
        return (
            <div className="community-loading">
                <div className="spinner"></div>
                <p>Finding nearby water systems...</p>
            </div>
        );
    }

    return (
        <div className="community-map">
            <header className="community-header">
                <h2>🏘️ Community Water Sharing</h2>
                <p>Connect with neighbors for water sharing</p>
            </header>

            {stats && (
                <div className="community-stats">
                    <div className="stat">
                        <span className="stat-value">{stats.total_systems}</span>
                        <span className="stat-label">Systems Nearby</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{stats.systems_with_surplus}</span>
                        <span className="stat-label">With Surplus</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{stats.community_fill_percent}%</span>
                        <span className="stat-label">Avg Fill</span>
                    </div>
                    <div className="stat">
                        <span className="stat-value">{(stats.last_30_days.total_liters_shared / 1000).toFixed(1)}kL</span>
                        <span className="stat-label">Shared (30d)</span>
                    </div>
                </div>
            )}

            <div className="view-toggle">
                <button className={viewMode === 'list' ? 'active' : ''} onClick={() => setViewMode('list')}>📋 List</button>
                <button className={viewMode === 'map' ? 'active' : ''} onClick={() => setViewMode('map')}>🗺️ Map</button>
            </div>

            {viewMode === 'list' ? (
                <div className="systems-list">
                    {systems.map(system => (
                        <div key={system.system_id} className="system-card">
                            <div className="system-header">
                                <span className="system-icon">{getStatusIcon(system.availability)}</span>
                                <div className="system-info">
                                    <h3>{system.owner}</h3>
                                    <p>{system.address}</p>
                                </div>
                                <span className="system-distance">{system.distance_km} km</span>
                            </div>

                            <div className="system-level">
                                <div className="level-bar">
                                    <div
                                        className="level-fill"
                                        style={{ width: `${system.level_pct}%`, backgroundColor: getStatusColor(system.availability) }}
                                    />
                                </div>
                                <span className="level-text">{system.level_pct}% full</span>
                            </div>

                            <div className="system-footer">
                                <span className={`badge ${system.availability}`}>
                                    {system.availability === 'surplus' && `${system.available_liters}L available`}
                                    {system.availability === 'balanced' && 'Balanced'}
                                    {system.availability === 'deficit' && 'Needs water'}
                                    {system.availability === 'critical' && 'Critical'}
                                </span>
                                {system.availability === 'surplus' && (
                                    <button className="request-btn" onClick={() => handleRequestWater(system)}>
                                        Request Water
                                    </button>
                                )}
                            </div>
                        </div>
                    ))}
                </div>
            ) : (
                <div className="map-view">
                    <div className="map-placeholder">
                        <p>🗺️ Map View</p>
                        <span>Integrate with Mapbox/Google Maps to show system locations</span>
                    </div>
                </div>
            )}

            {showRequest && selectedSystem && (
                <div className="modal-overlay" onClick={() => setShowRequest(false)}>
                    <div className="modal" onClick={e => e.stopPropagation()}>
                        <h3>Request Water</h3>
                        <p>From: <strong>{selectedSystem.owner}</strong></p>
                        <p>Available: <strong>{selectedSystem.available_liters} liters</strong></p>

                        <div className="form-group">
                            <label>Amount to request (liters)</label>
                            <input
                                type="range"
                                min={100}
                                max={selectedSystem.available_liters}
                                step={100}
                                value={requestLiters}
                                onChange={e => setRequestLiters(parseInt(e.target.value))}
                            />
                            <span className="amount">{requestLiters} L</span>
                        </div>

                        <div className="modal-actions">
                            <button className="cancel" onClick={() => setShowRequest(false)}>Cancel</button>
                            <button className="submit" onClick={submitRequest}>Send Request</button>
                        </div>
                    </div>
                </div>
            )}
        </div>
    );
}
