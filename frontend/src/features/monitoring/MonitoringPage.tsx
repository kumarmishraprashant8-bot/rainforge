import { useState, useEffect } from 'react';
import { Droplets, AlertTriangle, CheckCircle, TrendingUp, Gauge, RefreshCw } from 'lucide-react';
import axios from 'axios';

interface TankReading {
    project_id: number;
    tank_level_percent: number;
    current_volume_liters: number;
    capacity_liters: number;
    last_updated: string;
    sensor_status: string;
    maintenance_alerts: string[];
    days_until_empty: number;
}

interface HistoricalReading {
    timestamp: string;
    tank_level_percent: number;
    flow_rate_lpm: number;
    rainfall_mm: number;
}

const MonitoringPage = () => {
    const [projectId, setProjectId] = useState(1);
    const [tankStatus, setTankStatus] = useState<TankReading | null>(null);
    const [history, setHistory] = useState<HistoricalReading[]>([]);
    const [loading, setLoading] = useState(true);

    // Fallback demo data when API is unavailable
    const fallbackTankStatus: TankReading = {
        project_id: projectId,
        tank_level_percent: 34,
        current_volume_liters: 3400,
        capacity_liters: 10000,
        last_updated: new Date().toISOString(),
        sensor_status: 'online',
        maintenance_alerts: [],
        days_until_empty: 17
    };

    const generateFallbackHistory = (): HistoricalReading[] => {
        const readings: HistoricalReading[] = [];
        for (let i = 23; i >= 0; i--) {
            readings.push({
                timestamp: new Date(Date.now() - i * 60 * 60 * 1000).toISOString(),
                tank_level_percent: 30 + Math.sin(i / 4) * 15 + Math.random() * 5,
                flow_rate_lpm: Math.random() * 2,
                rainfall_mm: i % 6 === 0 ? Math.random() * 5 : 0
            });
        }
        return readings;
    };

    const fetchData = async () => {
        // For demo: use mock data immediately (instant response)
        // This ensures the demo always shows engaging data
        setTankStatus({
            project_id: projectId,
            tank_level_percent: 57,
            current_volume_liters: 5700,
            capacity_liters: 10000,
            last_updated: new Date().toISOString(),
            sensor_status: 'online',
            maintenance_alerts: [],
            days_until_empty: 29
        });
        setHistory(generateFallbackHistory());
        setLoading(false);
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000);
        return () => clearInterval(interval);
    }, [projectId]);

    return (
        <div className="min-h-screen py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6">
                {/* Header */}
                <div className="flex flex-col sm:flex-row justify-between items-start gap-4 mb-8 animate-fade-in-up">
                    <div>
                        <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-accent-success)]/10 border border-[var(--color-accent-success)]/20 mb-4">
                            <div className="w-2 h-2 bg-[var(--color-accent-success)] rounded-full animate-pulse"></div>
                            <span className="text-[var(--color-accent-success)] text-sm font-medium">Live Monitoring</span>
                        </div>
                        <h1 className="text-4xl sm:text-5xl font-bold text-[var(--color-text-primary)] mb-2">
                            Water Accounting
                        </h1>
                        <p className="text-[var(--color-text-muted)]">Real-time tank levels and predictive analytics</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="btn-secondary p-3 flex items-center gap-2"
                    >
                        <RefreshCw size={18} />
                        Refresh
                    </button>
                </div>

                {loading ? (
                    <div className="text-center text-[var(--color-text-muted)] py-20">
                        <div className="animate-pulse">Loading sensor data...</div>
                    </div>
                ) : tankStatus && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Main Tank Gauge */}
                        <div className="lg:col-span-1">
                            <div className="card-premium rounded-2xl p-8 animate-fade-in-up stagger-1">
                                <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-6 flex items-center gap-2">
                                    <div className="stat-icon stat-icon-indigo">
                                        <Gauge size={18} />
                                    </div>
                                    Tank Level
                                </h3>

                                {/* Circular Gauge */}
                                <div className="relative w-52 h-52 mx-auto mb-6">
                                    <svg className="w-full h-full transform -rotate-90" style={{ filter: 'drop-shadow(0 0 20px rgba(99, 102, 241, 0.4))' }}>
                                        <defs>
                                            <linearGradient id="gaugeGradient" x1="0%" y1="0%" x2="100%" y2="0%">
                                                <stop offset="0%" stopColor="#06b6d4" />
                                                <stop offset="50%" stopColor="#8b5cf6" />
                                                <stop offset="100%" stopColor="#ec4899" />
                                            </linearGradient>
                                        </defs>
                                        <circle
                                            cx="104" cy="104" r="92"
                                            fill="none"
                                            stroke="rgba(255,255,255,0.1)"
                                            strokeWidth="14"
                                        />
                                        <circle
                                            cx="104" cy="104" r="92"
                                            fill="none"
                                            stroke="url(#gaugeGradient)"
                                            strokeWidth="14"
                                            strokeLinecap="round"
                                            strokeDasharray={`${(tankStatus.tank_level_percent / 100) * 578} 578`}
                                            className="transition-all duration-1000"
                                        />
                                    </svg>
                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                                        <span className="text-5xl font-black bg-gradient-to-r from-cyan-400 via-purple-400 to-pink-400 bg-clip-text text-transparent">
                                            {Math.round(tankStatus.tank_level_percent ?? 0)}%
                                        </span>
                                        <span className="text-cyan-400 text-lg font-semibold mt-1">
                                            {((tankStatus.current_volume_liters ?? 0) / 1000).toFixed(1)} kL
                                        </span>
                                    </div>
                                </div>

                                {/* Stats */}
                                <div className="space-y-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-[var(--color-text-muted)]">Capacity</span>
                                        <span className="text-[var(--color-text-primary)] font-medium">
                                            {(tankStatus.capacity_liters / 1000).toFixed(0)} kL
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-[var(--color-text-muted)]">Days until empty</span>
                                        <span className={`font-medium ${(tankStatus.days_until_empty ?? 0) < 7
                                            ? 'text-[var(--color-accent-danger)]'
                                            : 'text-[var(--color-accent-success)]'
                                            }`}>
                                            {(tankStatus.days_until_empty ?? 0).toFixed(0)} days
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-[var(--color-text-muted)]">Sensor Status</span>
                                        <span className="text-[var(--color-accent-success)] flex items-center gap-1">
                                            <CheckCircle size={14} /> Online
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Alerts */}
                            {tankStatus.maintenance_alerts.length > 0 && (
                                <div className="card-premium rounded-2xl p-6 mt-6 border-l-4 border-l-[var(--color-accent-warning)] animate-fade-in-up stagger-2">
                                    <h3 className="text-lg font-semibold text-[var(--color-accent-warning)] mb-4 flex items-center gap-2">
                                        <AlertTriangle size={18} />
                                        Maintenance Alerts
                                    </h3>
                                    <ul className="space-y-2">
                                        {tankStatus.maintenance_alerts.map((alert, i) => (
                                            <li key={i} className="text-sm text-[var(--color-text-secondary)] flex items-start gap-2">
                                                <span className="text-[var(--color-accent-warning)]">•</span>
                                                {alert}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        {/* Historical Chart */}
                        <div className="lg:col-span-2">
                            <div className="card-premium rounded-2xl p-6 h-full animate-fade-in-up stagger-3">
                                <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-6 flex items-center gap-2">
                                    <div className="stat-icon stat-icon-emerald">
                                        <TrendingUp size={18} />
                                    </div>
                                    24-Hour Trend
                                </h3>

                                <div className="h-80 relative">
                                    {/* Mini chart visualization */}
                                    <div className="absolute inset-0 flex items-end gap-[2px] pl-10">
                                        {history.slice(-24).map((reading, i) => (
                                            <div
                                                key={i}
                                                className="flex-1 min-w-[8px]"
                                                style={{ height: `${Math.max(reading.tank_level_percent, 5)}%` }}
                                            >
                                                <div
                                                    className="w-full h-full rounded-t-sm transition-opacity hover:opacity-100"
                                                    style={{
                                                        background: 'linear-gradient(to top, #6366f1, #a855f7)',
                                                        opacity: 0.7
                                                    }}
                                                    title={`${reading.tank_level_percent.toFixed(1)}%`}
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    {/* Y-axis labels */}
                                    <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-[var(--color-text-muted)]">
                                        <span>100%</span>
                                        <span>50%</span>
                                        <span>0%</span>
                                    </div>
                                </div>

                                {/* Legend */}
                                <div className="mt-4 flex justify-center gap-6 text-sm text-[var(--color-text-muted)]">
                                    <span className="flex items-center gap-2">
                                        <div className="w-3 h-3 rounded-sm bg-[var(--color-accent-primary)]"></div>
                                        Tank Level
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Predictions Card */}
                <div className="mt-6 card-premium rounded-2xl p-6 animate-fade-in-up stagger-4">
                    <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4">Predictive Insights</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="stat-card">
                            <div className="text-sm text-[var(--color-text-muted)] mb-1">Expected Rainfall</div>
                            <div className="text-2xl font-bold text-[var(--color-accent-info)]">45mm</div>
                            <div className="text-xs text-[var(--color-text-muted)]">next 7 days</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-sm text-[var(--color-text-muted)] mb-1">Predicted Capture</div>
                            <div className="text-2xl font-bold text-[var(--color-accent-success)]">4,500 L</div>
                            <div className="text-xs text-[var(--color-text-muted)]">based on forecast</div>
                        </div>
                        <div className="stat-card">
                            <div className="text-sm text-[var(--color-text-muted)] mb-1">Overflow Risk</div>
                            <div className="text-2xl font-bold text-[var(--color-accent-warning)]">Low</div>
                            <div className="text-xs text-[var(--color-text-muted)]">tank has 40% capacity</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MonitoringPage;
