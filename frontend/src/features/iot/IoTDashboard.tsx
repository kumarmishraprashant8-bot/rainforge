/**
 * IoT Dashboard Page
 * Live tank monitoring with charts and alerts
 */

import { useState, useEffect } from 'react';
import {
    Droplets, Thermometer, Zap, Bell, Settings, Plus,
    TrendingUp, TrendingDown, AlertTriangle, CheckCircle,
    Wifi, WifiOff, RefreshCw, BarChart3
} from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    LineChart, Line
} from 'recharts';

interface TankData {
    id: string;
    name: string;
    capacity_liters: number;
    current_level_liters: number;
    current_level_percent: number;
    temperature: number;
    ph_level: number;
    last_updated: string;
    status: 'online' | 'offline';
    alerts: { type: string; message: string }[];
}

interface UsageHistory {
    time: string;
    level: number;
    inflow: number;
    outflow: number;
}

const IoTDashboard = () => {
    const [tanks, setTanks] = useState<TankData[]>([]);
    const [selectedTank, setSelectedTank] = useState<string | null>(null);
    const [usageHistory, setUsageHistory] = useState<UsageHistory[]>([]);
    const [timeRange, setTimeRange] = useState<'24h' | '7d' | '30d'>('24h');
    const [loading, setLoading] = useState(true);

    // Generate demo data
    useEffect(() => {
        const demoTanks: TankData[] = [
            {
                id: 'tank_001',
                name: 'Main Rooftop Tank',
                capacity_liters: 17000,
                current_level_liters: 12580,
                current_level_percent: 74,
                temperature: 26,
                ph_level: 7.2,
                last_updated: new Date().toISOString(),
                status: 'online',
                alerts: []
            },
            {
                id: 'tank_002',
                name: 'Ground Storage',
                capacity_liters: 10000,
                current_level_liters: 3200,
                current_level_percent: 32,
                temperature: 24,
                ph_level: 7.0,
                last_updated: new Date().toISOString(),
                status: 'online',
                alerts: [{ type: 'warning', message: 'Low water level' }]
            }
        ];
        setTanks(demoTanks);
        setSelectedTank(demoTanks[0].id);

        // Generate usage history
        const history: UsageHistory[] = [];
        for (let i = 23; i >= 0; i--) {
            const hour = new Date();
            hour.setHours(hour.getHours() - i);
            history.push({
                time: hour.toLocaleTimeString('en-US', { hour: '2-digit' }),
                level: 60 + Math.random() * 30,
                inflow: Math.random() > 0.7 ? Math.floor(Math.random() * 500) : 0,
                outflow: 20 + Math.floor(Math.random() * 80)
            });
        }
        setUsageHistory(history);
        setLoading(false);
    }, []);

    const activeTank = tanks.find(t => t.id === selectedTank);

    const getLevelColor = (percent: number) => {
        if (percent > 70) return 'text-green-400';
        if (percent > 30) return 'text-yellow-400';
        return 'text-red-400';
    };

    const getLevelBgColor = (percent: number) => {
        if (percent > 70) return 'from-green-500 to-emerald-500';
        if (percent > 30) return 'from-yellow-500 to-orange-500';
        return 'from-red-500 to-pink-500';
    };

    const handleAddDevice = () => {
        const newId = `tank_00${tanks.length + 1}`;
        const newTank: TankData = {
            id: newId,
            name: `New Tank ${tanks.length + 1}`,
            capacity_liters: 5000 + Math.floor(Math.random() * 15000),
            current_level_liters: 2500,
            current_level_percent: 50,
            temperature: 25,
            ph_level: 7.0,
            last_updated: new Date().toISOString(),
            status: 'online',
            alerts: []
        };
        setTanks([...tanks, newTank]);
        setSelectedTank(newId);
    };

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400" />
            </div>
        );
    }

    const updateTankStats = (id: string, updates: Partial<TankData>) => {
        setTanks(tanks.map(t => {
            if (t.id === id) {
                const updated = { ...t, ...updates };
                // Recalculate liters if percent changes
                if (updates.current_level_percent !== undefined) {
                    updated.current_level_liters = Math.round((updated.current_level_percent / 100) * updated.capacity_liters);
                }
                return updated;
            }
            return t;
        }));
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="flex justify-between items-center">
                    <div>
                        <h1 className="text-3xl font-black text-white flex items-center gap-3">
                            <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl">
                                <Zap className="text-white" size={28} />
                            </div>
                            IoT Dashboard
                        </h1>
                        <p className="text-gray-400 mt-1">Real-time tank monitoring</p>
                    </div>
                    <div className="flex gap-3">
                        <button className="p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                            <RefreshCw className="text-gray-400" size={20} />
                        </button>
                        <button className="p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                            <Bell className="text-gray-400" size={20} />
                        </button>
                        <button
                            onClick={handleAddDevice}
                            className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity"
                        >
                            <Plus size={18} /> Add Device
                        </button>
                    </div>
                </div>

                {/* Tank Selector */}
                <div className="flex gap-4 overflow-x-auto pb-2">
                    {tanks.map(tank => (
                        <button
                            key={tank.id}
                            onClick={() => setSelectedTank(tank.id)}
                            className={`flex-shrink-0 p-4 rounded-2xl transition-all ${selectedTank === tank.id
                                ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border-2 border-cyan-500'
                                : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                                }`}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`w-3 h-3 rounded-full ${tank.status === 'online' ? 'bg-green-400' : 'bg-red-400'}`} />
                                <span className="text-white font-semibold">{tank.name}</span>
                                <span className={`font-bold ${getLevelColor(tank.current_level_percent)}`}>
                                    {tank.current_level_percent}%
                                </span>
                            </div>
                        </button>
                    ))}
                </div>

                {activeTank && (
                    <>
                        {/* Simulation Controls */}
                        <div className="glass rounded-2xl p-6 mb-6">
                            <div className="flex items-center gap-2 mb-4 text-cyan-400">
                                <Settings size={20} />
                                <span className="font-bold">Simulation Controls</span>
                            </div>
                            <div className="grid md:grid-cols-3 gap-6">
                                <div>
                                    <label className="text-gray-400 text-sm mb-2 block">Water Level ({activeTank.current_level_percent}%)</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="100"
                                        value={activeTank.current_level_percent}
                                        onChange={(e) => updateTankStats(activeTank.id, { current_level_percent: parseInt(e.target.value) })}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-cyan-500"
                                    />
                                </div>
                                <div>
                                    <label className="text-gray-400 text-sm mb-2 block">Temperature ({activeTank.temperature}°C)</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="50"
                                        value={activeTank.temperature}
                                        onChange={(e) => updateTankStats(activeTank.id, { temperature: parseInt(e.target.value) })}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-orange-500"
                                    />
                                </div>
                                <div>
                                    <label className="text-gray-400 text-sm mb-2 block">pH Level ({activeTank.ph_level})</label>
                                    <input
                                        type="range"
                                        min="0"
                                        max="14"
                                        step="0.1"
                                        value={activeTank.ph_level}
                                        onChange={(e) => updateTankStats(activeTank.id, { ph_level: parseFloat(e.target.value) })}
                                        className="w-full h-2 bg-gray-700 rounded-lg appearance-none cursor-pointer accent-green-500"
                                    />
                                </div>
                            </div>
                        </div>
                        {/* Main Stats */}
                        <div className="grid lg:grid-cols-4 gap-4">
                            {/* Tank Level Visualization */}
                            <div className="lg:col-span-1 glass rounded-2xl p-6 flex flex-col items-center justify-center">
                                <div className="relative w-32 h-48 bg-white/5 rounded-2xl border-4 border-white/20 overflow-hidden">
                                    {/* Water Level */}
                                    <div
                                        className={`absolute bottom-0 left-0 right-0 bg-gradient-to-t ${getLevelBgColor(activeTank.current_level_percent)} transition-all duration-1000`}
                                        style={{ height: `${activeTank.current_level_percent}%` }}
                                    >
                                        {/* Wave animation */}
                                        <div className="absolute top-0 left-0 right-0 h-4 bg-white/20 animate-pulse" />
                                    </div>
                                    {/* Level Text */}
                                    <div className="absolute inset-0 flex items-center justify-center">
                                        <span className="text-4xl font-black text-white drop-shadow-lg">
                                            {activeTank.current_level_percent}%
                                        </span>
                                    </div>
                                </div>
                                <div className="mt-4 text-center">
                                    <div className="text-white font-semibold">{activeTank.current_level_liters.toLocaleString()} L</div>
                                    <div className="text-gray-500 text-sm">of {activeTank.capacity_liters.toLocaleString()} L</div>
                                </div>
                            </div>

                            {/* Stats Grid */}
                            <div className="lg:col-span-3 grid grid-cols-2 lg:grid-cols-4 gap-4">
                                <div className="glass rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
                                        <Droplets size={16} /> Current Level
                                    </div>
                                    <div className={`text-2xl font-bold ${getLevelColor(activeTank.current_level_percent)}`}>
                                        {activeTank.current_level_liters.toLocaleString()} L
                                    </div>
                                </div>
                                <div className="glass rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
                                        <Thermometer size={16} /> Temperature
                                    </div>
                                    <div className="text-2xl font-bold text-white">
                                        {activeTank.temperature}°C
                                    </div>
                                </div>
                                <div className="glass rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
                                        <BarChart3 size={16} /> pH Level
                                    </div>
                                    <div className="text-2xl font-bold text-green-400">
                                        {activeTank.ph_level}
                                    </div>
                                </div>
                                <div className="glass rounded-xl p-4">
                                    <div className="flex items-center gap-2 text-gray-400 text-sm mb-2">
                                        {activeTank.status === 'online' ? <Wifi size={16} /> : <WifiOff size={16} />}
                                        Status
                                    </div>
                                    <div className={`text-2xl font-bold ${activeTank.status === 'online' ? 'text-green-400' : 'text-red-400'}`}>
                                        {activeTank.status === 'online' ? 'Online' : 'Offline'}
                                    </div>
                                </div>
                            </div>
                        </div>

                        {/* Alerts */}
                        {activeTank.alerts.length > 0 && (
                            <div className="glass rounded-2xl p-4 bg-yellow-500/10 border border-yellow-500/30">
                                <div className="flex items-center gap-3">
                                    <AlertTriangle className="text-yellow-400" size={24} />
                                    <div>
                                        <p className="text-white font-semibold">Active Alerts</p>
                                        {activeTank.alerts.map((alert, idx) => (
                                            <p key={idx} className="text-yellow-400 text-sm">{alert.message}</p>
                                        ))}
                                    </div>
                                </div>
                            </div>
                        )}

                        {/* Charts */}
                        <div className="glass rounded-2xl p-6">
                            <div className="flex justify-between items-center mb-6">
                                <h3 className="text-lg font-bold text-white">Water Level History</h3>
                                <div className="flex gap-2">
                                    {(['24h', '7d', '30d'] as const).map(range => (
                                        <button
                                            key={range}
                                            onClick={() => setTimeRange(range)}
                                            className={`px-3 py-1 rounded-lg text-sm font-medium transition-all ${timeRange === range
                                                ? 'bg-cyan-500 text-white'
                                                : 'bg-white/5 text-gray-400 hover:text-white'
                                                }`}
                                        >
                                            {range}
                                        </button>
                                    ))}
                                </div>
                            </div>
                            <div className="h-64">
                                <ResponsiveContainer width="100%" height="100%">
                                    <AreaChart data={usageHistory}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                                        <YAxis stroke="#94a3b8" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        />
                                        <Area
                                            type="monotone"
                                            dataKey="level"
                                            stroke="#06b6d4"
                                            fill="url(#colorLevel)"
                                            name="Level %"
                                        />
                                        <defs>
                                            <linearGradient id="colorLevel" x1="0" y1="0" x2="0" y2="1">
                                                <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.5} />
                                                <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.05} />
                                            </linearGradient>
                                        </defs>
                                    </AreaChart>
                                </ResponsiveContainer>
                            </div>
                        </div>

                        {/* Inflow/Outflow Chart */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-6">Water Flow</h3>
                            <div className="h-48">
                                <ResponsiveContainer width="100%" height="100%">
                                    <LineChart data={usageHistory}>
                                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                        <XAxis dataKey="time" stroke="#94a3b8" fontSize={12} />
                                        <YAxis stroke="#94a3b8" fontSize={12} />
                                        <Tooltip
                                            contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        />
                                        <Line type="monotone" dataKey="inflow" stroke="#10b981" strokeWidth={2} name="Inflow (L)" dot={false} />
                                        <Line type="monotone" dataKey="outflow" stroke="#f59e0b" strokeWidth={2} name="Outflow (L)" dot={false} />
                                    </LineChart>
                                </ResponsiveContainer>
                            </div>
                            <div className="flex justify-center gap-8 mt-4">
                                <div className="flex items-center gap-2">
                                    <TrendingUp className="text-green-400" size={16} />
                                    <span className="text-gray-400 text-sm">Inflow (Rain collection)</span>
                                </div>
                                <div className="flex items-center gap-2">
                                    <TrendingDown className="text-yellow-400" size={16} />
                                    <span className="text-gray-400 text-sm">Outflow (Usage)</span>
                                </div>
                            </div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default IoTDashboard;
