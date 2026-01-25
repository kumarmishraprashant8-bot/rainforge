import { useState } from 'react';
import { Store, Zap, Gavel, Wallet, Shield, Settings } from 'lucide-react';
import AllocationPanel from './AllocationPanel';
import BiddingPanel from './BiddingPanel';
import PaymentMilestones from '../payments/PaymentMilestones';

type Tab = 'allocation' | 'bidding' | 'payments';

const MarketplacePage = () => {
    const [activeTab, setActiveTab] = useState<Tab>('allocation');

    const tabs = [
        { id: 'allocation' as Tab, label: 'Smart Allocation', icon: Zap, color: 'yellow' },
        { id: 'bidding' as Tab, label: 'Competitive Bidding', icon: Gavel, color: 'purple' },
        { id: 'payments' as Tab, label: 'Escrow & Payments', icon: Wallet, color: 'green' },
    ];

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                {/* Header */}
                <div className="text-center">
                    <div className="inline-flex items-center gap-2 px-4 py-2 bg-purple-500/10 border border-purple-500/20 rounded-full mb-4">
                        <Store className="text-purple-400" size={16} />
                        <span className="text-purple-300 text-sm font-medium">Government Procurement</span>
                    </div>
                    <h1 className="text-4xl font-black text-white mb-2">
                        RainForge Marketplace
                    </h1>
                    <p className="text-gray-400">Allocation • Bidding • Escrow • Verification</p>
                </div>

                {/* Tab Navigation */}
                <div className="flex justify-center">
                    <div className="inline-flex bg-white/5 rounded-xl p-1">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-6 py-3 rounded-lg font-semibold transition-all ${activeTab === tab.id
                                        ? `bg-${tab.color}-500 text-white`
                                        : 'text-gray-400 hover:text-white'
                                    }`}
                                style={activeTab === tab.id ? {
                                    backgroundColor: tab.color === 'yellow' ? '#eab308' :
                                        tab.color === 'purple' ? '#a855f7' :
                                            '#22c55e'
                                } : {}}
                            >
                                <tab.icon size={18} />
                                {tab.label}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Tab Content */}
                <div className="max-w-5xl mx-auto">
                    {activeTab === 'allocation' && <AllocationPanel />}
                    {activeTab === 'bidding' && <BiddingPanel jobId={116} estimatedCost={115000} />}
                    {activeTab === 'payments' && <PaymentMilestones jobId={116} totalAmount={115000} />}
                </div>

                {/* Quick Actions */}
                <div className="max-w-5xl mx-auto">
                    <div className="glass rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-white mb-4 flex items-center gap-2">
                            <Settings className="text-gray-400" size={20} />
                            Admin Quick Actions
                        </h3>
                        <div className="grid md:grid-cols-4 gap-4">
                            <button className="p-4 bg-white/5 hover:bg-white/10 rounded-xl text-left transition-colors">
                                <Shield className="text-blue-400 mb-2" size={24} />
                                <div className="font-semibold text-white">Review Verifications</div>
                                <div className="text-xs text-gray-400">3 pending</div>
                            </button>
                            <button className="p-4 bg-white/5 hover:bg-white/10 rounded-xl text-left transition-colors">
                                <Gavel className="text-purple-400 mb-2" size={24} />
                                <div className="font-semibold text-white">Open Bids</div>
                                <div className="text-xs text-gray-400">5 active</div>
                            </button>
                            <button className="p-4 bg-white/5 hover:bg-white/10 rounded-xl text-left transition-colors">
                                <Wallet className="text-green-400 mb-2" size={24} />
                                <div className="font-semibold text-white">Pending Releases</div>
                                <div className="text-xs text-gray-400">₹4.2L in escrow</div>
                            </button>
                            <button className="p-4 bg-white/5 hover:bg-white/10 rounded-xl text-left transition-colors">
                                <Zap className="text-yellow-400 mb-2" size={24} />
                                <div className="font-semibold text-white">Run Batch Allocation</div>
                                <div className="text-xs text-gray-400">12 unassigned jobs</div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketplacePage;
