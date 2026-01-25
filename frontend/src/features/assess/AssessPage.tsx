import { useLocation } from 'react-router-dom';
import {
    Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    AreaChart, Area, ComposedChart, Line
} from 'recharts';
import {
    CloudRain, Database, DollarSign, FileText, TrendingUp, Droplets,
    Zap, Download, Info, ChevronDown, ChevronUp, CheckCircle, Leaf
} from 'lucide-react';
import { useState } from 'react';

const AssessPage = () => {
    const { state } = useLocation();
    const result = state?.result;
    const [showExplanation, setShowExplanation] = useState<string | null>(null);
    const [activeScenario, setActiveScenario] = useState('cost_optimized');

    // Mock scenario comparison data
    const scenarios = [
        {
            id: 'cost_optimized',
            name: 'Cost Optimized',
            tank: 12000,
            cost: 96000,
            savings: 4200,
            payback: 2.8,
            reliability: 85,
            desc: 'Minimizes investment while meeting 80% of demand'
        },
        {
            id: 'max_capture',
            name: 'Maximum Capture',
            tank: 25000,
            cost: 175000,
            savings: 5800,
            payback: 3.5,
            reliability: 98,
            desc: 'Captures all available rainfall, maximum water security'
        },
        {
            id: 'dry_season',
            name: 'Dry Season',
            tank: 18000,
            cost: 126000,
            savings: 5000,
            payback: 3.0,
            reliability: 92,
            desc: 'Optimized for Nov-Mar water availability'
        },
    ];

    if (!result) return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
            <div className="text-center glass rounded-2xl p-12 max-w-md">
                <div className="text-6xl mb-6">📊</div>
                <h2 className="text-2xl font-bold text-white mb-2">Demo Assessment</h2>
                <p className="text-gray-400 mb-6">No live data - showing demo results</p>
            </div>
        </div>
    );

    const chartData = result.monthly_breakdown.map((val: number, idx: number) => ({
        month: ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"][idx],
        yield: Math.round(val),
        demand: 15000,
        cumulative: result.monthly_breakdown.slice(0, idx + 1).reduce((a: number, b: number) => a + b, 0)
    }));

    // Water balance data
    const balanceData = chartData.map((d: { month: string; yield: number; demand: number }) => ({
        month: d.month,
        supply: d.yield,
        demand: d.demand,
        balance: d.yield - d.demand
    }));

    const downloadReport = async () => {
        try {
            const response = await fetch(`http://localhost:8000/api/v1/assessments/${result.project_id}/report`);
            const blob = await response.blob();
            const url = window.URL.createObjectURL(blob);
            const a = document.createElement('a');
            a.href = url;
            a.download = `RainForge_Report_${result.project_id}.pdf`;
            a.click();
        } catch (e) {
            alert("Download failed");
        }
    };

    const ExplainPanel = ({ title, children, id }: { title: string; children: React.ReactNode; id: string }) => (
        <div className="mt-2">
            <button
                onClick={() => setShowExplanation(showExplanation === id ? null : id)}
                className="flex items-center gap-2 text-sm text-cyan-400 hover:text-cyan-300"
            >
                <Info size={14} />
                Explain Calculation
                {showExplanation === id ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
            </button>
            {showExplanation === id && (
                <div className="mt-3 p-4 bg-white/5 rounded-lg text-sm text-gray-300 space-y-2">
                    <div className="font-semibold text-white">{title}</div>
                    {children}
                </div>
            )}
        </div>
    );

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                {/* Header */}
                <div className="glass rounded-2xl p-8">
                    <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                        <div>
                            <div className="flex items-center gap-3 mb-2">
                                <div className="p-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-lg">
                                    <Droplets className="text-white" size={24} />
                                </div>
                                <h1 className="text-4xl font-black text-white">Assessment Complete</h1>
                            </div>
                            <p className="text-gray-400">Project #{result.project_id} • Generated just now</p>
                        </div>
                        <button
                            onClick={downloadReport}
                            className="flex items-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-lg"
                        >
                            <Download size={20} />
                            Download PDF
                        </button>
                    </div>
                </div>

                {/* Scenario Selector */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-xl font-bold text-white mb-4 flex items-center gap-2">
                        <Zap className="text-yellow-400" size={20} />
                        Scenario Comparison
                    </h3>
                    <div className="grid md:grid-cols-3 gap-4">
                        {scenarios.map(s => (
                            <button
                                key={s.id}
                                onClick={() => setActiveScenario(s.id)}
                                className={`p-5 rounded-xl text-left transition-all ${activeScenario === s.id
                                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border-2 border-cyan-500'
                                    : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                                    }`}
                            >
                                <div className="flex justify-between items-start mb-2">
                                    <span className="font-bold text-white">{s.name}</span>
                                    {activeScenario === s.id && <CheckCircle className="text-cyan-400" size={18} />}
                                </div>
                                <p className="text-xs text-gray-400 mb-3">{s.desc}</p>
                                <div className="grid grid-cols-2 gap-2 text-sm">
                                    <div>
                                        <span className="text-gray-400">Tank:</span>
                                        <span className="text-white ml-1">{(s.tank / 1000)}kL</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">Cost:</span>
                                        <span className="text-green-400 ml-1">₹{(s.cost / 1000)}k</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">ROI:</span>
                                        <span className="text-white ml-1">{s.payback}yr</span>
                                    </div>
                                    <div>
                                        <span className="text-gray-400">Reliability:</span>
                                        <span className="text-cyan-400 ml-1">{s.reliability}%</span>
                                    </div>
                                </div>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Key Metrics */}
                <div className="grid grid-cols-1 md:grid-cols-4 gap-6">
                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-gradient-to-br from-blue-500 to-cyan-500 rounded-xl">
                                <CloudRain className="text-white" size={28} />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-400 mb-1">Annual Yield</p>
                                <h3 className="text-2xl font-black text-white">
                                    {Math.round(result.runoff_potential_liters).toLocaleString()}L
                                </h3>
                            </div>
                        </div>
                        <ExplainPanel id="yield" title="Yield Calculation">
                            <p><strong>Formula:</strong> Q = C × I × A × η</p>
                            <p><strong>C:</strong> Runoff coefficient (0.85 for concrete)</p>
                            <p><strong>I:</strong> Rainfall (mm/year)</p>
                            <p><strong>A:</strong> Roof area (m²)</p>
                            <p><strong>η:</strong> Collection efficiency (90%)</p>
                            <p className="text-xs text-gray-500 mt-2">Reference: IS 15797:2008</p>
                        </ExplainPanel>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-gradient-to-br from-indigo-500 to-purple-500 rounded-xl">
                                <Database className="text-white" size={28} />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-400 mb-1">Tank Size</p>
                                <h3 className="text-2xl font-black text-white">
                                    {Math.round(result.recommended_tank_size).toLocaleString()}L
                                </h3>
                            </div>
                        </div>
                        <ExplainPanel id="tank" title="Tank Sizing">
                            <p><strong>Method:</strong> 2-month carryover (Cost Optimized)</p>
                            <p><strong>Daily demand:</strong> 500L × 30 days × 2 = 30,000L</p>
                            <p><strong>Adjusted for:</strong> Peak capture efficiency</p>
                        </ExplainPanel>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-gradient-to-br from-green-500 to-emerald-500 rounded-xl">
                                <DollarSign className="text-white" size={28} />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-400 mb-1">Est. Cost</p>
                                <h3 className="text-2xl font-black text-white">₹96K</h3>
                                <p className="text-xs text-green-400">After subsidy: ₹48K</p>
                            </div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-start gap-4">
                            <div className="p-3 bg-gradient-to-br from-yellow-500 to-orange-500 rounded-xl">
                                <Leaf className="text-white" size={28} />
                            </div>
                            <div className="flex-1">
                                <p className="text-sm font-medium text-gray-400 mb-1">CO₂ Offset</p>
                                <h3 className="text-2xl font-black text-white">64 kg/yr</h3>
                                <p className="text-xs text-gray-400">From reduced pumping</p>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Charts Row */}
                <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
                    {/* Water Balance Chart */}
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <TrendingUp className="text-cyan-400" size={20} />
                            Water Balance Simulation
                        </h3>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <ComposedChart data={balanceData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                    <XAxis dataKey="month" stroke="#94a3b8" />
                                    <YAxis stroke="#94a3b8" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        labelStyle={{ color: '#f1f5f9' }}
                                    />
                                    <Bar dataKey="supply" fill="#06b6d4" radius={[4, 4, 0, 0]} name="Supply" />
                                    <Line type="monotone" dataKey="demand" stroke="#f59e0b" strokeWidth={2} name="Demand" />
                                </ComposedChart>
                            </ResponsiveContainer>
                        </div>
                        <ExplainPanel id="balance" title="Water Balance Method">
                            <p>Monthly mass balance: Sₜ = Sₜ₋₁ + Qₜ - Dₜ</p>
                            <p>Blue bars = rainfall capture, Orange line = household demand</p>
                            <p>Months where supply &gt; demand = surplus (stored for dry months)</p>
                        </ExplainPanel>
                    </div>

                    {/* Cumulative Chart */}
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-xl font-bold text-white mb-6 flex items-center gap-2">
                            <Droplets className="text-green-400" size={20} />
                            Cumulative Capture
                        </h3>
                        <div className="h-80 w-full">
                            <ResponsiveContainer width="100%" height="100%">
                                <AreaChart data={chartData}>
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} />
                                    <XAxis dataKey="month" stroke="#94a3b8" />
                                    <YAxis stroke="#94a3b8" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        formatter={(value) => [`${Math.round(value as number).toLocaleString()} L`, 'Total']}
                                    />
                                    <Area type="monotone" dataKey="cumulative" stroke="#10b981" fill="url(#colorGreen)" />
                                    <defs>
                                        <linearGradient id="colorGreen" x1="0" y1="0" x2="0" y2="1">
                                            <stop offset="0%" stopColor="#10b981" stopOpacity={0.8} />
                                            <stop offset="100%" stopColor="#10b981" stopOpacity={0.1} />
                                        </linearGradient>
                                    </defs>
                                </AreaChart>
                            </ResponsiveContainer>
                        </div>
                    </div>
                </div>

                {/* Policy & Subsidy Card */}
                <div className="glass rounded-2xl p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border-green-500/20">
                    <h3 className="text-xl font-bold text-white mb-4">💰 Policy & Subsidy Insights</h3>
                    <div className="grid md:grid-cols-3 gap-6">
                        <div>
                            <p className="text-gray-400 text-sm mb-1">Eligible Scheme</p>
                            <p className="text-white font-semibold">Jal Shakti Abhiyan RWH Subsidy</p>
                        </div>
                        <div>
                            <p className="text-gray-400 text-sm mb-1">Subsidy Amount</p>
                            <p className="text-green-400 font-bold text-2xl">₹48,000</p>
                            <p className="text-xs text-gray-500">50% of system cost (max ₹50K)</p>
                        </div>
                        <div>
                            <p className="text-gray-400 text-sm mb-1">Net Cost After Subsidy</p>
                            <p className="text-white font-bold text-2xl">₹48,000</p>
                            <p className="text-xs text-gray-500">Effective payback: 1.4 years</p>
                        </div>
                    </div>
                </div>

                {/* Recommendations */}
                <div className="glass rounded-2xl p-8">
                    <h3 className="text-2xl font-bold text-white mb-6 flex items-center gap-2">
                        <FileText className="text-cyan-400" size={24} />
                        System Recommendations
                    </h3>
                    <div className="grid md:grid-cols-2 gap-4">
                        {[
                            { title: "First Flush Diverter", desc: "20L capacity, auto-reset type", icon: "💧" },
                            { title: "Filtration System", desc: "2-stage: gravel + mesh before tank", icon: "🔧" },
                            { title: "Overflow Management", desc: "Route to recharge pit (2m³)", icon: "🌊" },
                            { title: "Pump Specification", desc: "0.5 HP submersible, 2000 LPH", icon: "⚡" }
                        ].map((rec, i) => (
                            <div key={i} className="flex items-start gap-4 p-4 bg-white/5 rounded-xl">
                                <div className="text-3xl">{rec.icon}</div>
                                <div>
                                    <h4 className="font-bold text-white mb-1">{rec.title}</h4>
                                    <p className="text-sm text-gray-400">{rec.desc}</p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default AssessPage;
