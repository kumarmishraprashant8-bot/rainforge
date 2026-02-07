/**
 * Historical Rainfall Component
 * Visualize past rainfall data vs averages
 */

import React, { useState, useEffect } from 'react';
import { CloudRain, TrendingUp, AlertCircle, Calendar } from 'lucide-react';
import { BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, ReferenceLine } from 'recharts';
import { weatherService } from '../services/weatherService';

const HistoricalRainfall = () => {
    const [history, setHistory] = useState<{ year: number; rainfall_mm: number; average_mm: number }[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, []);

    const loadData = async () => {
        setLoading(true);
        try {
            const data = await weatherService.getHistoricalRainfall('user-location');
            setHistory(data);
        } catch (error) {
            console.error('Failed to load history:', error);
        } finally {
            setLoading(false);
        }
    };

    const currentYearData = history[history.length - 1];
    const deviation = currentYearData
        ? Math.round(((currentYearData.rainfall_mm - currentYearData.average_mm) / currentYearData.average_mm) * 100)
        : 0;

    return (
        <div className="space-y-6 animate-fade-in">
            {/* Header */}
            <div className="glass rounded-2xl p-6">
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-4">
                        <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-blue-500 to-indigo-500 flex items-center justify-center">
                            <CloudRain className="text-white" size={24} />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Rainfall History</h2>
                            <p className="text-gray-400">5-Year Comparative Analysis</p>
                        </div>
                    </div>
                    {currentYearData && (
                        <div className={`px-4 py-2 rounded-xl border ${deviation < 0
                                ? 'bg-red-500/10 border-red-500/30 text-red-400'
                                : 'bg-green-500/10 border-green-500/30 text-green-400'
                            } flex items-center gap-2`}>
                            <TrendingUp size={18} />
                            <span className="font-bold">{deviation > 0 ? '+' : ''}{deviation}%</span>
                            <span className="text-sm">vs Average</span>
                        </div>
                    )}
                </div>
            </div>

            <div className="grid lg:grid-cols-3 gap-6">
                {/* Main Graph */}
                <div className="lg:col-span-2 glass rounded-2xl p-6 h-[400px]">
                    <h3 className="text-lg font-bold text-white mb-6">Annual Rainfall (mm)</h3>
                    {loading ? (
                        <div className="h-full flex items-center justify-center text-gray-400">Loading data...</div>
                    ) : (
                        <ResponsiveContainer width="100%" height="90%">
                            <BarChart data={history} margin={{ top: 20, right: 30, left: 20, bottom: 5 }}>
                                <XAxis dataKey="year" stroke="#94a3b8" />
                                <YAxis stroke="#94a3b8" />
                                <Tooltip
                                    contentStyle={{ backgroundColor: '#1e293b', borderColor: '#334155', color: '#fff' }}
                                    cursor={{ fill: 'rgba(255,255,255,0.05)' }}
                                />
                                <ReferenceLine y={800} stroke="#f59e0b" strokeDasharray="3 3" label={{ value: 'Avg (800mm)', fill: '#f59e0b', fontSize: 12 }} />
                                <Bar dataKey="rainfall_mm" name="Actual Rainfall" fill="url(#colorRain)" radius={[4, 4, 0, 0]} />
                                <defs>
                                    <linearGradient id="colorRain" x1="0" y1="0" x2="0" y2="1">
                                        <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.8} />
                                        <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.3} />
                                    </linearGradient>
                                </defs>
                            </BarChart>
                        </ResponsiveContainer>
                    )}
                </div>

                {/* Insights Panel */}
                <div className="space-y-6">
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                            <Calendar size={18} className="text-cyan-400" />
                            Key Insights
                        </h3>
                        <div className="space-y-4">
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <p className="text-gray-400 text-sm mb-1">Wettest Year</p>
                                <p className="text-xl font-bold text-white">
                                    {history.sort((a, b) => b.rainfall_mm - a.rainfall_mm)[0]?.year}
                                    <span className="text-sm font-normal text-gray-500 ml-2">
                                        ({history.sort((a, b) => b.rainfall_mm - a.rainfall_mm)[0]?.rainfall_mm}mm)
                                    </span>
                                </p>
                            </div>
                            <div className="p-4 bg-white/5 rounded-xl border border-white/5">
                                <p className="text-gray-400 text-sm mb-1">Driest Year</p>
                                <p className="text-xl font-bold text-white">
                                    {history.sort((a, b) => a.rainfall_mm - b.rainfall_mm)[0]?.year}
                                    <span className="text-sm font-normal text-gray-500 ml-2">
                                        ({history.sort((a, b) => a.rainfall_mm - b.rainfall_mm)[0]?.rainfall_mm}mm)
                                    </span>
                                </p>
                            </div>
                        </div>
                    </div>

                    <div className="glass rounded-2xl p-6 border-l-4 border-yellow-500">
                        <div className="flex items-start gap-3">
                            <AlertCircle className="text-yellow-500 shrink-0 mt-1" size={20} />
                            <div>
                                <h4 className="text-white font-bold mb-1">Planning Tip</h4>
                                <p className="text-gray-400 text-sm">
                                    Based on the drier trend in {currentYearData?.year}, consider increasing your storage capacity by 15% to buffer against erratic monsoons.
                                </p>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default HistoricalRainfall;
