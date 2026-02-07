/**
 * Rain Alert Component
 * Shows upcoming rain predictions and tank fill estimates
 */

import { useState, useEffect } from 'react';
import { Cloud, CloudRain, Droplets, Bell, X, TrendingUp, Clock } from 'lucide-react';

interface RainForecast {
    time: string;
    chance: number;
    intensity: 'light' | 'moderate' | 'heavy';
    expectedMm: number;
}

interface RainAlertProps {
    tankCapacity?: number;
    roofArea?: number;
}

const RainAlert = ({ tankCapacity = 5000, roofArea = 100 }: RainAlertProps) => {
    const [isVisible, setIsVisible] = useState(true);
    const [forecast, setForecast] = useState<RainForecast[]>([]);

    useEffect(() => {
        // Simulated forecast data
        setForecast([
            { time: '2 hours', chance: 85, intensity: 'moderate', expectedMm: 15 },
            { time: 'Tomorrow', chance: 60, intensity: 'light', expectedMm: 8 },
            { time: 'Day after', chance: 40, intensity: 'light', expectedMm: 5 },
        ]);
    }, []);

    const calculateCollection = (mm: number) => {
        // Collection = Roof Area (m²) × Rainfall (mm) × Runoff Coefficient (0.8)
        return Math.round(roofArea * mm * 0.8);
    };

    const getIntensityColor = (intensity: string) => {
        switch (intensity) {
            case 'heavy': return 'text-blue-400 bg-blue-500/20';
            case 'moderate': return 'text-cyan-400 bg-cyan-500/20';
            default: return 'text-gray-400 bg-gray-500/20';
        }
    };

    if (!isVisible || forecast.length === 0) return null;

    const nextRain = forecast[0];
    const expectedCollection = calculateCollection(nextRain.expectedMm);
    const fillPercent = Math.min(100, (expectedCollection / tankCapacity) * 100);

    return (
        <div className="fixed bottom-4 right-4 z-40 max-w-sm animate-slideUp">
            <div className="glass rounded-2xl p-4 border border-cyan-500/30 shadow-xl shadow-cyan-500/10">
                {/* Header */}
                <div className="flex items-start justify-between mb-3">
                    <div className="flex items-center gap-2">
                        <div className="p-2 bg-cyan-500/20 rounded-xl">
                            <CloudRain className="text-cyan-400" size={20} />
                        </div>
                        <div>
                            <h4 className="text-white font-bold">Rain Alert! 🌧️</h4>
                            <p className="text-gray-400 text-xs">Get ready to collect water</p>
                        </div>
                    </div>
                    <button
                        onClick={() => setIsVisible(false)}
                        className="text-gray-500 hover:text-white"
                    >
                        <X size={18} />
                    </button>
                </div>

                {/* Main Prediction */}
                <div className="bg-gradient-to-r from-cyan-500/10 to-blue-500/10 rounded-xl p-3 mb-3">
                    <div className="flex items-center justify-between mb-2">
                        <div className="flex items-center gap-2">
                            <Clock size={14} className="text-gray-400" />
                            <span className="text-gray-300 text-sm">In {nextRain.time}</span>
                        </div>
                        <span className={`text-xs px-2 py-1 rounded-full ${getIntensityColor(nextRain.intensity)}`}>
                            {nextRain.intensity.charAt(0).toUpperCase() + nextRain.intensity.slice(1)} rain
                        </span>
                    </div>
                    <div className="flex items-end justify-between">
                        <div>
                            <div className="text-3xl font-black text-cyan-400">{nextRain.chance}%</div>
                            <div className="text-gray-500 text-xs">Rain probability</div>
                        </div>
                        <div className="text-right">
                            <div className="text-xl font-bold text-white">{expectedCollection}L</div>
                            <div className="text-gray-500 text-xs">Expected collection</div>
                        </div>
                    </div>
                </div>

                {/* Tank Fill Preview */}
                <div className="mb-3">
                    <div className="flex justify-between text-xs text-gray-400 mb-1">
                        <span>Tank Fill Estimate</span>
                        <span>{fillPercent.toFixed(0)}%</span>
                    </div>
                    <div className="h-2 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-cyan-500 to-blue-500 rounded-full transition-all"
                            style={{ width: `${fillPercent}%` }}
                        />
                    </div>
                </div>

                {/* Quick Actions */}
                <div className="flex gap-2">
                    <button className="flex-1 flex items-center justify-center gap-2 py-2 bg-white/10 rounded-xl text-white text-sm hover:bg-white/20 transition-colors">
                        <Bell size={14} />
                        Remind Me
                    </button>
                    <button className="flex-1 flex items-center justify-center gap-2 py-2 bg-cyan-500 rounded-xl text-white text-sm font-medium hover:bg-cyan-600 transition-colors">
                        <Droplets size={14} />
                        Prepare Tank
                    </button>
                </div>

                {/* Upcoming */}
                <div className="mt-3 pt-3 border-t border-white/10">
                    <div className="text-xs text-gray-500 mb-2">Next 3 days</div>
                    <div className="flex gap-2">
                        {forecast.map((f, i) => (
                            <div key={i} className="flex-1 text-center">
                                <div className="text-lg font-bold text-white">{f.chance}%</div>
                                <div className="text-xs text-gray-500">{f.time}</div>
                            </div>
                        ))}
                    </div>
                </div>
            </div>
        </div>
    );
};

export default RainAlert;
