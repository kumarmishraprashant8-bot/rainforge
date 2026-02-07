import { useState } from 'react';
import { Store, Zap, Gavel, Wallet, Shield, Settings } from 'lucide-react';
import AllocationPanel from './AllocationPanel';
import BiddingPanel from './BiddingPanel';
import PaymentMilestones from '../payments/PaymentMilestones';

type Tab = 'allocation' | 'bidding' | 'payments';

const MarketplacePage = () => {
    const [activeTab, setActiveTab] = useState<Tab>('allocation');

    const tabs = [
        { id: 'allocation' as Tab, label: 'Smart Allocation', icon: Zap, emoji: '⚡' },
        { id: 'bidding' as Tab, label: 'Competitive Bidding', icon: Gavel, emoji: '🔨' },
        { id: 'payments' as Tab, label: 'Escrow & Payments', icon: Wallet, emoji: '💳' },
    ];

    return (
        <div className="min-h-screen py-12">
            <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 space-y-8">
                {/* Header */}
                <div className="text-center animate-fade-in-up">
                    <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-accent-secondary)]/10 border border-[var(--color-accent-secondary)]/20 mb-6">
                        <Store className="text-[var(--color-accent-secondary)]" size={16} />
                        <span className="text-[var(--color-accent-secondary)] text-sm font-medium">Government Procurement</span>
                    </div>
                    <h1 className="text-3xl sm:text-4xl font-bold text-[var(--color-text-primary)] mb-2">
                        RainForge Marketplace
                    </h1>
                    <p className="text-[var(--color-text-muted)]">Allocation • Bidding • Escrow • Verification</p>
                </div>

                {/* Tab Navigation */}
                <div className="flex justify-center animate-fade-in-up stagger-1">
                    <div className="inline-flex bg-[var(--color-bg-elevated)] rounded-xl p-1.5 border border-[var(--color-border)]">
                        {tabs.map((tab) => (
                            <button
                                key={tab.id}
                                onClick={() => setActiveTab(tab.id)}
                                className={`flex items-center gap-2 px-5 py-3 rounded-lg font-medium transition-all ${activeTab === tab.id
                                        ? 'bg-[var(--color-accent-primary)] text-white shadow-lg'
                                        : 'text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] hover:bg-[var(--color-border)]'
                                    }`}
                            >
                                <span className="text-lg">{tab.emoji}</span>
                                <span className="hidden sm:inline">{tab.label}</span>
                            </button>
                        ))}
                    </div>
                </div>

                {/* Tab Content */}
                <div className="max-w-5xl mx-auto animate-fade-in-up stagger-2">
                    {activeTab === 'allocation' && <AllocationPanel />}
                    {activeTab === 'bidding' && <BiddingPanel jobId={116} estimatedCost={115000} />}
                    {activeTab === 'payments' && <PaymentMilestones jobId={116} totalAmount={115000} />}
                </div>

                {/* Quick Actions */}
                <div className="max-w-5xl mx-auto animate-fade-in-up stagger-3">
                    <div className="card-premium rounded-2xl p-6">
                        <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-4 flex items-center gap-2">
                            <Settings className="text-[var(--color-text-muted)]" size={20} />
                            Admin Quick Actions
                        </h3>
                        <div className="grid sm:grid-cols-2 md:grid-cols-4 gap-4">
                            <button className="stat-card hover:border-[var(--color-accent-info)]/30 text-left transition-colors">
                                <div className="stat-icon stat-icon-sky mb-3">
                                    <Shield size={18} />
                                </div>
                                <div className="font-medium text-[var(--color-text-primary)]">Review Verifications</div>
                                <div className="text-xs text-[var(--color-text-muted)] mt-1">3 pending</div>
                            </button>
                            <button className="stat-card hover:border-[var(--color-accent-secondary)]/30 text-left transition-colors">
                                <div className="stat-icon stat-icon-indigo mb-3">
                                    <Gavel size={18} />
                                </div>
                                <div className="font-medium text-[var(--color-text-primary)]">Open Bids</div>
                                <div className="text-xs text-[var(--color-text-muted)] mt-1">5 active</div>
                            </button>
                            <button className="stat-card hover:border-[var(--color-accent-success)]/30 text-left transition-colors">
                                <div className="stat-icon stat-icon-emerald mb-3">
                                    <Wallet size={18} />
                                </div>
                                <div className="font-medium text-[var(--color-text-primary)]">Pending Releases</div>
                                <div className="text-xs text-[var(--color-text-muted)] mt-1">₹4.2L in escrow</div>
                            </button>
                            <button className="stat-card hover:border-[var(--color-accent-warning)]/30 text-left transition-colors">
                                <div className="stat-icon stat-icon-amber mb-3">
                                    <Zap size={18} />
                                </div>
                                <div className="font-medium text-[var(--color-text-primary)]">Run Batch Allocation</div>
                                <div className="text-xs text-[var(--color-text-muted)] mt-1">12 unassigned jobs</div>
                            </button>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default MarketplacePage;
