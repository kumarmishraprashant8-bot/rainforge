/**
 * Community Leaderboard Page
 * Regional water conservation rankings and achievements
 */

import { useState, useEffect } from 'react';
import {
    Trophy, Droplets, Users, MapPin, TrendingUp, Award,
    Search, ChevronUp, ChevronDown, Crown, Medal, Star,
    Share2, Target, Zap
} from 'lucide-react';
import ShareButtons from '../../components/ShareButtons';
import Confetti from '../../components/Confetti';

interface LeaderboardEntry {
    rank: number;
    userId: string;
    name: string;
    city: string;
    waterSaved: number;
    co2Offset: number;
    badges: number;
    change: number; // rank change from last week
    avatar?: string;
}

interface CityStats {
    city: string;
    state: string;
    totalUsers: number;
    totalWaterSaved: number;
    avgPerUser: number;
    rank: number;
}

const CommunityPage = () => {
    const [view, setView] = useState<'individual' | 'city'>('individual');
    const [timeRange, setTimeRange] = useState<'week' | 'month' | 'alltime'>('month');
    const [searchQuery, setSearchQuery] = useState('');
    const [showConfetti, setShowConfetti] = useState(false);

    // Trigger confetti on first visit (simulating you're in top 10)
    useEffect(() => {
        const hasSeenConfetti = sessionStorage.getItem('community-confetti');
        if (!hasSeenConfetti) {
            setTimeout(() => setShowConfetti(true), 500);
            sessionStorage.setItem('community-confetti', 'true');
            setTimeout(() => setShowConfetti(false), 4000);
        }
    }, []);

    // Dynamic leaderboard data based on time range
    const getMultiplier = () => {
        switch (timeRange) {
            case 'week': return 0.25;
            case 'alltime': return 12;
            default: return 1;
        }
    };

    const multiplier = getMultiplier();

    const individualLeaderboard: LeaderboardEntry[] = [
        { rank: 1, userId: 'u1', name: 'Rahul Sharma', city: 'New Delhi', waterSaved: Math.round(485000 * multiplier), co2Offset: Math.round(243 * multiplier), badges: 8, change: 0 },
        { rank: 2, userId: 'u2', name: 'Priya Patel', city: 'Mumbai', waterSaved: Math.round(412000 * multiplier), co2Offset: Math.round(206 * multiplier), badges: 7, change: 2 },
        { rank: 3, userId: 'u3', name: 'Arjun Reddy', city: 'Hyderabad', waterSaved: Math.round(398000 * multiplier), co2Offset: Math.round(199 * multiplier), badges: 6, change: -1 },
        { rank: 4, userId: 'u4', name: 'Sneha Gupta', city: 'Bangalore', waterSaved: Math.round(356000 * multiplier), co2Offset: Math.round(178 * multiplier), badges: 5, change: 1 },
        { rank: 5, userId: 'u5', name: 'Vikram Singh', city: 'Jaipur', waterSaved: Math.round(324000 * multiplier), co2Offset: Math.round(162 * multiplier), badges: 5, change: -2 },
        { rank: 6, userId: 'u6', name: 'Ananya Iyer', city: 'Chennai', waterSaved: Math.round(298000 * multiplier), co2Offset: Math.round(149 * multiplier), badges: 4, change: 0 },
        { rank: 7, userId: 'u7', name: 'Karan Mehta', city: 'Pune', waterSaved: Math.round(275000 * multiplier), co2Offset: Math.round(138 * multiplier), badges: 4, change: 3 },
        { rank: 8, userId: 'u8', name: 'Neha Verma', city: 'Kolkata', waterSaved: Math.round(256000 * multiplier), co2Offset: Math.round(128 * multiplier), badges: 3, change: -1 },
        { rank: 9, userId: 'u9', name: 'Rohit Kumar', city: 'Ahmedabad', waterSaved: Math.round(234000 * multiplier), co2Offset: Math.round(117 * multiplier), badges: 3, change: 0 },
        { rank: 10, userId: 'u10', name: 'Divya Nair', city: 'Kochi', waterSaved: Math.round(212000 * multiplier), co2Offset: Math.round(106 * multiplier), badges: 3, change: 2 },
    ].sort((a, b) => b.waterSaved - a.waterSaved).map((entry, idx) => ({ ...entry, rank: idx + 1 }));

    const cityLeaderboard: CityStats[] = [
        { city: 'Bangalore', state: 'Karnataka', totalUsers: 4523, totalWaterSaved: Math.round(125000000 * multiplier), avgPerUser: Math.round(27640 * multiplier), rank: 1 },
        { city: 'Chennai', state: 'Tamil Nadu', totalUsers: 3891, totalWaterSaved: Math.round(98000000 * multiplier), avgPerUser: Math.round(25189 * multiplier), rank: 2 },
        { city: 'Mumbai', state: 'Maharashtra', totalUsers: 5234, totalWaterSaved: Math.round(112000000 * multiplier), avgPerUser: Math.round(21401 * multiplier), rank: 3 },
        { city: 'New Delhi', state: 'Delhi', totalUsers: 4102, totalWaterSaved: Math.round(85000000 * multiplier), avgPerUser: Math.round(20722 * multiplier), rank: 4 },
        { city: 'Hyderabad', state: 'Telangana', totalUsers: 2987, totalWaterSaved: Math.round(58000000 * multiplier), avgPerUser: Math.round(19418 * multiplier), rank: 5 },
        { city: 'Pune', state: 'Maharashtra', totalUsers: 2456, totalWaterSaved: Math.round(45000000 * multiplier), avgPerUser: Math.round(18322 * multiplier), rank: 6 },
        { city: 'Jaipur', state: 'Rajasthan', totalUsers: 1876, totalWaterSaved: Math.round(32000000 * multiplier), avgPerUser: Math.round(17057 * multiplier), rank: 7 },
        { city: 'Kolkata', state: 'West Bengal', totalUsers: 2134, totalWaterSaved: Math.round(35000000 * multiplier), avgPerUser: Math.round(16401 * multiplier), rank: 8 },
    ].sort((a, b) => b.totalWaterSaved - a.totalWaterSaved).map((entry, idx) => ({ ...entry, rank: idx + 1 }));

    const getRankIcon = (rank: number) => {
        if (rank === 1) return <Crown className="text-yellow-400" size={24} />;
        if (rank === 2) return <Medal className="text-gray-300" size={24} />;
        if (rank === 3) return <Medal className="text-amber-600" size={24} />;
        return <span className="text-gray-400 font-bold">#{rank}</span>;
    };

    const getRankBg = (rank: number) => {
        if (rank === 1) return 'bg-gradient-to-r from-yellow-500/20 to-amber-500/20 border-yellow-500/30';
        if (rank === 2) return 'bg-gradient-to-r from-gray-400/20 to-gray-500/20 border-gray-400/30';
        if (rank === 3) return 'bg-gradient-to-r from-amber-600/20 to-orange-600/20 border-amber-600/30';
        return 'bg-white/5 border-transparent hover:border-white/10';
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            {/* Confetti Celebration */}
            <Confetti isActive={showConfetti} />

            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-3 mb-4">
                        <div className="p-3 bg-gradient-to-r from-yellow-500 to-orange-500 rounded-2xl">
                            <Trophy className="text-white" size={32} />
                        </div>
                        <h1 className="text-4xl font-black text-white">Community Leaderboard</h1>
                    </div>
                    <p className="text-gray-400 text-lg">See how you rank among water conservation champions</p>
                </div>

                {/* Global Stats */}
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-4">
                    <div className="glass rounded-2xl p-5 text-center">
                        <div className="text-4xl mb-2">💧</div>
                        <div className="text-3xl font-black text-cyan-400">2.4B</div>
                        <div className="text-gray-400 text-sm">Liters Saved</div>
                    </div>
                    <div className="glass rounded-2xl p-5 text-center">
                        <div className="text-4xl mb-2">🏠</div>
                        <div className="text-3xl font-black text-green-400">45K+</div>
                        <div className="text-gray-400 text-sm">Active Users</div>
                    </div>
                    <div className="glass rounded-2xl p-5 text-center">
                        <div className="text-4xl mb-2">🌍</div>
                        <div className="text-3xl font-black text-purple-400">1.2M</div>
                        <div className="text-gray-400 text-sm">kg CO₂ Offset</div>
                    </div>
                    <div className="glass rounded-2xl p-5 text-center">
                        <div className="text-4xl mb-2">🏆</div>
                        <div className="text-3xl font-black text-yellow-400">156</div>
                        <div className="text-gray-400 text-sm">Cities Active</div>
                    </div>
                </div>

                {/* View Toggle & Filters */}
                <div className="flex flex-col sm:flex-row justify-between gap-4">
                    <div className="flex gap-2">
                        <button
                            onClick={() => setView('individual')}
                            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${view === 'individual'
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            <Users size={18} /> Individuals
                        </button>
                        <button
                            onClick={() => setView('city')}
                            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium transition-all ${view === 'city'
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            <MapPin size={18} /> Cities
                        </button>
                    </div>

                    <div className="flex gap-2">
                        {(['week', 'month', 'alltime'] as const).map(range => (
                            <button
                                key={range}
                                onClick={() => setTimeRange(range)}
                                className={`px-3 py-2 rounded-lg text-sm font-medium transition-all ${timeRange === range
                                    ? 'bg-cyan-500/20 text-cyan-400 border border-cyan-500/30'
                                    : 'bg-white/5 text-gray-400 hover:text-white'
                                    }`}
                            >
                                {range === 'week' ? 'This Week' : range === 'month' ? 'This Month' : 'All Time'}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Search */}
                <div className="relative">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder={view === 'individual' ? 'Search by name...' : 'Search by city...'}
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                    />
                </div>

                {/* Individual Leaderboard */}
                {view === 'individual' && (
                    <div className="glass rounded-2xl overflow-hidden">
                        <div className="p-4 border-b border-white/10">
                            <h3 className="text-lg font-bold text-white">Top Water Savers</h3>
                        </div>
                        <div className="divide-y divide-white/5">
                            {individualLeaderboard
                                .filter(e => e.name.toLowerCase().includes(searchQuery.toLowerCase()))
                                .map((entry) => (
                                    <div
                                        key={entry.userId}
                                        className={`flex items-center gap-4 p-4 border-l-4 transition-all ${getRankBg(entry.rank)}`}
                                    >
                                        {/* Rank */}
                                        <div className="w-12 flex justify-center">
                                            {getRankIcon(entry.rank)}
                                        </div>

                                        {/* Avatar & Name */}
                                        <div className="flex items-center gap-3 flex-1">
                                            <div className="w-12 h-12 rounded-full bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-white font-bold text-lg">
                                                {entry.name.charAt(0)}
                                            </div>
                                            <div>
                                                <div className="text-white font-semibold">{entry.name}</div>
                                                <div className="text-gray-500 text-sm flex items-center gap-1">
                                                    <MapPin size={12} /> {entry.city}
                                                </div>
                                            </div>
                                        </div>

                                        {/* Stats */}
                                        <div className="hidden md:flex items-center gap-6">
                                            <div className="text-center">
                                                <div className="text-cyan-400 font-bold">{(entry.waterSaved / 1000).toFixed(0)}k L</div>
                                                <div className="text-gray-500 text-xs">Water Saved</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-green-400 font-bold">{entry.co2Offset} kg</div>
                                                <div className="text-gray-500 text-xs">CO₂ Offset</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-purple-400 font-bold flex items-center gap-1">
                                                    <Star size={14} /> {entry.badges}
                                                </div>
                                                <div className="text-gray-500 text-xs">Badges</div>
                                            </div>
                                        </div>

                                        {/* Rank Change */}
                                        <div className={`flex items-center gap-1 ${entry.change > 0 ? 'text-green-400' : entry.change < 0 ? 'text-red-400' : 'text-gray-500'
                                            }`}>
                                            {entry.change > 0 ? <ChevronUp size={18} /> : entry.change < 0 ? <ChevronDown size={18} /> : <span>-</span>}
                                            {entry.change !== 0 && <span className="text-sm font-medium">{Math.abs(entry.change)}</span>}
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>
                )}

                {/* City Leaderboard */}
                {view === 'city' && (
                    <div className="glass rounded-2xl overflow-hidden">
                        <div className="p-4 border-b border-white/10">
                            <h3 className="text-lg font-bold text-white">Top Cities</h3>
                        </div>
                        <div className="divide-y divide-white/5">
                            {cityLeaderboard
                                .filter(c => c.city.toLowerCase().includes(searchQuery.toLowerCase()))
                                .map((city) => (
                                    <div
                                        key={city.city}
                                        className={`flex items-center gap-4 p-4 border-l-4 transition-all ${getRankBg(city.rank)}`}
                                    >
                                        {/* Rank */}
                                        <div className="w-12 flex justify-center">
                                            {getRankIcon(city.rank)}
                                        </div>

                                        {/* City Info */}
                                        <div className="flex-1">
                                            <div className="text-white font-semibold text-lg">{city.city}</div>
                                            <div className="text-gray-500 text-sm">{city.state}</div>
                                        </div>

                                        {/* Stats */}
                                        <div className="hidden md:flex items-center gap-8">
                                            <div className="text-center">
                                                <div className="text-cyan-400 font-bold">{(city.totalWaterSaved / 1000000).toFixed(0)}M L</div>
                                                <div className="text-gray-500 text-xs">Total Saved</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-green-400 font-bold">{city.totalUsers.toLocaleString()}</div>
                                                <div className="text-gray-500 text-xs">Users</div>
                                            </div>
                                            <div className="text-center">
                                                <div className="text-purple-400 font-bold">{(city.avgPerUser / 1000).toFixed(1)}k L</div>
                                                <div className="text-gray-500 text-xs">Avg/User</div>
                                            </div>
                                        </div>
                                    </div>
                                ))}
                        </div>
                    </div>
                )}

                {/* Your Rank Card */}
                <div className="glass rounded-2xl p-6 bg-gradient-to-r from-purple-500/10 to-pink-500/10 border border-purple-500/20">
                    <div className="flex flex-col md:flex-row items-center justify-between gap-4">
                        <div className="flex items-center gap-4">
                            <div className="w-16 h-16 rounded-2xl bg-gradient-to-br from-purple-500 to-pink-500 flex items-center justify-center text-white font-bold text-2xl">
                                D
                            </div>
                            <div>
                                <div className="text-gray-400 text-sm">Your Current Rank</div>
                                <div className="text-3xl font-black text-white">#127</div>
                                <div className="text-green-400 text-sm flex items-center gap-1">
                                    <TrendingUp size={14} /> Up 15 from last week
                                </div>
                            </div>
                        </div>
                        <div className="flex flex-col sm:flex-row gap-3 items-center">
                            <ShareButtons
                                title="My RainForge Ranking"
                                text="I'm ranked #127 on the RainForge Community Leaderboard! Join me in saving water 💧"
                            />
                            <button
                                onClick={() => setShowConfetti(true)}
                                className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-purple-500 to-pink-500 rounded-xl text-white font-semibold hover:scale-105 transition-transform"
                            >
                                <Target size={18} />
                                Celebrate! 🎉
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default CommunityPage;
