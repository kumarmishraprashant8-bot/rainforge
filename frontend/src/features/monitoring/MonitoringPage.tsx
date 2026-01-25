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

    const fetchData = async () => {
        try {
            const [statusRes, historyRes] = await Promise.all([
                axios.get(`http://localhost:8000/api/v1/monitoring/${projectId}/status`),
                axios.get(`http://localhost:8000/api/v1/monitoring/${projectId}/history?hours=24`)
            ]);
            setTankStatus(statusRes.data);
            setHistory(historyRes.data.readings);
        } catch (err) {
            console.error(err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchData();
        const interval = setInterval(fetchData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, [projectId]);

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header */}
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-4">
                            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
                            <span className="text-green-300 text-sm font-medium">Live Monitoring</span>
                        </div>
                        <h1 className="text-5xl font-black text-white mb-2">Water Accounting</h1>
                        <p className="text-gray-400">Real-time tank levels and predictive analytics</p>
                    </div>
                    <button
                        onClick={fetchData}
                        className="p-3 bg-white/10 hover:bg-white/20 rounded-xl text-white"
                    >
                        <RefreshCw size={20} />
                    </button>
                </div>

                {loading ? (
                    <div className="text-center text-gray-400 py-20">Loading sensor data...</div>
                ) : tankStatus && (
                    <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
                        {/* Main Tank Gauge */}
                        <div className="lg:col-span-1">
                            <div className="glass rounded-2xl p-8">
                                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                    <Gauge className="text-cyan-400" size={24} />
                                    Tank Level
                                </h3>

                                {/* Circular Gauge */}
                                <div className="relative w-48 h-48 mx-auto mb-6">
                                    <svg className="w-full h-full transform -rotate-90">
                                        <circle
                                            cx="96" cy="96" r="88"
                                            fill="none"
                                            stroke="rgba(255,255,255,0.1)"
                                            strokeWidth="16"
                                        />
                                        <circle
                                            cx="96" cy="96" r="88"
                                            fill="none"
                                            stroke={tankStatus.tank_level_percent > 20 ? "#06b6d4" : "#ef4444"}
                                            strokeWidth="16"
                                            strokeLinecap="round"
                                            strokeDasharray={`${(tankStatus.tank_level_percent / 100) * 553} 553`}
                                        />
                                    </svg>
                                    <div className="absolute inset-0 flex flex-col items-center justify-center">
                                        <span className="text-5xl font-black text-white">
                                            {Math.round(tankStatus.tank_level_percent)}%
                                        </span>
                                        <span className="text-gray-400 text-sm">
                                            {(tankStatus.current_volume_liters / 1000).toFixed(1)} kL
                                        </span>
                                    </div>
                                </div>

                                {/* Stats */}
                                <div className="space-y-4">
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Capacity</span>
                                        <span className="text-white font-semibold">
                                            {(tankStatus.capacity_liters / 1000).toFixed(0)} kL
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Days until empty</span>
                                        <span className={`font-semibold ${tankStatus.days_until_empty < 7 ? 'text-red-400' : 'text-green-400'
                                            }`}>
                                            {tankStatus.days_until_empty.toFixed(0)} days
                                        </span>
                                    </div>
                                    <div className="flex justify-between text-sm">
                                        <span className="text-gray-400">Sensor Status</span>
                                        <span className="text-green-400 flex items-center gap-1">
                                            <CheckCircle size={14} /> Online
                                        </span>
                                    </div>
                                </div>
                            </div>

                            {/* Alerts */}
                            {tankStatus.maintenance_alerts.length > 0 && (
                                <div className="glass rounded-2xl p-6 mt-6 border border-yellow-500/20">
                                    <h3 className="text-lg font-bold text-yellow-400 mb-4 flex items-center gap-2">
                                        <AlertTriangle size={20} />
                                        Maintenance Alerts
                                    </h3>
                                    <ul className="space-y-2">
                                        {tankStatus.maintenance_alerts.map((alert, i) => (
                                            <li key={i} className="text-sm text-gray-300 flex items-start gap-2">
                                                <span className="text-yellow-500">•</span>
                                                {alert}
                                            </li>
                                        ))}
                                    </ul>
                                </div>
                            )}
                        </div>

                        {/* Historical Chart */}
                        <div className="lg:col-span-2">
                            <div className="glass rounded-2xl p-6 h-full">
                                <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                                    <TrendingUp className="text-cyan-400" size={24} />
                                    24-Hour Trend
                                </h3>

                                <div className="h-80 relative">
                                    {/* Mini chart visualization */}
                                    <div className="absolute inset-0 flex items-end">
                                        {history.slice(-24).map((reading, i) => (
                                            <div
                                                key={i}
                                                className="flex-1 mx-px"
                                                style={{ height: `${reading.tank_level_percent}%` }}
                                            >
                                                <div
                                                    className="w-full h-full bg-gradient-to-t from-cyan-500 to-blue-500 rounded-t opacity-75 hover:opacity-100 transition-opacity"
                                                    title={`${reading.tank_level_percent.toFixed(1)}%`}
                                                />
                                            </div>
                                        ))}
                                    </div>

                                    {/* Y-axis labels */}
                                    <div className="absolute left-0 top-0 h-full flex flex-col justify-between text-xs text-gray-500">
                                        <span>100%</span>
                                        <span>50%</span>
                                        <span>0%</span>
                                    </div>
                                </div>

                                {/* Legend */}
                                <div className="mt-4 flex justify-center gap-6 text-sm text-gray-400">
                                    <span className="flex items-center gap-2">
                                        <div className="w-3 h-3 bg-cyan-500 rounded"></div>
                                        Tank Level
                                    </span>
                                </div>
                            </div>
                        </div>
                    </div>
                )}

                {/* Predictions Card */}
                <div className="mt-6 glass rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4">Predictive Insights</h3>
                    <div className="grid md:grid-cols-3 gap-4">
                        <div className="bg-white/5 rounded-xl p-4">
                            <div className="text-sm text-gray-400 mb-1">Expected Rainfall</div>
                            <div className="text-2xl font-bold text-cyan-400">45mm</div>
                            <div className="text-xs text-gray-500">next 7 days</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4">
                            <div className="text-sm text-gray-400 mb-1">Predicted Capture</div>
                            <div className="text-2xl font-bold text-green-400">4,500 L</div>
                            <div className="text-xs text-gray-500">based on forecast</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4">
                            <div className="text-sm text-gray-400 mb-1">Next Overflow Risk</div>
                            <div className="text-2xl font-bold text-yellow-400">Low</div>
                            <div className="text-xs text-gray-500">tank has 40% capacity</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MonitoringPage;
