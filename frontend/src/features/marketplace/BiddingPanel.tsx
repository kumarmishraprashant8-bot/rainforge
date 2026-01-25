import { useState } from 'react';
import {
    Gavel, DollarSign, Clock, Shield, Award, TrendingUp,
    Send, Users, CheckCircle, XCircle
} from 'lucide-react';

interface Bid {
    bid_id: string;
    installer_id: number;
    installer_name: string;
    installer_rpi: number;
    price: number;
    timeline_days: number;
    warranty_months: number;
    score: number;
    rank: number;
}

interface BiddingPanelProps {
    jobId: number;
    estimatedCost: number;
    onBidAwarded?: (bid: Bid) => void;
}

const BiddingPanel = ({ jobId = 116, estimatedCost = 115000, onBidAwarded }: BiddingPanelProps) => {
    const [bids, setBids] = useState<Bid[]>([]);
    const [bidOpen, setBidOpen] = useState(false);
    const [loading, setLoading] = useState(false);
    const [newBid, setNewBid] = useState({
        installer_id: 1,
        installer_name: 'Jal Mitra Solutions',
        installer_rpi: 92,
        price: estimatedCost * 0.95,
        timeline_days: 25,
        warranty_months: 12
    });
    const [awardedBid, setAwardedBid] = useState<Bid | null>(null);

    const openBidding = async () => {
        setLoading(true);
        try {
            await fetch(`https://rainforge-api.onrender.com/api/v1/marketplace/jobs/${jobId}/open-bid`, {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ deadline_hours: 72 })
            });
            setBidOpen(true);
        } catch (e) {
            setBidOpen(true);
        }
        setLoading(false);
    };

    const submitBid = async () => {
        setLoading(true);
        try {
            const res = await fetch('https://rainforge-api.onrender.com/api/v1/marketplace/bids', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId, ...newBid })
            });
            await fetchBids();
        } catch (e) {
            // Mock add
            const mockBid: Bid = {
                bid_id: `BID-${Math.random().toString(36).substr(2, 8)}`,
                ...newBid,
                score: 75 + Math.random() * 20,
                rank: bids.length + 1
            };
            setBids([...bids, mockBid].sort((a, b) => b.score - a.score).map((b, i) => ({ ...b, rank: i + 1 })));
        }
        setLoading(false);
    };

    const fetchBids = async () => {
        try {
            const res = await fetch(`https://rainforge-api.onrender.com/api/v1/marketplace/bids?job_id=${jobId}`);
            const data = await res.json();
            setBids(data.bids || []);
        } catch (e) {
            // Keep existing
        }
    };

    const awardBid = async (bidId: string) => {
        setLoading(true);
        try {
            await fetch(`https://rainforge-api.onrender.com/api/v1/marketplace/bids/${bidId}/award`, { method: 'POST' });
        } catch (e) { }

        const awarded = bids.find(b => b.bid_id === bidId);
        if (awarded) {
            setAwardedBid(awarded);
            onBidAwarded?.(awarded);
        }
        setLoading(false);
    };

    const addDemoBids = () => {
        const demoBids: Bid[] = [
            { bid_id: 'BID-001', installer_id: 1, installer_name: 'Jal Mitra Solutions', installer_rpi: 92, price: 109000, timeline_days: 22, warranty_months: 18, score: 88.5, rank: 1 },
            { bid_id: 'BID-002', installer_id: 3, installer_name: 'BlueDrop Tech', installer_rpi: 95, price: 118000, timeline_days: 20, warranty_months: 24, score: 85.2, rank: 2 },
            { bid_id: 'BID-003', installer_id: 2, installer_name: 'AquaSave India', installer_rpi: 85, price: 105000, timeline_days: 28, warranty_months: 12, score: 78.8, rank: 3 },
            { bid_id: 'BID-004', installer_id: 7, installer_name: 'Monsoon Masters', installer_rpi: 82, price: 112000, timeline_days: 25, warranty_months: 15, score: 74.5, rank: 4 },
        ];
        setBids(demoBids);
        setBidOpen(true);
    };

    return (
        <div className="glass rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Gavel className="text-purple-400" />
                    Competitive Bidding
                </h2>
                <div className={`px-3 py-1 rounded-full text-sm font-semibold ${awardedBid ? 'bg-green-500/20 text-green-400' :
                    bidOpen ? 'bg-yellow-500/20 text-yellow-400' : 'bg-gray-500/20 text-gray-400'
                    }`}>
                    {awardedBid ? '✓ Awarded' : bidOpen ? '● Open' : '○ Closed'}
                </div>
            </div>

            {/* Job Info */}
            <div className="bg-white/5 rounded-xl p-4">
                <div className="text-sm text-gray-400 mb-1">Job #{jobId}</div>
                <div className="text-lg font-semibold text-white">New School Building, Najafgarh</div>
                <div className="text-cyan-400 font-bold mt-1">Estimated: ₹{estimatedCost.toLocaleString()}</div>
            </div>

            {/* Controls */}
            {!bidOpen && !awardedBid && (
                <div className="flex gap-3">
                    <button
                        onClick={openBidding}
                        disabled={loading}
                        className="flex-1 py-3 bg-gradient-to-r from-purple-500 to-pink-500 text-white font-bold rounded-xl"
                    >
                        Open for Bidding
                    </button>
                    <button
                        onClick={addDemoBids}
                        className="px-6 py-3 bg-white/10 text-white rounded-xl hover:bg-white/20"
                    >
                        Demo Bids
                    </button>
                </div>
            )}

            {/* Submit Bid Form (for installers) */}
            {bidOpen && !awardedBid && (
                <div className="bg-white/5 rounded-xl p-4 space-y-4">
                    <h3 className="font-semibold text-white">Submit Your Bid</h3>
                    <div className="grid grid-cols-3 gap-4">
                        <div>
                            <label className="text-xs text-gray-400">Price (₹)</label>
                            <input
                                type="number"
                                value={newBid.price}
                                onChange={(e) => setNewBid({ ...newBid, price: parseFloat(e.target.value) })}
                                className="w-full mt-1 p-2 bg-white/10 border border-white/10 rounded-lg text-white"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-gray-400">Timeline (days)</label>
                            <input
                                type="number"
                                value={newBid.timeline_days}
                                onChange={(e) => setNewBid({ ...newBid, timeline_days: parseInt(e.target.value) })}
                                className="w-full mt-1 p-2 bg-white/10 border border-white/10 rounded-lg text-white"
                            />
                        </div>
                        <div>
                            <label className="text-xs text-gray-400">Warranty (months)</label>
                            <input
                                type="number"
                                value={newBid.warranty_months}
                                onChange={(e) => setNewBid({ ...newBid, warranty_months: parseInt(e.target.value) })}
                                className="w-full mt-1 p-2 bg-white/10 border border-white/10 rounded-lg text-white"
                            />
                        </div>
                    </div>
                    <button
                        onClick={submitBid}
                        disabled={loading}
                        className="w-full py-3 bg-cyan-500 text-white font-bold rounded-xl flex items-center justify-center gap-2"
                    >
                        <Send size={18} />
                        Submit Bid
                    </button>
                </div>
            )}

            {/* Bid Rankings */}
            {bids.length > 0 && (
                <div className="space-y-3">
                    <h3 className="font-semibold text-white flex items-center gap-2">
                        <TrendingUp size={18} className="text-cyan-400" />
                        Bid Rankings
                    </h3>

                    {bids.map((bid) => (
                        <div
                            key={bid.bid_id}
                            className={`p-4 rounded-xl border-2 transition-all ${awardedBid?.bid_id === bid.bid_id
                                ? 'border-green-500 bg-green-500/10'
                                : bid.rank === 1
                                    ? 'border-yellow-500/50 bg-yellow-500/5'
                                    : 'border-white/10 bg-white/5'
                                }`}
                        >
                            <div className="flex items-center justify-between mb-3">
                                <div className="flex items-center gap-3">
                                    <div className={`w-8 h-8 rounded-full flex items-center justify-center font-bold ${bid.rank === 1 ? 'bg-yellow-500 text-black' :
                                        bid.rank === 2 ? 'bg-gray-300 text-black' :
                                            bid.rank === 3 ? 'bg-amber-600 text-white' :
                                                'bg-white/20 text-white'
                                        }`}>
                                        {bid.rank}
                                    </div>
                                    <div>
                                        <div className="font-semibold text-white">{bid.installer_name}</div>
                                        <div className="text-xs text-gray-400">RPI: {bid.installer_rpi}</div>
                                    </div>
                                </div>
                                <div className="text-2xl font-black text-cyan-400">{bid.score.toFixed(1)}</div>
                            </div>

                            <div className="grid grid-cols-3 gap-4 mb-3">
                                <div className="flex items-center gap-2">
                                    <DollarSign size={16} className="text-green-400" />
                                    <div>
                                        <div className="text-white font-semibold">₹{bid.price.toLocaleString()}</div>
                                        <div className="text-xs text-gray-400">
                                            {((bid.price / estimatedCost - 1) * 100).toFixed(0)}% {bid.price < estimatedCost ? 'below' : 'above'}
                                        </div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Clock size={16} className="text-blue-400" />
                                    <div>
                                        <div className="text-white font-semibold">{bid.timeline_days} days</div>
                                        <div className="text-xs text-gray-400">Timeline</div>
                                    </div>
                                </div>
                                <div className="flex items-center gap-2">
                                    <Shield size={16} className="text-purple-400" />
                                    <div>
                                        <div className="text-white font-semibold">{bid.warranty_months} mo</div>
                                        <div className="text-xs text-gray-400">Warranty</div>
                                    </div>
                                </div>
                            </div>

                            {!awardedBid && (
                                <button
                                    onClick={() => awardBid(bid.bid_id)}
                                    disabled={loading}
                                    className="w-full py-2 bg-green-500 hover:bg-green-600 text-white font-semibold rounded-lg flex items-center justify-center gap-2"
                                >
                                    <Award size={16} />
                                    Award Bid
                                </button>
                            )}

                            {awardedBid?.bid_id === bid.bid_id && (
                                <div className="flex items-center justify-center gap-2 text-green-400 py-2">
                                    <CheckCircle size={20} />
                                    <span className="font-semibold">Bid Awarded</span>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}
        </div>
    );
};

export default BiddingPanel;
