import { useState, useEffect } from 'react';
import {
    Globe, Droplets, Building2, Leaf, Users, Download,
    TrendingUp, MapPin, BarChart3, Trophy, Medal
} from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, Cell } from 'recharts';

interface WardStat {
    ward_id: string;
    ward_name: string;
    systems: number;
    captured: number;
}

interface CityStats {
    city: string;
    total_wards: number;
    total_systems: number;
    active_systems: number;
    total_captured_liters: number;
    total_captured_display: string;
    co2_avoided_kg: number;
    funds_spent_inr: number;
    funds_spent_display: string;
    beneficiaries: number;
    wards: WardStat[];
}

interface LeaderboardWard {
    ward_id: string;
    ward_name: string;
    systems: number;
    captured: number;
    rank: number;
}

const PublicDashboard = () => {
    const [stats, setStats] = useState<CityStats | null>(null);
    const [leaderboard, setLeaderboard] = useState<LeaderboardWard[]>([]);
    const [selectedWard, setSelectedWard] = useState<string | null>(null);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchStats();
    }, []);

    useEffect(() => {
        const api = import.meta.env.VITE_API_URL || 'http://localhost:8000';
        fetch(`${api}/api/v1/success/leaderboard`)
            .then((res) => res.json())
            .then((data) => setLeaderboard(data?.wards || []))
            .catch(() => setLeaderboard([]));
    }, []);

    const fetchStats = async () => {
        // Use mock data immediately for demo
        setStats({
            city: "New Delhi",
            total_wards: 5,
            total_systems: 226,
            active_systems: 208,
            total_captured_liters: 12700000,
            total_captured_display: "12.7M L",
            co2_avoided_kg: 8890,
            funds_spent_inr: 22600000,
            funds_spent_display: "₹226L",
            beneficiaries: 904,
            wards: [
                { ward_id: "W001", ward_name: "Connaught Place", systems: 45, captured: 2500000 },
                { ward_id: "W002", ward_name: "Karol Bagh", systems: 32, captured: 1800000 },
                { ward_id: "W003", ward_name: "Rohini Sector 5", systems: 67, captured: 3800000 },
                { ward_id: "W004", ward_name: "Dwarka Sector 12", systems: 54, captured: 3100000 },
                { ward_id: "W005", ward_name: "Lajpat Nagar", systems: 28, captured: 1500000 },
            ]
        });
        setLoading(false);
    };

    const exportData = async (format: string) => {
        if (format === 'csv') {
            const content = `ward_id,ward_name,systems,captured_liters
W001,Connaught Place,45,2500000
W002,Karol Bagh,32,1800000
W003,Rohini Sector 5,67,3800000
W004,Dwarka Sector 12,54,3100000
W005,Lajpat Nagar,28,1500000`;
            const blob = new Blob([content], { type: 'text/csv' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'rainforge_city_data.csv';
            a.click();
        } else {
            const blob = new Blob([JSON.stringify(stats, null, 2)], { type: 'application/json' });
            const url = URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = 'rainforge_city_data.json';
            a.click();
        }
    };

    const colors = ['#06b6d4', '#10b981', '#8b5cf6', '#f59e0b', '#ef4444'];

    if (loading) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
                <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-cyan-400"></div>
            </div>
        );
    }

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                {/* Header */}
                <div className="text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-4">
                        <Globe className="text-green-400" size={16} />
                        <span className="text-green-300 text-sm font-medium">Public Transparency Dashboard</span>
                    </div>
                    <h1 className="text-4xl font-black text-white mb-2">
                        {stats?.city} Rainwater Harvesting
                    </h1>
                    <p className="text-gray-400">Real-time impact metrics • Last updated: Today</p>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                    <div className="glass rounded-2xl p-6 text-center">
                        <Droplets className="mx-auto text-cyan-400 mb-2" size={32} />
                        <div className="text-3xl font-black text-white">{stats?.total_captured_display}</div>
                        <div className="text-sm text-gray-400">Water Captured</div>
                    </div>
                    <div className="glass rounded-2xl p-6 text-center">
                        <Building2 className="mx-auto text-purple-400 mb-2" size={32} />
                        <div className="text-3xl font-black text-white">{stats?.total_systems}</div>
                        <div className="text-sm text-gray-400">Active Systems</div>
                    </div>
                    <div className="glass rounded-2xl p-6 text-center">
                        <Leaf className="mx-auto text-green-400 mb-2" size={32} />
                        <div className="text-3xl font-black text-white">{stats?.co2_avoided_kg.toLocaleString()} kg</div>
                        <div className="text-sm text-gray-400">CO₂ Avoided</div>
                    </div>
                    <div className="glass rounded-2xl p-6 text-center">
                        <Users className="mx-auto text-yellow-400 mb-2" size={32} />
                        <div className="text-3xl font-black text-white">{stats?.beneficiaries}</div>
                        <div className="text-sm text-gray-400">Beneficiaries</div>
                    </div>
                </div>

                {/* Leaderboard - Top wards (grand success / gamification) */}
                {leaderboard.length > 0 && (
                    <div className="glass rounded-2xl p-6 border border-amber-500/20">
                        <h2 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                            <Trophy className="text-amber-400" size={24} />
                            Ward Leaderboard
                        </h2>
                        <p className="text-gray-400 text-sm mb-4">Top wards by RWH adoption and water captured</p>
                        <div className="space-y-2">
                            {leaderboard.map((w) => (
                                <div
                                    key={w.ward_id}
                                    className="flex items-center gap-4 p-3 rounded-xl bg-white/5 hover:bg-white/10 transition-colors"
                                >
                                    <div className="w-10 h-10 rounded-full flex items-center justify-center font-black text-white bg-gradient-to-br from-amber-500 to-orange-600">
                                        {w.rank === 1 && <Medal size={20} />}
                                        {w.rank !== 1 && w.rank}
                                    </div>
                                    <div className="flex-1 min-w-0">
                                        <div className="font-semibold text-white truncate">{w.ward_name}</div>
                                        <div className="text-xs text-gray-400">{w.systems} systems • {(w.captured / 1e6).toFixed(1)}M L captured</div>
                                    </div>
                                    <span className="text-amber-400 font-bold">#{w.rank}</span>
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Ward Breakdown Chart */}
                <div className="glass rounded-2xl p-6">
                    <div className="flex items-center justify-between mb-6">
                        <h2 className="text-xl font-bold text-white flex items-center gap-2">
                            <BarChart3 className="text-cyan-400" size={24} />
                            Ward-wise Water Capture
                        </h2>
                        <div className="flex gap-2">
                            <button
                                onClick={() => exportData('csv')}
                                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm"
                            >
                                <Download size={16} />
                                CSV
                            </button>
                            <button
                                onClick={() => exportData('json')}
                                className="flex items-center gap-2 px-4 py-2 bg-white/10 hover:bg-white/20 text-white rounded-lg text-sm"
                            >
                                <Download size={16} />
                                GeoJSON
                            </button>
                        </div>
                    </div>

                    <div className="h-80">
                        <ResponsiveContainer width="100%" height="100%">
                            <BarChart data={stats?.wards} layout="vertical">
                                <XAxis type="number" stroke="#94a3b8" tickFormatter={(v) => `${(v / 1000000).toFixed(1)}M`} />
                                <YAxis dataKey="ward_name" type="category" stroke="#94a3b8" width={120} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    formatter={(value: any) => [`${(Number(value) / 1000000).toFixed(2)}M liters`, 'Captured']}
                                />
                                <Bar dataKey="captured" radius={[0, 8, 8, 0]}>
                                    {stats?.wards.map((_, index) => (
                                        <Cell key={`cell-${index}`} fill={colors[index % colors.length]} />
                                    ))}
                                </Bar>
                            </BarChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                {/* Ward Cards */}
                <div className="grid md:grid-cols-3 lg:grid-cols-5 gap-4">
                    {stats?.wards.map((ward, idx) => (
                        <div
                            key={ward.ward_id}
                            className="glass rounded-xl p-4 hover:scale-105 transition-transform cursor-pointer"
                            onClick={() => setSelectedWard(ward.ward_id)}
                        >
                            <div className="flex items-center gap-2 mb-2">
                                <MapPin className="text-gray-400" size={16} />
                                <span className="text-sm text-gray-400">{ward.ward_id}</span>
                            </div>
                            <div className="font-semibold text-white mb-1">{ward.ward_name}</div>
                            <div className="text-2xl font-black" style={{ color: colors[idx] }}>
                                {ward.systems}
                            </div>
                            <div className="text-xs text-gray-400">systems installed</div>
                        </div>
                    ))}
                </div>

                {/* Investment Summary */}
                <div className="glass rounded-2xl p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10">
                    <h3 className="text-xl font-bold text-white mb-4">Investment Impact</h3>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div>
                            <div className="text-sm text-gray-400 mb-1">Total Investment</div>
                            <div className="text-3xl font-black text-white">{stats?.funds_spent_display}</div>
                        </div>
                        <div>
                            <div className="text-sm text-gray-400 mb-1">Cost per Liter Captured</div>
                            <div className="text-3xl font-black text-green-400">
                                ₹{stats ? (stats.funds_spent_inr / stats.total_captured_liters).toFixed(2) : '0'}
                            </div>
                        </div>
                        <div>
                            <div className="text-sm text-gray-400 mb-1">Cost per Beneficiary</div>
                            <div className="text-3xl font-black text-cyan-400">
                                ₹{stats ? Math.round(stats.funds_spent_inr / stats.beneficiaries).toLocaleString() : '0'}
                            </div>
                        </div>
                    </div>
                </div>

                {/* Footer */}
                <div className="text-center text-sm text-gray-500">
                    Powered by RainForge • Jal Shakti Abhiyan Aligned • Data updated daily
                </div>
            </div>
        </div>
    );
};

export default PublicDashboard;
