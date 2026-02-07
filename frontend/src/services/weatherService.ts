/**
 * Weather Service
 * Real-time weather data and rain alerts
 */

export interface WeatherData {
    location: string;
    temperature: number;
    humidity: number;
    condition: 'sunny' | 'cloudy' | 'rainy' | 'stormy';
    rainfall_today_mm: number;
    rainfall_forecast_mm: number;
    wind_speed_kmh: number;
    last_updated: string;
}

export interface RainAlert {
    type: 'light' | 'moderate' | 'heavy' | 'storm';
    message: string;
    expected_collection_liters: number;
    start_time: string;
    duration_hours: number;
}

export interface MonsoonForecast {
    onset_date: string;
    expected_rainfall_mm: number;
    status: 'normal' | 'above_normal' | 'below_normal';
    weekly_forecast: { week: string; rainfall_mm: number }[];
}

// Weather condition icons
export const WEATHER_ICONS: Record<string, string> = {
    sunny: '☀️',
    cloudy: '⛅',
    rainy: '🌧️',
    stormy: '⛈️'
};

class WeatherService {
    private baseUrl = 'https://api.openweathermap.org/data/2.5';
    private apiKey = 'demo'; // Would be env variable in production

    async getCurrentWeather(lat: number, lon: number): Promise<WeatherData> {
        // Demo data - in production would call OpenWeather API
        const conditions: WeatherData['condition'][] = ['sunny', 'cloudy', 'rainy', 'stormy'];
        const randomCondition = conditions[Math.floor(Math.random() * conditions.length)];

        return {
            location: 'New Delhi',
            temperature: 28 + Math.floor(Math.random() * 10),
            humidity: 60 + Math.floor(Math.random() * 30),
            condition: randomCondition,
            rainfall_today_mm: randomCondition === 'rainy' ? 15 + Math.floor(Math.random() * 30) : 0,
            rainfall_forecast_mm: Math.floor(Math.random() * 50),
            wind_speed_kmh: 5 + Math.floor(Math.random() * 20),
            last_updated: new Date().toISOString()
        };
    }

    async getRainAlerts(lat: number, lon: number): Promise<RainAlert[]> {
        // Demo alerts
        const hasAlert = Math.random() > 0.5;
        if (!hasAlert) return [];

        return [{
            type: 'moderate',
            message: 'Rain expected in next 2 hours! Your tank could collect ~200L',
            expected_collection_liters: 200,
            start_time: new Date(Date.now() + 2 * 60 * 60 * 1000).toISOString(),
            duration_hours: 3
        }];
    }

    async getMonsoonForecast(state: string): Promise<MonsoonForecast> {
        return {
            onset_date: '2026-06-15',
            expected_rainfall_mm: 850,
            status: 'normal',
            weekly_forecast: [
                { week: 'Week 1', rainfall_mm: 45 },
                { week: 'Week 2', rainfall_mm: 80 },
                { week: 'Week 3', rainfall_mm: 120 },
                { week: 'Week 4', rainfall_mm: 95 }
            ]
        };
    }

    async getHistoricalRainfall(location: string): Promise<{ year: number; rainfall_mm: number; average_mm: number }[]> {
        // Mock data for 5-year history
        const currentYear = new Date().getFullYear();
        const baseRainfall = 800; // Base mm for the region

        return Array.from({ length: 5 }, (_, i) => {
            const year = currentYear - 5 + i;
            const variation = (Math.random() * 200) - 100; // +/- 100mm random variation
            return {
                year,
                rainfall_mm: Math.round(baseRainfall + variation),
                average_mm: baseRainfall
            };
        });
    }

    calculateExpectedCollection(rainfall_mm: number, roofArea: number, runoffCoeff: number = 0.85): number {
        return Math.round(rainfall_mm * roofArea * runoffCoeff * 0.9);
    }
}

export const weatherService = new WeatherService();
export default weatherService;
