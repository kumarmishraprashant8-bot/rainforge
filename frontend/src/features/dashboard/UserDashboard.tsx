/**
 * User Dashboard Page
 * Showcases all advanced features in one place
 */

import { useState } from 'react';
import {
    Home, Droplets, Target, Wrench, Calculator, FileText,
    Trophy, Bell, ChevronRight, User
} from 'lucide-react';
import RainAlert from '../../components/RainAlert';
import StreakTracker from '../../components/StreakTracker';
import MonthlyChallenges from '../../components/MonthlyChallenges';
import MaintenanceReminders from '../../components/MaintenanceReminders';
import ROICalculator from '../../components/ROICalculator';
import WaterBillScanner from '../../components/WaterBillScanner';
import WaterQualityLog from '../quality/WaterQualityLog';
import HistoricalRainfall from '../../components/HistoricalRainfall';

type TabType = 'overview' | 'challenges' | 'maintenance' | 'calculator' | 'scanner' | 'quality' | 'history';

const UserDashboard = () => {
    const [activeTab, setActiveTab] = useState<TabType>('overview');

    const tabs = [
        { id: 'overview', label: 'Overview', icon: Home },
        { id: 'quality', label: 'Water Quality', icon: FileText }, // Reusing icon for now
        { id: 'history', label: 'Rain History', icon: Home }, // Reusing icon for now
        { id: 'challenges', label: 'Challenges', icon: Target },
        { id: 'maintenance', label: 'Maintenance', icon: Wrench },
        { id: 'calculator', label: 'ROI Calculator', icon: Calculator },
        { id: 'scanner', label: 'Bill Scanner', icon: FileText },
    ];

    // ... (keep existing render logic for tabs)

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            {/* Rain Alert Popup */}
            <RainAlert tankCapacity={5000} roofArea={100} />

            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                {/* Header */}
                <div className="flex items-center justify-between mb-8">
                    <div className="flex items-center gap-4">
                        <div className="w-16 h-16 rounded-2xl bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-white text-2xl font-bold">
                            D
                        </div>
                        <div>
                            <h1 className="text-3xl font-black text-white">Welcome Back! 👋</h1>
                            <p className="text-gray-400">Your water conservation dashboard</p>
                        </div>
                    </div>
                    <div className="flex items-center gap-3">
                        <button className="p-3 bg-white/10 rounded-xl text-white hover:bg-white/20 relative">
                            <Bell size={20} />
                            <span className="absolute -top-1 -right-1 w-5 h-5 bg-red-500 rounded-full text-xs flex items-center justify-center">3</span>
                        </button>
                        <button className="flex items-center gap-2 px-4 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-xl text-white font-medium">
                            <User size={18} />
                            Profile
                        </button>
                    </div>
                </div>

                {/* Tab Navigation */}
                <div className="flex gap-2 mb-8 overflow-x-auto pb-2">
                    {tabs.map((tab) => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as TabType)}
                            className={`flex items-center gap-2 px-4 py-3 rounded-xl font-medium transition-all whitespace-nowrap ${activeTab === tab.id
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                                : 'bg-white/10 text-gray-400 hover:text-white'
                                }`}
                        >
                            <tab.icon size={18} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Overview Tab */}
                {activeTab === 'overview' && (
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Streak Tracker */}
                        <StreakTracker />

                        {/* Quick Stats */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-xl font-bold text-white mb-4">Quick Stats</h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 rounded-xl p-4 text-center">
                                    <Droplets className="mx-auto text-cyan-400 mb-2" size={28} />
                                    <div className="text-2xl font-black text-white">245k L</div>
                                    <div className="text-gray-500 text-sm">Total Saved</div>
                                </div>
                                <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 rounded-xl p-4 text-center">
                                    <Trophy className="mx-auto text-green-400 mb-2" size={28} />
                                    <div className="text-2xl font-black text-white">#127</div>
                                    <div className="text-gray-500 text-sm">Your Rank</div>
                                </div>
                                <div className="bg-gradient-to-r from-purple-500/20 to-pink-500/20 rounded-xl p-4 text-center">
                                    <Target className="mx-auto text-purple-400 mb-2" size={28} />
                                    <div className="text-2xl font-black text-white">12</div>
                                    <div className="text-gray-500 text-sm">Challenges Won</div>
                                </div>
                                <div className="bg-gradient-to-r from-orange-500/20 to-red-500/20 rounded-xl p-4 text-center">
                                    <Wrench className="mx-auto text-orange-400 mb-2" size={28} />
                                    <div className="text-2xl font-black text-white">2</div>
                                    <div className="text-gray-500 text-sm">Tasks Due</div>
                                </div>
                            </div>

                            {/* Quick Links */}
                            <div className="mt-6 space-y-2">
                                {[
                                    { label: 'View Leaderboard', href: '/community' },
                                    { label: 'Check Impact', href: '/impact' },
                                    { label: 'Book Installer', href: '/book-installer' },
                                ].map((link, i) => (
                                    <a
                                        key={i}
                                        href={link.href}
                                        className="flex items-center justify-between p-3 bg-white/5 rounded-xl text-white hover:bg-white/10 transition-colors"
                                    >
                                        <span>{link.label}</span>
                                        <ChevronRight size={18} className="text-gray-500" />
                                    </a>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {/* Challenges Tab */}
                {activeTab === 'challenges' && <MonthlyChallenges />}

                {/* Maintenance Tab */}
                {activeTab === 'maintenance' && <MaintenanceReminders />}

                {/* Quality Tab */}
                {activeTab === 'quality' && <WaterQualityLog />}

                {/* History Tab */}
                {activeTab === 'history' && <HistoricalRainfall />}

                {/* Calculator Tab */}
                {activeTab === 'calculator' && (
                    <div className="max-w-2xl mx-auto">
                        <ROICalculator />
                    </div>
                )}

                {/* Scanner Tab */}
                {activeTab === 'scanner' && (
                    <div className="max-w-2xl mx-auto">
                        <WaterBillScanner />
                    </div>
                )}
            </div>
        </div>
    );
};

export default UserDashboard;
