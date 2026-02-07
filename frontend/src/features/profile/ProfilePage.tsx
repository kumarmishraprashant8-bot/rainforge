/**
 * User Profile Page
 * Shows user stats, saved assessments, badges, and settings
 */

import { useState } from 'react';
import {
    User, Settings, Award, FileText, Droplets, TrendingUp,
    LogOut, Edit2, Camera, Globe, Bell, Shield, ChevronRight,
    Calendar, MapPin, Phone, Mail, Star, CheckCircle
} from 'lucide-react';
import { useAuth } from '../../context/AuthContext';
import AadhaarKycModal from '../verification/AadhaarKycModal';

const ProfilePage = () => {
    const { user, logout, updateProfile, isAuthenticated } = useAuth();
    const [activeTab, setActiveTab] = useState('overview');
    const [editing, setEditing] = useState(false);
    const [editName, setEditName] = useState(user?.name || '');

    // KYC State
    const [showKyc, setShowKyc] = useState(false);
    const [isVerified, setIsVerified] = useState(false);
    const [kycDetails, setKycDetails] = useState<any>(null);

    // Demo data for assessments
    const savedAssessments = [
        { id: 'ASM-20260206-CF0089', location: 'New Delhi', date: '2026-02-06', yield: 71400, status: 'completed' },
        { id: 'ASM-20260115-AB1234', location: 'Mumbai', date: '2026-01-15', yield: 95000, status: 'in_progress' },
        { id: 'ASM-20251228-XY5678', location: 'Bangalore', date: '2025-12-28', yield: 62000, status: 'completed' },
    ];

    // Demo badges
    const badges = [
        { id: 'early_adopter', name: 'Early Adopter', icon: '🌟', desc: 'Joined during beta', earned: true },
        { id: 'water_warrior', name: 'Water Warrior', icon: '💧', desc: 'Saved 100,000L', earned: true },
        { id: 'eco_champion', name: 'Eco Champion', icon: '🌱', desc: '50kg CO₂ offset', earned: true },
        { id: 'community_hero', name: 'Community Hero', icon: '🏆', desc: 'Top 10 in region', earned: false },
        { id: 'installer_pro', name: 'Installer Pro', icon: '🔧', desc: 'Completed installation', earned: false },
        { id: 'referral_king', name: 'Referral King', icon: '👑', desc: 'Referred 5 friends', earned: false },
    ];

    if (!isAuthenticated || !user) {
        return (
            <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center">
                <div className="text-center glass rounded-2xl p-12 max-w-md">
                    <div className="text-6xl mb-6">🔐</div>
                    <h2 className="text-2xl font-bold text-white mb-2">Sign In Required</h2>
                    <p className="text-gray-400 mb-6">Please sign in to view your profile</p>
                    <a href="/" className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl inline-block">
                        Go Home
                    </a>
                </div>
            </div>
        );
    }

    const handleSaveName = () => {
        updateProfile({ name: editName });
        setEditing(false);
    };

    const handleKycSuccess = (details: any) => {
        setIsVerified(true);
        setKycDetails(details);
        // In a real app, you would save this to the backend
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-6xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Profile Header */}
                <div className="glass rounded-2xl p-6">
                    <div className="flex flex-col md:flex-row gap-6 items-start md:items-center">
                        {/* Avatar */}
                        <div className="relative">
                            <div className="w-24 h-24 rounded-2xl bg-gradient-to-br from-cyan-500 to-blue-500 flex items-center justify-center text-4xl text-white font-bold">
                                {user.name.charAt(0).toUpperCase()}
                            </div>
                            {isVerified && (
                                <div className="absolute -bottom-2 -left-2 p-1 bg-green-500 rounded-full border-4 border-slate-900">
                                    <CheckCircle size={16} className="text-white fill-green-500" />
                                </div>
                            )}
                            <button className="absolute -bottom-2 -right-2 p-2 bg-white/10 rounded-full hover:bg-white/20">
                                <Camera size={14} className="text-white" />
                            </button>
                        </div>

                        {/* Info */}
                        <div className="flex-1">
                            <div className="flex items-center gap-3">
                                {editing ? (
                                    <div className="flex gap-2">
                                        <input
                                            value={editName}
                                            onChange={(e) => setEditName(e.target.value)}
                                            className="px-3 py-1 bg-white/10 border border-white/20 rounded-lg text-white"
                                        />
                                        <button onClick={handleSaveName} className="px-3 py-1 bg-cyan-500 rounded-lg text-white text-sm">Save</button>
                                        <button onClick={() => setEditing(false)} className="px-3 py-1 bg-white/10 rounded-lg text-white text-sm">Cancel</button>
                                    </div>
                                ) : (
                                    <>
                                        <h1 className="text-2xl font-bold text-white flex items-center gap-2">
                                            {user.name}
                                            {isVerified && <span className="text-green-400" title="Aadhaar Verified"><Shield size={20} className="fill-green-400/20" /></span>}
                                        </h1>
                                        <button onClick={() => setEditing(true)} className="text-gray-400 hover:text-white">
                                            <Edit2 size={16} />
                                        </button>
                                    </>
                                )}
                            </div>
                            <div className="flex flex-wrap gap-4 mt-2 text-sm text-gray-400">
                                {user.email && <span className="flex items-center gap-1"><Mail size={14} /> {user.email}</span>}
                                {user.phone && <span className="flex items-center gap-1"><Phone size={14} /> {user.phone}</span>}
                                <span className="flex items-center gap-1"><Calendar size={14} /> Member since {user.joinedAt}</span>
                            </div>

                            {/* KYC Verification Status */}
                            <div className="mt-4">
                                {isVerified ? (
                                    <div className="inline-flex items-center gap-2 px-3 py-1 bg-green-500/10 border border-green-500/30 rounded-lg text-green-400 text-sm font-medium">
                                        <Shield size={14} /> Aadhaar Verified: XXXX XXXX {kycDetails?.aadhaarLast4 || '8921'}
                                    </div>
                                ) : (
                                    <button
                                        onClick={() => setShowKyc(true)}
                                        className="inline-flex items-center gap-2 px-3 py-1 bg-yellow-500/10 border border-yellow-500/30 rounded-lg text-yellow-500 text-sm font-medium hover:bg-yellow-500/20 transition-all cursor-pointer animate-pulse"
                                    >
                                        <Shield size={14} /> Verify Identity (e-KYC)
                                    </button>
                                )}
                            </div>
                        </div>

                        {/* Quick Stats */}
                        <div className="flex gap-4">
                            <div className="text-center px-4 py-2 bg-white/5 rounded-xl">
                                <div className="text-2xl font-bold text-cyan-400">{user.waterCredits}</div>
                                <div className="text-xs text-gray-400">Credits</div>
                            </div>
                            <div className="text-center px-4 py-2 bg-white/5 rounded-xl">
                                <div className="text-2xl font-bold text-green-400">{(user.totalWaterSaved / 1000).toFixed(0)}k</div>
                                <div className="text-xs text-gray-400">Liters Saved</div>
                            </div>
                            <div className="text-center px-4 py-2 bg-white/5 rounded-xl">
                                <div className="text-2xl font-bold text-purple-400">{badges.filter(b => b.earned).length}</div>
                                <div className="text-xs text-gray-400">Badges</div>
                            </div>
                        </div>
                    </div>
                </div>

                {/* Tabs */}
                <div className="flex gap-2 overflow-x-auto">
                    {[
                        { id: 'overview', label: 'Overview', icon: User },
                        { id: 'assessments', label: 'My Assessments', icon: FileText },
                        { id: 'badges', label: 'Badges', icon: Award },
                        { id: 'settings', label: 'Settings', icon: Settings },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id)}
                            className={`flex items-center gap-2 px-4 py-2 rounded-xl font-medium whitespace-nowrap transition-all ${activeTab === tab.id
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            <tab.icon size={18} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* Tab Content */}
                {activeTab === 'overview' && (
                    <div className="grid lg:grid-cols-2 gap-6">
                        {/* Impact Summary */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <TrendingUp className="text-green-400" />
                                Your Impact
                            </h3>
                            <div className="grid grid-cols-2 gap-4">
                                <div className="bg-white/5 rounded-xl p-4">
                                    <div className="text-3xl font-bold text-cyan-400">{(user.totalWaterSaved / 1000).toFixed(0)}k L</div>
                                    <div className="text-gray-400 text-sm">Water Harvested</div>
                                </div>
                                <div className="bg-white/5 rounded-xl p-4">
                                    <div className="text-3xl font-bold text-green-400">{Math.round(user.totalWaterSaved * 0.0005)} kg</div>
                                    <div className="text-gray-400 text-sm">CO₂ Offset</div>
                                </div>
                                <div className="bg-white/5 rounded-xl p-4">
                                    <div className="text-3xl font-bold text-purple-400">{user.assessments.length}</div>
                                    <div className="text-gray-400 text-sm">Projects</div>
                                </div>
                                <div className="bg-white/5 rounded-xl p-4">
                                    <div className="text-3xl font-bold text-yellow-400">₹{Math.round(user.totalWaterSaved * 0.015).toLocaleString()}</div>
                                    <div className="text-gray-400 text-sm">Money Saved</div>
                                </div>
                            </div>
                        </div>

                        {/* Recent Activity */}
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-4 flex items-center gap-2">
                                <Droplets className="text-cyan-400" />
                                Recent Activity
                            </h3>
                            <div className="space-y-3">
                                {savedAssessments.slice(0, 3).map(a => (
                                    <div key={a.id} className="flex items-center gap-3 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                                        <div className="p-2 bg-cyan-500/20 rounded-lg">
                                            <FileText className="text-cyan-400" size={18} />
                                        </div>
                                        <div className="flex-1">
                                            <div className="text-white font-medium">{a.id}</div>
                                            <div className="text-gray-500 text-sm flex items-center gap-2">
                                                <MapPin size={12} /> {a.location} • {a.date}
                                            </div>
                                        </div>
                                        <ChevronRight className="text-gray-400" size={18} />
                                    </div>
                                ))}
                            </div>
                        </div>
                    </div>
                )}

                {activeTab === 'assessments' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4">My Assessments</h3>
                        <div className="space-y-3">
                            {savedAssessments.map(a => (
                                <div key={a.id} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors cursor-pointer">
                                    <div className="p-3 bg-cyan-500/20 rounded-xl">
                                        <FileText className="text-cyan-400" size={24} />
                                    </div>
                                    <div className="flex-1">
                                        <div className="text-white font-semibold">{a.id}</div>
                                        <div className="text-gray-400 text-sm">{a.location} • {a.date}</div>
                                    </div>
                                    <div className="text-right">
                                        <div className="text-cyan-400 font-bold">{(a.yield / 1000).toFixed(1)}k L/yr</div>
                                        <div className={`text-xs px-2 py-1 rounded-full ${a.status === 'completed' ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                                            }`}>
                                            {a.status === 'completed' ? '✓ Completed' : '⏳ In Progress'}
                                        </div>
                                    </div>
                                    <ChevronRight className="text-gray-400" size={20} />
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'badges' && (
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-bold text-white mb-4">Achievement Badges</h3>
                        <div className="grid grid-cols-2 md:grid-cols-3 gap-4">
                            {badges.map(badge => (
                                <div
                                    key={badge.id}
                                    className={`p-4 rounded-xl text-center transition-all ${badge.earned
                                        ? 'bg-gradient-to-br from-cyan-500/20 to-blue-500/20 border border-cyan-500/30'
                                        : 'bg-white/5 opacity-50 grayscale'
                                        }`}
                                >
                                    <div className="text-4xl mb-2">{badge.icon}</div>
                                    <div className="text-white font-semibold">{badge.name}</div>
                                    <div className="text-gray-400 text-xs mt-1">{badge.desc}</div>
                                    {badge.earned && (
                                        <div className="mt-2 text-xs text-green-400 flex items-center justify-center gap-1">
                                            <Star size={12} /> Earned
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {activeTab === 'settings' && (
                    <div className="glass rounded-2xl p-6 space-y-4">
                        <h3 className="text-lg font-bold text-white mb-4">Settings</h3>

                        {/* Settings Options */}
                        {[
                            { icon: Globe, label: 'Language', value: 'English', action: 'Change' },
                            { icon: Bell, label: 'Notifications', value: 'Enabled', action: 'Manage' },
                            { icon: Shield, label: 'Privacy', value: '', action: 'View' },
                            { icon: Droplets, label: 'Default Roof Area', value: '120 m²', action: 'Edit' },
                        ].map((item, idx) => (
                            <div key={idx} className="flex items-center gap-4 p-4 bg-white/5 rounded-xl">
                                <item.icon className="text-gray-400" size={20} />
                                <div className="flex-1">
                                    <div className="text-white">{item.label}</div>
                                    {item.value && <div className="text-gray-500 text-sm">{item.value}</div>}
                                </div>
                                <button className="text-cyan-400 text-sm hover:underline">{item.action}</button>
                            </div>
                        ))}

                        {/* Logout */}
                        <button
                            onClick={logout}
                            className="w-full flex items-center justify-center gap-2 p-4 bg-red-500/10 border border-red-500/20 rounded-xl text-red-400 hover:bg-red-500/20 transition-colors"
                        >
                            <LogOut size={20} />
                            Sign Out
                        </button>
                    </div>
                )}
            </div>

            {/* Aadhaar e-KYC Modal */}
            <AadhaarKycModal
                isOpen={showKyc}
                onClose={() => setShowKyc(false)}
                onSuccess={handleKycSuccess}
            />
        </div>
    );
};

export default ProfilePage;
