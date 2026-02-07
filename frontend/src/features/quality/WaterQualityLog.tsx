/**
 * Water Quality Log Component
 * Track pH, TDS, Turbidity and analyze safety
 */

import React, { useState } from 'react';
import {
    FlaskConical, AlertTriangle, CheckCircle, Save,
    Droplet, Activity, History, LineChart as ChartIcon
} from 'lucide-react';
import { LineChart, Line, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid } from 'recharts';

interface QualityLog {
    id: string;
    date: string;
    ph: number;
    tds: number;
    turbidity: string;
    notes: string;
    status: 'safe' | 'warning' | 'unsafe';
}

const WaterQualityLog = () => {
    const [logs, setLogs] = useState<QualityLog[]>([
        { id: '1', date: '2024-01-15', ph: 7.2, tds: 150, turbidity: 'Clear', notes: 'Post-rain test', status: 'safe' },
        { id: '2', date: '2024-02-01', ph: 6.8, tds: 180, turbidity: 'Slight cloudy', notes: 'Tank cleaning due', status: 'warning' },
        { id: '3', date: '2024-02-20', ph: 7.0, tds: 145, turbidity: 'Clear', notes: 'After filter replace', status: 'safe' },
    ]);

    const [form, setForm] = useState({
        ph: '',
        tds: '',
        turbidity: 'Clear',
        notes: ''
    });

    const calculateStatus = (ph: number, tds: number): QualityLog['status'] => {
        if (ph < 6.5 || ph > 8.5 || tds > 500) return 'unsafe';
        if (ph < 6.8 || ph > 8.0 || tds > 300) return 'warning';
        return 'safe';
    };

    const handleSave = () => {
        const phVal = parseFloat(form.ph);
        const tdsVal = parseInt(form.tds);

        if (!phVal || !tdsVal) return;

        const newLog: QualityLog = {
            id: Date.now().toString(),
            date: new Date().toISOString().split('T')[0],
            ph: phVal,
            tds: tdsVal,
            turbidity: form.turbidity,
            notes: form.notes,
            status: calculateStatus(phVal, tdsVal)
        };

        setLogs([newLog, ...logs]);
        setForm({ ph: '', tds: '', turbidity: 'Clear', notes: '' });
    };

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="glass rounded-2xl p-6">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-teal-500 to-emerald-500 flex items-center justify-center">
                        <FlaskConical className="text-white" size={24} />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">Water Quality Log</h2>
                        <p className="text-gray-400">Track potability and filtration health</p>
                    </div>
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Entry Form */}
                <div className="lg:col-span-1 space-y-6">
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Activity size={18} className="text-teal-400" />
                            New Test Entry
                        </h3>

                        <div className="space-y-4">
                            <div>
                                <label className="block text-sm text-gray-400 mb-1">pH Level (6.5 - 8.5)</label>
                                <input
                                    type="number"
                                    step="0.1"
                                    value={form.ph}
                                    onChange={e => setForm({ ...form, ph: e.target.value })}
                                    placeholder="e.g. 7.2"
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white focus:border-teal-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">TDS (ppm)</label>
                                <input
                                    type="number"
                                    value={form.tds}
                                    onChange={e => setForm({ ...form, tds: e.target.value })}
                                    placeholder="e.g. 150"
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white focus:border-teal-500 focus:outline-none"
                                />
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Turbidity (Visual)</label>
                                <select
                                    value={form.turbidity}
                                    onChange={e => setForm({ ...form, turbidity: e.target.value })}
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white focus:border-teal-500 focus:outline-none"
                                >
                                    <option className="bg-slate-800">Clear</option>
                                    <option className="bg-slate-800">Slightly Cloudy</option>
                                    <option className="bg-slate-800">Cloudy</option>
                                    <option className="bg-slate-800">Dirty</option>
                                </select>
                            </div>

                            <div>
                                <label className="block text-sm text-gray-400 mb-1">Notes</label>
                                <textarea
                                    value={form.notes}
                                    onChange={e => setForm({ ...form, notes: e.target.value })}
                                    placeholder="Any observations..."
                                    className="w-full bg-white/5 border border-white/10 rounded-xl p-3 text-white focus:border-teal-500 focus:outline-none resize-none h-20"
                                />
                            </div>

                            <button
                                onClick={handleSave}
                                className="w-full py-3 bg-gradient-to-r from-teal-500 to-emerald-500 text-white font-bold rounded-xl hover:opacity-90 transition-opacity flex items-center justify-center gap-2"
                            >
                                <Save size={18} />
                                Save Log
                            </button>
                        </div>
                    </div>
                </div>

                {/* Charts & History */}
                <div className="lg:col-span-2 space-y-6">
                    {/* Visual Chart */}
                    <div className="glass rounded-2xl p-6 h-[300px]">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <ChartIcon size={18} className="text-purple-400" />
                            Trend Analysis
                        </h3>
                        <ResponsiveContainer width="100%" height="100%">
                            <LineChart data={[...logs].reverse()}>
                                <CartesianGrid strokeDasharray="3 3" stroke="#ffffff10" />
                                <XAxis dataKey="date" stroke="#94a3b8" fontSize={12} />
                                <YAxis stroke="#94a3b8" fontSize={12} />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155' }}
                                    itemStyle={{ color: '#fff' }}
                                />
                                <Line type="monotone" dataKey="ph" stroke="#2dd4bf" strokeWidth={2} name="pH Level" />
                                <Line type="monotone" dataKey="tds" stroke="#8b5cf6" strokeWidth={2} name="TDS (ppm)" />
                            </LineChart>
                        </ResponsiveContainer>
                    </div>

                    {/* Recent Logs List */}
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <History size={18} className="text-cyan-400" />
                            Recent Logs
                        </h3>
                        <div className="space-y-3">
                            {logs.map(log => (
                                <div key={log.id} className="flex items-center justify-between p-3 bg-white/5 rounded-xl border border-white/5 hover:border-white/10 transition-colors">
                                    <div className="flex items-center gap-3">
                                        <div className={`w-2 h-12 rounded-full ${log.status === 'safe' ? 'bg-green-500' :
                                                log.status === 'warning' ? 'bg-yellow-500' : 'bg-red-500'
                                            }`} />
                                        <div>
                                            <div className="text-white font-medium">{log.date}</div>
                                            <div className="text-sm text-gray-400">{log.notes || 'No notes'}</div>
                                        </div>
                                    </div>
                                    <div className="flex gap-4 text-right">
                                        <div>
                                            <div className="text-xs text-gray-500">pH</div>
                                            <div className="text-white font-bold">{log.ph}</div>
                                        </div>
                                        <div>
                                            <div className="text-xs text-gray-500">TDS</div>
                                            <div className="text-white font-bold">{log.tds}</div>
                                        </div>
                                        <div className="hidden sm:block">
                                            <div className="text-xs text-gray-500">Clarity</div>
                                            <div className="text-white font-bold">{log.turbidity}</div>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default WaterQualityLog;
