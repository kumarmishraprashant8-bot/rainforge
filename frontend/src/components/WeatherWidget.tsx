/**
 * Weather Widget Component
 * Real-time weather and rain alerts
 */

import { useState, useEffect } from 'react';
import { Cloud, CloudRain, Sun, Wind, Droplets, AlertTriangle, TrendingUp } from 'lucide-react';
import weatherService, { WeatherData, RainAlert, WEATHER_ICONS } from '../services/weatherService';

interface WeatherWidgetProps {
    roofArea?: number;
    compact?: boolean;
}

const WeatherWidget = ({ roofArea = 120, compact = false }: WeatherWidgetProps) => {
    const [weather, setWeather] = useState<WeatherData | null>(null);
    const [alerts, setAlerts] = useState<RainAlert[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        const fetchWeather = async () => {
            try {
                const data = await weatherService.getCurrentWeather(28.6139, 77.2090);
                const alertData = await weatherService.getRainAlerts(28.6139, 77.2090);
                setWeather(data);
                setAlerts(alertData);
            } finally {
                setLoading(false);
            }
        };
        fetchWeather();
        const interval = setInterval(fetchWeather, 5 * 60 * 1000); // Refresh every 5 min
        return () => clearInterval(interval);
    }, []);

    if (loading) {
        return (
            <div className="glass rounded-2xl p-6 animate-pulse">
                <div className="h-20 bg-white/10 rounded-xl" />
            </div>
        );
    }

    if (!weather) return null;

    const expectedCollection = weather.rainfall_today_mm > 0
        ? weatherService.calculateExpectedCollection(weather.rainfall_today_mm, roofArea)
        : 0;

    const WeatherIcon = {
        sunny: Sun,
        cloudy: Cloud,
        rainy: CloudRain,
        stormy: CloudRain
    }[weather.condition];

    if (compact) {
        return (
            <div className="flex items-center gap-3 px-4 py-2 bg-white/5 rounded-xl">
                <span className="text-2xl">{WEATHER_ICONS[weather.condition]}</span>
                <div>
                    <span className="text-white font-semibold">{weather.temperature}°C</span>
                    {weather.rainfall_today_mm > 0 && (
                        <span className="text-cyan-400 ml-2 text-sm">
                            +{expectedCollection}L today
                        </span>
                    )}
                </div>
            </div>
        );
    }

    return (
        <div className="glass rounded-2xl p-6 space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <h3 className="text-lg font-bold text-white flex items-center gap-2">
                    <Cloud className="text-cyan-400" size={20} />
                    Weather & Rain Alerts
                </h3>
                <span className="text-xs text-gray-500">
                    Updated {new Date(weather.last_updated).toLocaleTimeString()}
                </span>
            </div>

            {/* Main Weather */}
            <div className="flex items-center gap-6">
                <div className="text-6xl">{WEATHER_ICONS[weather.condition]}</div>
                <div>
                    <div className="text-4xl font-black text-white">{weather.temperature}°C</div>
                    <div className="text-gray-400 capitalize">{weather.condition}</div>
                    <div className="text-sm text-gray-500">{weather.location}</div>
                </div>
            </div>

            {/* Stats Grid */}
            <div className="grid grid-cols-3 gap-4">
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <Droplets className="text-blue-400 mx-auto mb-1" size={18} />
                    <div className="text-white font-semibold">{weather.humidity}%</div>
                    <div className="text-xs text-gray-500">Humidity</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <Wind className="text-gray-400 mx-auto mb-1" size={18} />
                    <div className="text-white font-semibold">{weather.wind_speed_kmh} km/h</div>
                    <div className="text-xs text-gray-500">Wind</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <CloudRain className="text-cyan-400 mx-auto mb-1" size={18} />
                    <div className="text-white font-semibold">{weather.rainfall_today_mm} mm</div>
                    <div className="text-xs text-gray-500">Rain Today</div>
                </div>
            </div>

            {/* Collection Estimate */}
            {weather.rainfall_today_mm > 0 && (
                <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-xl p-4">
                    <div className="flex items-center gap-3">
                        <div className="p-2 bg-cyan-500/20 rounded-lg">
                            <TrendingUp className="text-cyan-400" size={20} />
                        </div>
                        <div>
                            <p className="text-white font-semibold">
                                🎉 Your tank is collecting water!
                            </p>
                            <p className="text-cyan-400 text-sm">
                                Estimated collection today: <strong>{expectedCollection.toLocaleString()} L</strong>
                            </p>
                        </div>
                    </div>
                </div>
            )}

            {/* Rain Alerts */}
            {alerts.length > 0 && (
                <div className="space-y-2">
                    {alerts.map((alert, idx) => (
                        <div
                            key={idx}
                            className="bg-yellow-500/10 border border-yellow-500/30 rounded-xl p-4 flex items-start gap-3"
                        >
                            <AlertTriangle className="text-yellow-400 flex-shrink-0" size={20} />
                            <div>
                                <p className="text-white font-medium">{alert.message}</p>
                                <p className="text-yellow-400 text-sm mt-1">
                                    Expected in {Math.round((new Date(alert.start_time).getTime() - Date.now()) / (1000 * 60 * 60))} hours
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            )}

            {/* Forecast */}
            <div className="pt-4 border-t border-white/10">
                <div className="flex items-center justify-between text-sm">
                    <span className="text-gray-400">Next 24h forecast:</span>
                    <span className="text-cyan-400 font-semibold">
                        {weather.rainfall_forecast_mm > 0
                            ? `${weather.rainfall_forecast_mm}mm expected`
                            : 'No rain expected'
                        }
                    </span>
                </div>
            </div>
        </div>
    );
};

export default WeatherWidget;
