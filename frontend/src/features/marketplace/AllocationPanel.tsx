import { useState, useEffect } from 'react';
import {
    Users, Zap, Scale, Target, Settings, ChevronDown, ChevronUp,
    Award, Star, MapPin, CheckCircle, AlertTriangle
} from 'lucide-react';
import API_BASE_URL from '../../config/api';

interface Installer {
    id: number;
    name: string;
    company: string;
    rpi_score: number;
    rpi_grade: string;
    badge_color: string;
    capacity_available: number;
    sla_compliance_pct: number;
}

interface AllocationResult {
    job_id: number;
    recommended_installer: {
        id: number;
        name: string;
        score: number;
    };
    score_breakdown: Record<string, number>;
    alternatives: Array<{
        installer_id: number;
        installer_name: string;
        score: number;
        rank: number;
    }>;
    reason: string;
}

const AllocationPanel = () => {
    const [mode, setMode] = useState<'user_choice' | 'gov_optimized' | 'equitable'>('gov_optimized');
    const [showWeights, setShowWeights] = useState(false);
    const [weights, setWeights] = useState({
        capacity: 0.20,
        rpi: 0.30,
        cost_band: 0.20,
        distance: 0.15,
        sla_history: 0.15
    });
    const [installers, setInstallers] = useState<Installer[]>([]);
    const [result, setResult] = useState<AllocationResult | null>(null);
    const [loading, setLoading] = useState(false);

    useEffect(() => {
        fetchInstallers();
    }, []);

    const fetchInstallers = async () => {
        // Use mock data directly for demo reliability
        const mockInstallers = [
            { id: 1, name: 'Jal Mitra Solutions', company: 'Jal Mitra', rpi_score: 92, rpi_grade: 'A+', badge_color: '#10b981', capacity_available: 8, sla_compliance_pct: 95 },
            { id: 2, name: 'AquaSave India', company: 'AquaSave', rpi_score: 85, rpi_grade: 'A', badge_color: '#22c55e', capacity_available: 5, sla_compliance_pct: 88 },
            { id: 3, name: 'BlueDrop Tech', company: 'BlueDrop', rpi_score: 95, rpi_grade: 'A+', badge_color: '#10b981', capacity_available: 2, sla_compliance_pct: 98 },
            { id: 4, name: 'RainCatch Pro', company: 'RainCatch', rpi_score: 88, rpi_grade: 'A', badge_color: '#22c55e', capacity_available: 6, sla_compliance_pct: 91 },
            { id: 5, name: 'HydroHarvest', company: 'HydroHarvest', rpi_score: 79, rpi_grade: 'B+', badge_color: '#eab308', capacity_available: 10, sla_compliance_pct: 82 },
            { id: 6, name: 'WaterWise Delhi', company: 'WaterWise', rpi_score: 90, rpi_grade: 'A', badge_color: '#22c55e', capacity_available: 4, sla_compliance_pct: 93 },
        ];

        try {
            const controller = new AbortController();
            const timeout = setTimeout(() => controller.abort(), 2000);

            const res = await fetch(`${API_BASE_URL}/api/v1/installers`, { signal: controller.signal });
            clearTimeout(timeout);
            const data = await res.json();
            // Ensure we get an array
            const list = Array.isArray(data) ? data : (Array.isArray(data?.installers) ? data.installers : mockInstallers);
            setInstallers(list.length > 0 ? list : mockInstallers);
        } catch (e) {
            setInstallers(mockInstallers);
        }
    };

    const runAllocation = async () => {
        setLoading(true);

        // For demo: use mock data immediately (instant response)
        // Simulating the algorithm running
        await new Promise(resolve => setTimeout(resolve, 500));

        // Generate realistic mock result based on mode
        const mockResults: Record<string, AllocationResult> = {
            gov_optimized: {
                job_id: 116,
                recommended_installer: { id: 3, name: 'BlueDrop Tech', score: 87.3 },
                score_breakdown: { capacity: 14, rpi: 30, cost_band: 18, distance: 13, sla_history: 12.3 },
                alternatives: [
                    { installer_id: 1, installer_name: 'Jal Mitra Solutions', score: 82.5, rank: 2 },
                    { installer_id: 6, installer_name: 'WaterWise Delhi', score: 78.9, rank: 3 }
                ],
                reason: 'BlueDrop Tech selected: Highest RPI (95) + Excellent SLA compliance (98%)'
            },
            equitable: {
                job_id: 116,
                recommended_installer: { id: 5, name: 'HydroHarvest', score: 74.2 },
                score_breakdown: { capacity: 20, rpi: 22, cost_band: 16, distance: 10, sla_history: 6.2 },
                alternatives: [
                    { installer_id: 4, installer_name: 'RainCatch Pro', score: 71.8, rank: 2 },
                    { installer_id: 2, installer_name: 'AquaSave India', score: 68.5, rank: 3 }
                ],
                reason: 'HydroHarvest selected: Most available capacity (10 slots) for equitable distribution'
            },
            user_choice: {
                job_id: 116,
                recommended_installer: { id: 1, name: 'Jal Mitra Solutions', score: 82.5 },
                score_breakdown: { capacity: 16, rpi: 28, cost_band: 18, distance: 12, sla_history: 8.5 },
                alternatives: [
                    { installer_id: 3, installer_name: 'BlueDrop Tech', score: 78.2, rank: 2 },
                    { installer_id: 2, installer_name: 'AquaSave India', score: 71.5, rank: 3 }
                ],
                reason: 'Jal Mitra Solutions selected based on custom weight preferences'
            }
        };

        setResult(mockResults[mode]);
        setLoading(false);
    };

    const updateWeights = async () => {
        // For demo: just show success
        alert('Weights updated successfully!');
    };

    const modeConfig = {
        user_choice: { icon: Users, label: 'User Choice', desc: 'Custom weights', color: 'blue' },
        gov_optimized: { icon: Target, label: 'Gov Optimized', desc: 'Priority: RPI + SLA', color: 'green' },
        equitable: { icon: Scale, label: 'Equitable', desc: 'Spread work evenly', color: 'purple' }
    };

    return (
        <div className="glass rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Zap className="text-yellow-400" />
                    Smart Allocation Engine
                </h2>
                <button
                    onClick={() => setShowWeights(!showWeights)}
                    className="text-sm text-gray-400 hover:text-white flex items-center gap-1"
                >
                    <Settings size={16} />
                    Tune Weights
                    {showWeights ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                </button>
            </div>

            {/* Mode Selector */}
            <div className="grid grid-cols-3 gap-3">
                {Object.entries(modeConfig).map(([key, config]) => (
                    <button
                        key={key}
                        onClick={() => setMode(key as typeof mode)}
                        className={`p-4 rounded-xl border-2 transition-all ${mode === key
                            ? `border-${config.color}-500 bg-${config.color}-500/20`
                            : 'border-white/10 hover:border-white/30'
                            }`}
                    >
                        <config.icon className={`mb-2 ${mode === key ? `text-${config.color}-400` : 'text-gray-400'}`} size={24} />
                        <div className="font-semibold text-white text-sm">{config.label}</div>
                        <div className="text-xs text-gray-400">{config.desc}</div>
                    </button>
                ))}
            </div>

            {/* Weight Tuning (Admin) */}
            {showWeights && (
                <div className="bg-white/5 rounded-xl p-4 space-y-4">
                    <h4 className="font-semibold text-white">Allocation Weights</h4>
                    {Object.entries(weights).map(([key, value]) => (
                        <div key={key} className="flex items-center gap-4">
                            <label className="w-24 text-sm text-gray-300 capitalize">{key.replace('_', ' ')}</label>
                            <input
                                type="range"
                                min="0"
                                max="0.5"
                                step="0.05"
                                value={value}
                                onChange={(e) => setWeights({ ...weights, [key]: parseFloat(e.target.value) })}
                                className="flex-1"
                            />
                            <span className="text-white w-12 text-right">{(value * 100).toFixed(0)}%</span>
                        </div>
                    ))}
                    <button
                        onClick={updateWeights}
                        className="px-4 py-2 bg-cyan-500 text-white rounded-lg text-sm font-semibold"
                    >
                        Apply Weights
                    </button>
                </div>
            )}

            {/* Run Allocation */}
            <button
                onClick={runAllocation}
                disabled={loading}
                className="w-full py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl hover:scale-[1.02] transition-transform"
            >
                {loading ? 'Running Allocation...' : 'Run Allocation for Demo Job #116'}
            </button>

            {/* Result */}
            {result && (
                <div className="bg-gradient-to-r from-green-500/10 to-emerald-500/10 rounded-xl p-6 border border-green-500/20">
                    <div className="flex items-start justify-between mb-4">
                        <div>
                            <h3 className="text-lg font-bold text-white">Recommended Installer</h3>
                            <p className="text-gray-400 text-sm">{result.reason}</p>
                        </div>
                        <div className="text-3xl font-black text-green-400">{result.recommended_installer.score.toFixed(1)}</div>
                    </div>

                    <div className="flex items-center gap-4 mb-4 p-4 bg-white/5 rounded-lg">
                        <Award className="text-yellow-400" size={40} />
                        <div>
                            <div className="font-bold text-white text-xl">{result.recommended_installer.name}</div>
                            <div className="text-gray-400 text-sm">ID: #{result.recommended_installer.id}</div>
                        </div>
                    </div>

                    {/* Score Breakdown */}
                    <div className="grid grid-cols-5 gap-2 mb-4">
                        {Object.entries(result.score_breakdown).map(([key, value]) => (
                            <div key={key} className="text-center p-2 bg-white/5 rounded-lg">
                                <div className="text-lg font-bold text-white">{value.toFixed(1)}</div>
                                <div className="text-xs text-gray-400 capitalize">{key.replace('_', ' ')}</div>
                            </div>
                        ))}
                    </div>

                    {/* Alternatives */}
                    <div className="text-sm text-gray-400 mb-2">Alternatives:</div>
                    <div className="space-y-2">
                        {result.alternatives.map((alt) => (
                            <div key={alt.installer_id} className="flex items-center justify-between p-3 bg-white/5 rounded-lg">
                                <span className="text-white">#{alt.rank} {alt.installer_name}</span>
                                <span className="text-gray-300">{alt.score.toFixed(1)}</span>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Installer Cards */}
            <div>
                <h3 className="text-lg font-semibold text-white mb-4">Available Installers</h3>
                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                    {installers.slice(0, 6).map((inst) => (
                        <div key={inst.id} className="bg-white/5 rounded-xl p-4 hover:bg-white/10 transition-colors">
                            <div className="flex items-start justify-between mb-2">
                                <div>
                                    <div className="font-semibold text-white">{inst.name}</div>
                                    <div className="text-xs text-gray-400">{inst.company}</div>
                                </div>
                                <div
                                    className="px-2 py-1 rounded-full text-xs font-bold"
                                    style={{ backgroundColor: inst.badge_color + '20', color: inst.badge_color }}
                                >
                                    {inst.rpi_grade} • {inst.rpi_score}
                                </div>
                            </div>
                            <div className="flex items-center gap-4 text-xs text-gray-400">
                                <span className="flex items-center gap-1">
                                    <Users size={12} />
                                    {inst.capacity_available} slots
                                </span>
                                <span className="flex items-center gap-1">
                                    <CheckCircle size={12} />
                                    {inst.sla_compliance_pct}% SLA
                                </span>
                            </div>
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default AllocationPanel;
