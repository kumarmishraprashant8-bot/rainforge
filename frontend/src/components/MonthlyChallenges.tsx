/**
 * Monthly Challenge Component
 * Gamified water-saving goals with progress tracking
 */

import { useState } from 'react';
import { Target, Droplets, Users, Clock, ChevronRight, Trophy, Zap, Gift } from 'lucide-react';

interface Challenge {
    id: string;
    title: string;
    description: string;
    target: number;
    current: number;
    unit: string;
    reward: string;
    participants: number;
    daysLeft: number;
    type: 'individual' | 'community';
    difficulty: 'easy' | 'medium' | 'hard';
}

const MonthlyChallenges = () => {
    const [activeTab, setActiveTab] = useState<'active' | 'completed'>('active');

    const challenges: Challenge[] = [
        {
            id: 'c1',
            title: 'February Water Warrior',
            description: 'Save 5,000 liters of water this month',
            target: 5000,
            current: 3200,
            unit: 'L',
            reward: '🏆 Gold Badge + 500 Credits',
            participants: 2341,
            daysLeft: 21,
            type: 'individual',
            difficulty: 'medium'
        },
        {
            id: 'c2',
            title: 'Monsoon Ready',
            description: 'Complete tank maintenance checklist',
            target: 5,
            current: 3,
            unit: 'tasks',
            reward: '🛠️ Maintenance Pro Badge',
            participants: 892,
            daysLeft: 14,
            type: 'individual',
            difficulty: 'easy'
        },
        {
            id: 'c3',
            title: 'City Challenge: Bangalore',
            description: 'Collectively save 1 Million liters',
            target: 1000000,
            current: 756000,
            unit: 'L',
            reward: '🌆 City Hero Badge',
            participants: 4523,
            daysLeft: 21,
            type: 'community',
            difficulty: 'hard'
        }
    ];

    const getDifficultyColor = (diff: string) => {
        switch (diff) {
            case 'easy': return 'bg-green-500/20 text-green-400';
            case 'medium': return 'bg-yellow-500/20 text-yellow-400';
            case 'hard': return 'bg-red-500/20 text-red-400';
            default: return 'bg-gray-500/20 text-gray-400';
        }
    };

    const getProgress = (current: number, target: number) => {
        return Math.min(100, (current / target) * 100);
    };

    const formatNumber = (num: number) => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}k`;
        return num.toString();
    };

    return (
        <div className="space-y-4">
            {/* Header */}
            <div className="flex items-center justify-between">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl">
                        <Target className="text-white" size={28} />
                    </div>
                    <div>
                        <h2 className="text-2xl font-black text-white">Monthly Challenges</h2>
                        <p className="text-gray-400">Complete challenges to earn rewards!</p>
                    </div>
                </div>
                <div className="flex gap-2">
                    <button
                        onClick={() => setActiveTab('active')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${activeTab === 'active'
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/10 text-gray-400'
                            }`}
                    >
                        Active
                    </button>
                    <button
                        onClick={() => setActiveTab('completed')}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${activeTab === 'completed'
                                ? 'bg-purple-500 text-white'
                                : 'bg-white/10 text-gray-400'
                            }`}
                    >
                        Completed
                    </button>
                </div>
            </div>

            {/* Challenge Cards */}
            <div className="space-y-4">
                {challenges.map((challenge) => (
                    <div
                        key={challenge.id}
                        className="glass rounded-2xl p-5 border border-white/10 hover:border-purple-500/30 transition-all group"
                    >
                        <div className="flex items-start justify-between mb-4">
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <h3 className="text-lg font-bold text-white">{challenge.title}</h3>
                                    <span className={`text-xs px-2 py-0.5 rounded-full ${getDifficultyColor(challenge.difficulty)}`}>
                                        {challenge.difficulty}
                                    </span>
                                    {challenge.type === 'community' && (
                                        <span className="text-xs px-2 py-0.5 rounded-full bg-cyan-500/20 text-cyan-400">
                                            <Users size={10} className="inline mr-1" />
                                            Community
                                        </span>
                                    )}
                                </div>
                                <p className="text-gray-400 text-sm">{challenge.description}</p>
                            </div>
                            <div className="text-right">
                                <div className="text-xs text-gray-500 flex items-center gap-1">
                                    <Clock size={12} />
                                    {challenge.daysLeft} days left
                                </div>
                            </div>
                        </div>

                        {/* Progress */}
                        <div className="mb-4">
                            <div className="flex justify-between text-sm mb-1">
                                <span className="text-gray-400">Progress</span>
                                <span className="text-white font-medium">
                                    {formatNumber(challenge.current)} / {formatNumber(challenge.target)} {challenge.unit}
                                </span>
                            </div>
                            <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                                <div
                                    className="h-full bg-gradient-to-r from-purple-500 to-pink-500 rounded-full transition-all"
                                    style={{ width: `${getProgress(challenge.current, challenge.target)}%` }}
                                />
                            </div>
                            <div className="text-right text-xs text-gray-500 mt-1">
                                {getProgress(challenge.current, challenge.target).toFixed(0)}% complete
                            </div>
                        </div>

                        {/* Footer */}
                        <div className="flex items-center justify-between">
                            <div className="flex items-center gap-4">
                                <div className="flex items-center gap-1 text-sm text-gray-400">
                                    <Users size={14} />
                                    {challenge.participants.toLocaleString()} joined
                                </div>
                                <div className="flex items-center gap-1 text-sm text-yellow-400">
                                    <Gift size={14} />
                                    {challenge.reward}
                                </div>
                            </div>
                            <button className="flex items-center gap-1 px-4 py-2 bg-purple-500/20 text-purple-400 rounded-xl text-sm font-medium group-hover:bg-purple-500 group-hover:text-white transition-all">
                                View Details
                                <ChevronRight size={16} />
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Stats */}
            <div className="grid grid-cols-3 gap-4">
                <div className="glass rounded-xl p-4 text-center">
                    <Trophy className="mx-auto text-yellow-400 mb-2" size={24} />
                    <div className="text-2xl font-bold text-white">12</div>
                    <div className="text-gray-500 text-xs">Challenges Won</div>
                </div>
                <div className="glass rounded-xl p-4 text-center">
                    <Zap className="mx-auto text-purple-400 mb-2" size={24} />
                    <div className="text-2xl font-bold text-white">2,450</div>
                    <div className="text-gray-500 text-xs">Total Credits</div>
                </div>
                <div className="glass rounded-xl p-4 text-center">
                    <Target className="mx-auto text-cyan-400 mb-2" size={24} />
                    <div className="text-2xl font-bold text-white">89%</div>
                    <div className="text-gray-500 text-xs">Success Rate</div>
                </div>
            </div>
        </div>
    );
};

export default MonthlyChallenges;
