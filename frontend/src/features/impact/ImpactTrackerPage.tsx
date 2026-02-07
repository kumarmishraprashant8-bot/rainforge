/**
 * Impact Tracker Page
 * Before/After analysis and cumulative impact dashboard
 */

import { useState } from 'react';
import {
    TrendingUp, Droplets, Leaf, DollarSign, Calendar,
    Download, Share2, ChevronDown, BarChart3, Target
} from 'lucide-react';
import {
    AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer,
    BarChart, Bar, LineChart, Line, PieChart, Pie, Cell
} from 'recharts';
import ShareButtons from '../../components/ShareButtons';
import CertificateGenerator from '../../components/CertificateGenerator';

const ImpactTrackerPage = () => {
    const [timeRange, setTimeRange] = useState<'3m' | '6m' | '1y' | 'all'>('6m');

    // Demo data
    const monthlyData = [
        { month: 'Sep', collected: 4200, saved: 280, co2: 2.1 },
        { month: 'Oct', collected: 8500, saved: 567, co2: 4.3 },
        { month: 'Nov', collected: 12300, saved: 820, co2: 6.2 },
        { month: 'Dec', collected: 3200, saved: 213, co2: 1.6 },
        { month: 'Jan', collected: 1800, saved: 120, co2: 0.9 },
        { month: 'Feb', collected: 2100, saved: 140, co2: 1.1 },
    ];

    const usageBreakdown = [
        { name: 'Gardening', value: 45, color: '#10b981' },
        { name: 'Toilet Flush', value: 30, color: '#3b82f6' },
        { name: 'Cleaning', value: 15, color: '#8b5cf6' },
        { name: 'Laundry', value: 10, color: '#f59e0b' },
    ];

    const billComparison = [
        { month: 'Before', municipal: 2500, rainwater: 0 },
        { month: 'After', municipal: 1100, rainwater: 1400 },
    ];

    const stats = {
        totalCollected: 245000,
        totalSaved: 12300,
        co2Offset: 122,
        waterCredits: 245,
        treesEquivalent: 6,
        showersEquivalent: 4900,
        billReduction: 56,
        roiAchieved: 18,
    };

    const handleExport = () => {
        // Load html2pdf dynamically
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
        script.onload = () => {
            generatePDF();
        };
        document.body.appendChild(script);

        const generatePDF = () => {
            const reportHTML = `
            <div style="font-family: system-ui, -apple-system, sans-serif; color: #1e293b; max-width: 800px; margin: 0 auto; padding: 40px; background: white;">
                <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 40px; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px;">
                    <div style="font-size: 24px; font-weight: bold; color: #0f172a;">🌧️ Rain<span style="color: #06b6d4;">Forge</span></div>
                    <div style="color: #64748b; font-size: 14px;">Generated on ${new Date().toLocaleDateString()}</div>
                </div>

                <div style="font-size: 32px; font-weight: bold; margin-bottom: 10px; color: #0f172a;">Impact Report</div>
                <div style="color: #64748b; margin-bottom: 40px;">Water Conservation Analysis • ${timeRange === 'all' ? 'All Time' : `Last ${timeRange.toUpperCase()}`}</div>

                <div style="display: grid; grid-template-columns: repeat(2, 1fr); gap: 20px; margin-bottom: 40px;">
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Total Water Collected</div>
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">${(stats.totalCollected / 1000).toLocaleString()}k Liters</div>
                    </div>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Money Saved</div>
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">₹${stats.totalSaved.toLocaleString()}</div>
                    </div>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">CO₂ Offset</div>
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">${stats.co2Offset} kg</div>
                    </div>
                    <div style="background: #f8fafc; padding: 20px; border-radius: 12px; border: 1px solid #e2e8f0;">
                        <div style="color: #64748b; font-size: 14px; margin-bottom: 5px;">Trees Equivalent</div>
                        <div style="font-size: 24px; font-weight: bold; color: #0f172a;">${stats.treesEquivalent} Trees 🌳</div>
                    </div>
                </div>

                <div style="margin-top: 40px;">
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;">Monthly Breakdown</div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <thead>
                            <tr>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Month</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Collected (L)</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Saved (₹)</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">CO₂ (kg)</th>
                            </tr>
                        </thead>
                        <tbody>
                            ${monthlyData.map(d => `
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">${d.month}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">${d.collected.toLocaleString()}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${d.saved}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">${d.co2}</td>
                            </tr>
                            `).join('')}
                        </tbody>
                    </table>
                </div>

                <div style="margin-top: 40px;">
                    <div style="font-size: 18px; font-weight: bold; margin-bottom: 15px; border-bottom: 1px solid #e2e8f0; padding-bottom: 5px;">Bill Comparison</div>
                    <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                        <thead>
                            <tr>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Period</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Municipal Bill</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Rainwater Value</th>
                                <th style="text-align: left; padding: 10px; border-bottom: 2px solid #e2e8f0; color: #64748b;">Net Cost</th>
                            </tr>
                        </thead>
                        <tbody>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">Before RWH</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${billComparison[0].municipal}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹0</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${billComparison[0].municipal}</td>
                            </tr>
                            <tr>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">After RWH</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${billComparison[1].municipal}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${billComparison[1].municipal}</td>
                                <td style="padding: 10px; border-bottom: 1px solid #e2e8f0;">₹${billComparison[0].municipal - billComparison[1].municipal} (Saved)</td>
                            </tr>
                        </tbody>
                    </table>
                </div>

                <div style="margin-top: 60px; text-align: center; color: #94a3b8; font-size: 12px; border-top: 1px solid #e2e8f0; padding-top: 20px;">
                    Generated by RainForge • Making every drop count
                </div>
            </div>`;

            // Create temporary container
            const container = document.createElement('div');
            container.innerHTML = reportHTML;

            // Use html2pdf to generate and save
            // @ts-ignore
            if (window.html2pdf) {
                const opt = {
                    margin: 10,
                    filename: `RainForge_Impact_Report_${new Date().toISOString().split('T')[0]}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };

                // @ts-ignore
                window.html2pdf().from(container).set(opt).save();
            } else {
                alert('PDF Generator is loading... please try again in a second.');
            }
        };
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div>
                        <h1 className="text-3xl font-black text-white flex items-center gap-3">
                            <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
                                <TrendingUp className="text-white" size={28} />
                            </div>
                            Your Impact
                        </h1>
                        <p className="text-gray-400 mt-1">Track your water conservation journey</p>
                    </div>
                    <div className="flex gap-3">
                        <div className="flex gap-1 bg-white/5 rounded-xl p-1">
                            {(['3m', '6m', '1y', 'all'] as const).map(range => (
                                <button
                                    key={range}
                                    onClick={() => setTimeRange(range)}
                                    className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${timeRange === range
                                        ? 'bg-cyan-500 text-white'
                                        : 'text-gray-400 hover:text-white'
                                        }`}
                                >
                                    {range === 'all' ? 'All Time' : range.toUpperCase()}
                                </button>
                            ))}
                        </div>
                        <div className="flex gap-3 flex-wrap">
                            <ShareButtons
                                title="My Water Impact"
                                text={`I've saved ${(stats.totalCollected / 1000).toFixed(0)}k liters of water with RainForge! 💧`}
                            />
                            <button
                                onClick={handleExport}
                                className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl text-white hover:bg-white/10"
                            >
                                <Download size={18} />
                                Export
                            </button>
                        </div>
                    </div>
                </div>

                {/* Headline Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-cyan-500/20 rounded-lg">
                                <Droplets className="text-cyan-400" size={20} />
                            </div>
                            <span className="text-gray-400">Total Collected</span>
                        </div>
                        <div className="text-3xl font-black text-white">{(stats.totalCollected / 1000).toFixed(0)}k L</div>
                        <div className="text-green-400 text-sm flex items-center gap-1 mt-1">
                            <TrendingUp size={14} /> +23% vs last period
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-green-500/20 rounded-lg">
                                <DollarSign className="text-green-400" size={20} />
                            </div>
                            <span className="text-gray-400">Money Saved</span>
                        </div>
                        <div className="text-3xl font-black text-white">₹{stats.totalSaved.toLocaleString()}</div>
                        <div className="text-green-400 text-sm flex items-center gap-1 mt-1">
                            <TrendingUp size={14} /> {stats.billReduction}% bill reduction
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-emerald-500/20 rounded-lg">
                                <Leaf className="text-emerald-400" size={20} />
                            </div>
                            <span className="text-gray-400">CO₂ Offset</span>
                        </div>
                        <div className="text-3xl font-black text-white">{stats.co2Offset} kg</div>
                        <div className="text-emerald-400 text-sm mt-1">
                            = {stats.treesEquivalent} trees planted
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-purple-500/20 rounded-lg">
                                <Target className="text-purple-400" size={20} />
                            </div>
                            <span className="text-gray-400">ROI Progress</span>
                        </div>
                        <div className="text-3xl font-black text-white">{stats.roiAchieved}%</div>
                        <div className="w-full bg-white/10 rounded-full h-2 mt-2">
                            <div className="bg-gradient-to-r from-purple-500 to-pink-500 h-2 rounded-full" style={{ width: `${stats.roiAchieved}%` }} />
                        </div>
                    </div>
                </div>

                {/* Collection Chart */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-6">Monthly Water Collection</h3>
                    <div className="h-72">
                        <ResponsiveContainer width="100%" height="100%">
                            <AreaChart data={monthlyData}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                <XAxis dataKey="month" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                    formatter={(value) => [`${(value as number)?.toLocaleString() ?? 0} L`, 'Collected']}
                                />
                                <defs>
                                    <linearGradient id="colorCollected" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="0%" stopColor="#06b6d4" stopOpacity={0.5} />
                                        <stop offset="100%" stopColor="#06b6d4" stopOpacity={0.05} />
                                    </linearGradient>
                                </defs>
                                <Area
                                    type="monotone"
                                    dataKey="collected"
                                    stroke="#06b6d4"
                                    strokeWidth={2}
                                    fill="url(#colorCollected)"
                                />
                            </AreaChart>
                        </ResponsiveContainer>
                    </div>
                </div>

                <div className="grid lg:grid-cols-2 gap-6">
                    {/* Bill Comparison */}
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-6">Water Bill: Before vs After</h3>
                        <div className="h-64">
                            <ResponsiveContainer width="100%" height="100%">
                                <BarChart data={billComparison} layout="vertical">
                                    <CartesianGrid strokeDasharray="3 3" stroke="#334155" />
                                    <XAxis type="number" stroke="#94a3b8" />
                                    <YAxis type="category" dataKey="month" stroke="#94a3b8" />
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        formatter={(value) => [`₹${value ?? 0}`, '']}
                                    />
                                    <Bar dataKey="municipal" name="Municipal Water" stackId="a" fill="#ef4444" radius={[0, 0, 0, 0]} />
                                    <Bar dataKey="rainwater" name="Rainwater Used" stackId="a" fill="#10b981" radius={[0, 8, 8, 0]} />
                                </BarChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex justify-center gap-6 mt-4">
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-red-500" />
                                <span className="text-gray-400 text-sm">Municipal Water</span>
                            </div>
                            <div className="flex items-center gap-2">
                                <div className="w-3 h-3 rounded-full bg-green-500" />
                                <span className="text-gray-400 text-sm">Rainwater Used</span>
                            </div>
                        </div>
                    </div>

                    {/* Usage Breakdown */}
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-6">Water Usage Breakdown</h3>
                        <div className="h-64 flex items-center justify-center">
                            <ResponsiveContainer width="100%" height="100%">
                                <PieChart>
                                    <Pie
                                        data={usageBreakdown}
                                        cx="50%"
                                        cy="50%"
                                        innerRadius={60}
                                        outerRadius={90}
                                        paddingAngle={4}
                                        dataKey="value"
                                    >
                                        {usageBreakdown.map((entry, index) => (
                                            <Cell key={`cell-${index}`} fill={entry.color} />
                                        ))}
                                    </Pie>
                                    <Tooltip
                                        contentStyle={{ backgroundColor: '#1e293b', border: '1px solid #334155', borderRadius: '8px' }}
                                        formatter={(value) => [`${value ?? 0}%`, '']}
                                    />
                                </PieChart>
                            </ResponsiveContainer>
                        </div>
                        <div className="flex flex-wrap justify-center gap-4 mt-4">
                            {usageBreakdown.map((item, idx) => (
                                <div key={idx} className="flex items-center gap-2">
                                    <div className="w-3 h-3 rounded-full" style={{ backgroundColor: item.color }} />
                                    <span className="text-gray-400 text-sm">{item.name} ({item.value}%)</span>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>

                {/* Fun Facts */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Your Impact in Perspective</h3>
                    <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-4xl mb-2">🚿</div>
                            <div className="text-2xl font-bold text-white">{stats.showersEquivalent.toLocaleString()}</div>
                            <div className="text-gray-400 text-sm">5-min showers</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-4xl mb-2">🌳</div>
                            <div className="text-2xl font-bold text-white">{stats.treesEquivalent}</div>
                            <div className="text-gray-400 text-sm">Trees planted equivalent</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-4xl mb-2">🚗</div>
                            <div className="text-2xl font-bold text-white">{Math.round(stats.co2Offset / 0.21)}</div>
                            <div className="text-gray-400 text-sm">km of driving offset</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-4xl mb-2">💧</div>
                            <div className="text-2xl font-bold text-white">{stats.waterCredits}</div>
                            <div className="text-gray-400 text-sm">Water credits earned</div>
                        </div>
                    </div>
                </div>

                {/* Achievement Certificate */}
                <CertificateGenerator
                    data={{
                        userName: "Demo User",
                        waterSaved: stats.totalCollected,
                        co2Offset: stats.co2Offset,
                        date: new Date().toLocaleDateString('en-IN', { month: 'long', year: 'numeric' }),
                        certificateId: `RF-${Date.now().toString(36).toUpperCase()}`
                    }}
                />
            </div>
        </div>
    );
};

export default ImpactTrackerPage;
