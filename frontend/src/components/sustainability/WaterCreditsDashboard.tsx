/**
 * Water Credits Dashboard Component
 * Tradeable water savings portfolio and marketplace
 */

import React, { useState, useEffect } from 'react';
import { Droplets, TrendingUp, ShoppingCart, Leaf, ArrowRight, Award } from 'lucide-react';
import { sustainabilityAPI } from '../../services/unbeatableAPI';

interface WaterCredit {
    credit_id: string;
    water_saved_liters: number;
    credit_units: number;
    status: string;
    price_per_unit?: number;
    issued_at: string;
}

interface WaterCreditsDashboardProps {
    userId: string;
}

const WaterCreditsDashboard: React.FC<WaterCreditsDashboardProps> = ({ userId }) => {
    const [credits, setCredits] = useState<WaterCredit[]>([]);
    const [totalUnits, setTotalUnits] = useState(0);
    const [estimatedValue, setEstimatedValue] = useState(0);
    const [listings, setListings] = useState<any[]>([]);
    const [activeTab, setActiveTab] = useState<'portfolio' | 'marketplace'>('portfolio');
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        loadData();
    }, [userId]);

    const loadData = async () => {
        setLoading(true);
        try {
            const [portfolioRes, marketRes] = await Promise.all([
                sustainabilityAPI.getPortfolio(userId),
                sustainabilityAPI.getMarketplace()
            ]);

            setCredits(portfolioRes.data.credits || []);
            setTotalUnits(portfolioRes.data.total_units || 0);
            setEstimatedValue(portfolioRes.data.estimated_value || 0);
            setListings(marketRes.data.listings || []);
        } catch (error) {
            console.error('Error loading water credits:', error);
        } finally {
            setLoading(false);
        }
    };

    const handleListForSale = async (creditId: string, price: number) => {
        try {
            await sustainabilityAPI.listCreditsForSale(creditId, userId, price);
            loadData();
        } catch (error) {
            console.error('Error listing credit:', error);
        }
    };

    const handleBuy = async (orderId: string) => {
        try {
            await sustainabilityAPI.buyCredits(orderId, userId);
            loadData();
        } catch (error) {
            console.error('Error buying credit:', error);
        }
    };

    const handleRetire = async (creditId: string) => {
        try {
            await sustainabilityAPI.retireCredits(creditId, userId, 'Water-positive certification');
            loadData();
        } catch (error) {
            console.error('Error retiring credit:', error);
        }
    };

    const formatNumber = (num: number) => new Intl.NumberFormat('en-IN').format(num);

    return (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-cyan-500 to-blue-600 p-6">
                <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                        <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                            <Droplets className="w-6 h-6 text-white" />
                        </div>
                        <div>
                            <h2 className="text-xl font-bold text-white">Water Credits</h2>
                            <p className="text-white/70 text-sm">Tradeable water savings certificates</p>
                        </div>
                    </div>
                    <div className="text-right">
                        <p className="text-white/70 text-sm">Your Portfolio Value</p>
                        <p className="text-2xl font-bold text-white">₹{formatNumber(estimatedValue)}</p>
                    </div>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-4">
                    <div className="bg-white/10 rounded-xl p-4">
                        <Droplets className="w-5 h-5 text-white/70 mb-2" />
                        <p className="text-2xl font-bold text-white">{formatNumber(totalUnits)}</p>
                        <p className="text-white/70 text-sm">Credit Units</p>
                    </div>
                    <div className="bg-white/10 rounded-xl p-4">
                        <Award className="w-5 h-5 text-white/70 mb-2" />
                        <p className="text-2xl font-bold text-white">{credits.filter(c => c.status === 'retired').length}</p>
                        <p className="text-white/70 text-sm">Retired Credits</p>
                    </div>
                    <div className="bg-white/10 rounded-xl p-4">
                        <TrendingUp className="w-5 h-5 text-white/70 mb-2" />
                        <p className="text-2xl font-bold text-white">₹25</p>
                        <p className="text-white/70 text-sm">Per kL Rate</p>
                    </div>
                </div>
            </div>

            {/* Tabs */}
            <div className="flex border-b">
                <button
                    onClick={() => setActiveTab('portfolio')}
                    className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'portfolio'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    My Portfolio
                </button>
                <button
                    onClick={() => setActiveTab('marketplace')}
                    className={`flex-1 px-6 py-4 text-sm font-medium transition-colors ${activeTab === 'marketplace'
                            ? 'text-blue-600 border-b-2 border-blue-600'
                            : 'text-gray-500 hover:text-gray-700'
                        }`}
                >
                    <div className="flex items-center justify-center gap-2">
                        <ShoppingCart className="w-4 h-4" />
                        Marketplace
                    </div>
                </button>
            </div>

            {/* Content */}
            <div className="p-6">
                {loading ? (
                    <div className="text-center py-12">
                        <div className="animate-spin w-8 h-8 border-4 border-blue-600 border-t-transparent rounded-full mx-auto" />
                    </div>
                ) : activeTab === 'portfolio' ? (
                    <div className="space-y-4">
                        {credits.length === 0 ? (
                            <div className="text-center py-12">
                                <Droplets className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                <p className="text-gray-500">No water credits yet</p>
                                <p className="text-sm text-gray-400">Complete RWH projects to earn credits</p>
                            </div>
                        ) : (
                            credits.map((credit) => (
                                <div key={credit.credit_id} className="border rounded-xl p-4 hover:shadow-md transition-shadow">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="font-semibold text-gray-800">
                                                {formatNumber(credit.water_saved_liters)} L saved
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {credit.credit_units} units • {credit.credit_id}
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-2">
                                            {credit.status === 'active' && (
                                                <>
                                                    <button
                                                        onClick={() => handleListForSale(credit.credit_id, 25)}
                                                        className="px-4 py-2 bg-blue-100 text-blue-700 rounded-lg text-sm font-medium hover:bg-blue-200 transition-colors"
                                                    >
                                                        Sell
                                                    </button>
                                                    <button
                                                        onClick={() => handleRetire(credit.credit_id)}
                                                        className="px-4 py-2 bg-green-100 text-green-700 rounded-lg text-sm font-medium hover:bg-green-200 transition-colors"
                                                    >
                                                        <div className="flex items-center gap-1">
                                                            <Leaf className="w-4 h-4" />
                                                            Retire
                                                        </div>
                                                    </button>
                                                </>
                                            )}
                                            {credit.status === 'listed' && (
                                                <span className="px-3 py-1 bg-yellow-100 text-yellow-700 rounded-full text-sm">
                                                    Listed @ ₹{credit.price_per_unit}/unit
                                                </span>
                                            )}
                                            {credit.status === 'retired' && (
                                                <span className="px-3 py-1 bg-green-100 text-green-700 rounded-full text-sm flex items-center gap-1">
                                                    <Award className="w-4 h-4" /> Retired
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                ) : (
                    <div className="space-y-4">
                        {listings.length === 0 ? (
                            <div className="text-center py-12">
                                <ShoppingCart className="w-12 h-12 text-gray-300 mx-auto mb-4" />
                                <p className="text-gray-500">No listings available</p>
                            </div>
                        ) : (
                            listings.map((listing) => (
                                <div key={listing.order_id} className="border rounded-xl p-4 hover:shadow-md transition-shadow">
                                    <div className="flex items-center justify-between">
                                        <div>
                                            <p className="font-semibold text-gray-800">
                                                {formatNumber(listing.units)} units
                                            </p>
                                            <p className="text-sm text-gray-500">
                                                {formatNumber(listing.water_saved_liters)} L equivalent
                                            </p>
                                        </div>
                                        <div className="flex items-center gap-4">
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-gray-800">₹{listing.price_per_unit}/unit</p>
                                                <p className="text-sm text-gray-500">Total: ₹{formatNumber(listing.total_price)}</p>
                                            </div>
                                            <button
                                                onClick={() => handleBuy(listing.order_id)}
                                                className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-600 text-white rounded-xl font-medium hover:opacity-90 transition-opacity flex items-center gap-2"
                                            >
                                                Buy <ArrowRight className="w-4 h-4" />
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default WaterCreditsDashboard;
