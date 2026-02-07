/**
 * Streak Tracker Component
 * Gamification - track consecutive days of water conservation
 */

import { useState, useEffect } from 'react';
import { Flame, Calendar, Trophy, Star, Gift, Zap } from 'lucide-react';

interface StreakData {
    currentStreak: number;
    longestStreak: number;
    totalDays: number;
    weekProgress: boolean[];
    nextMilestone: number;
    rewards: { day: number; reward: string; claimed: boolean }[];
}

const StreakTracker = () => {
    const [streak, setStreak] = useState<StreakData>({
        currentStreak: 7,
        longestStreak: 14,
        totalDays: 45,
        weekProgress: [true, true, true, true, true, true, true],
        nextMilestone: 10,
        rewards: [
            { day: 7, reward: '🏅 Bronze Badge', claimed: true },
            { day: 14, reward: '🥈 Silver Badge', claimed: false },
            { day: 30, reward: '🥇 Gold Badge + 100 Credits', claimed: false },
        ]
    });

    const [showCelebration, setShowCelebration] = useState(false);

    useEffect(() => {
        // Check if it's a milestone day
        if (streak.currentStreak === 7 || streak.currentStreak === 14 || streak.currentStreak === 30) {
            setShowCelebration(true);
            setTimeout(() => setShowCelebration(false), 3000);
        }
    }, [streak.currentStreak]);

    const getFlameColor = () => {
        if (streak.currentStreak >= 30) return 'from-purple-500 to-pink-500';
        if (streak.currentStreak >= 14) return 'from-orange-500 to-red-500';
        if (streak.currentStreak >= 7) return 'from-yellow-500 to-orange-500';
        return 'from-gray-500 to-gray-600';
    };

    const days = ['M', 'T', 'W', 'T', 'F', 'S', 'S'];

    return (
        <div className="glass rounded-2xl p-6 bg-gradient-to-r from-orange-500/10 to-red-500/10 border border-orange-500/20">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className={`p-3 bg-gradient-to-r ${getFlameColor()} rounded-xl shadow-lg`}>
                        <Flame className="text-white" size={28} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Daily Streak</h3>
                        <p className="text-gray-400 text-sm">Keep saving water every day!</p>
                    </div>
                </div>
                {showCelebration && (
                    <div className="px-3 py-1 bg-yellow-500/20 rounded-full text-yellow-400 text-sm animate-bounce">
                        🎉 New Milestone!
                    </div>
                )}
            </div>

            {/* Main Streak Display */}
            <div className="text-center mb-6">
                <div className="relative inline-block">
                    <div className={`text-7xl font-black bg-gradient-to-r ${getFlameColor()} bg-clip-text text-transparent`}>
                        {streak.currentStreak}
                    </div>
                    <Flame className="absolute -top-2 -right-4 text-orange-400 animate-pulse" size={24} />
                </div>
                <div className="text-gray-400 mt-1">day streak 🔥</div>
            </div>

            {/* Week Progress */}
            <div className="mb-6">
                <div className="text-sm text-gray-400 mb-2">This Week</div>
                <div className="flex justify-between gap-2">
                    {days.map((day, i) => (
                        <div key={i} className="flex-1 text-center">
                            <div
                                className={`w-10 h-10 mx-auto rounded-xl flex items-center justify-center mb-1 transition-all ${streak.weekProgress[i]
                                        ? 'bg-gradient-to-r from-green-500 to-emerald-500 text-white'
                                        : 'bg-white/10 text-gray-500'
                                    }`}
                            >
                                {streak.weekProgress[i] ? '✓' : day}
                            </div>
                            <div className="text-xs text-gray-500">{day}</div>
                        </div>
                    ))}
                </div>
            </div>

            {/* Stats Row */}
            <div className="grid grid-cols-3 gap-3 mb-6">
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <Trophy className="mx-auto text-yellow-400 mb-1" size={20} />
                    <div className="text-lg font-bold text-white">{streak.longestStreak}</div>
                    <div className="text-xs text-gray-500">Best Streak</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <Calendar className="mx-auto text-cyan-400 mb-1" size={20} />
                    <div className="text-lg font-bold text-white">{streak.totalDays}</div>
                    <div className="text-xs text-gray-500">Total Days</div>
                </div>
                <div className="bg-white/5 rounded-xl p-3 text-center">
                    <Star className="mx-auto text-purple-400 mb-1" size={20} />
                    <div className="text-lg font-bold text-white">{streak.nextMilestone - streak.currentStreak}</div>
                    <div className="text-xs text-gray-500">To Next Badge</div>
                </div>
            </div>

            {/* Upcoming Rewards */}
            <div>
                <div className="text-sm text-gray-400 mb-2 flex items-center gap-2">
                    <Gift size={14} />
                    Upcoming Rewards
                </div>
                <div className="space-y-2">
                    {streak.rewards.map((r, i) => (
                        <div
                            key={i}
                            className={`flex items-center justify-between p-3 rounded-xl transition-all ${r.claimed
                                    ? 'bg-green-500/10 border border-green-500/20'
                                    : streak.currentStreak >= r.day
                                        ? 'bg-yellow-500/10 border border-yellow-500/20 animate-pulse'
                                        : 'bg-white/5'
                                }`}
                        >
                            <div className="flex items-center gap-3">
                                <div className={`text-2xl ${r.claimed ? 'grayscale-0' : 'grayscale opacity-50'}`}>
                                    {r.reward.split(' ')[0]}
                                </div>
                                <div>
                                    <div className="text-white text-sm font-medium">{r.reward}</div>
                                    <div className="text-gray-500 text-xs">Day {r.day}</div>
                                </div>
                            </div>
                            {r.claimed ? (
                                <span className="text-green-400 text-xs">Claimed ✓</span>
                            ) : streak.currentStreak >= r.day ? (
                                <button className="px-3 py-1 bg-yellow-500 text-black text-xs font-bold rounded-lg">
                                    Claim!
                                </button>
                            ) : (
                                <span className="text-gray-500 text-xs">{r.day - streak.currentStreak} days</span>
                            )}
                        </div>
                    ))}
                </div>
            </div>
        </div>
    );
};

export default StreakTracker;
