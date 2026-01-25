import { useState, useEffect } from 'react';
import {
    Wallet, CheckCircle, Circle, Lock, Unlock, Clock,
    ArrowRight, DollarSign, AlertTriangle
} from 'lucide-react';

interface Milestone {
    id: string;
    name: string;
    amount: number;
    sequence: number;
    status: 'pending' | 'in_progress' | 'completed' | 'verified' | 'released';
    completed_at?: string;
    released_at?: string;
}

interface Payment {
    payment_id: string;
    job_id: number;
    total_amount: number;
    escrow_amount: number;
    released_amount: number;
    status: string;
    milestones: Milestone[];
}

interface PaymentMilestonesProps {
    jobId?: number;
    totalAmount?: number;
}

const PaymentMilestones = ({ jobId = 116, totalAmount = 115000 }: PaymentMilestonesProps) => {
    const [payment, setPayment] = useState<Payment | null>(null);
    const [loading, setLoading] = useState(false);

    const createPayment = async () => {
        setLoading(true);
        try {
            const res = await fetch('https://rainforge-api.onrender.com/api/v1/payments', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ job_id: jobId, total_amount: totalAmount })
            });
            const data = await res.json();

            // Capture to escrow
            await fetch(`https://rainforge-api.onrender.com/api/v1/payments/${data.payment_id}/escrow`, { method: 'POST' });

            fetchPayment(data.payment_id);
        } catch (e) {
            // Mock payment
            setPayment({
                payment_id: 'PAY-DEMO01',
                job_id: jobId,
                total_amount: totalAmount,
                escrow_amount: totalAmount,
                released_amount: 0,
                status: 'escrow',
                milestones: [
                    { id: 'MS-001', name: 'Design Approval', amount: 23000, sequence: 1, status: 'pending' },
                    { id: 'MS-002', name: 'Installation Complete', amount: 46000, sequence: 2, status: 'pending' },
                    { id: 'MS-003', name: 'Verification Passed', amount: 34500, sequence: 3, status: 'pending' },
                    { id: 'MS-004', name: 'Post-Performance Check', amount: 11500, sequence: 4, status: 'pending' }
                ]
            });
        }
        setLoading(false);
    };

    const fetchPayment = async (paymentId: string) => {
        try {
            const res = await fetch(`https://rainforge-api.onrender.com/api/v1/payments/${paymentId}`);
            setPayment(await res.json());
        } catch (e) { }
    };

    const completeMilestone = async (milestoneId: string) => {
        if (!payment) return;
        setLoading(true);

        try {
            await fetch(`https://rainforge-api.onrender.com/api/v1/payments/${payment.payment_id}/milestones/${milestoneId}/complete`, { method: 'POST' });
            await fetchPayment(payment.payment_id);
        } catch (e) {
            // Mock update
            setPayment({
                ...payment,
                milestones: payment.milestones.map(m =>
                    m.id === milestoneId ? { ...m, status: 'completed' } : m
                )
            });
        }
        setLoading(false);
    };

    const verifyMilestone = async (milestoneId: string) => {
        if (!payment) return;
        setLoading(true);

        try {
            await fetch(`https://rainforge-api.onrender.com/api/v1/payments/${payment.payment_id}/milestones/${milestoneId}/verify`, { method: 'POST' });
            await fetchPayment(payment.payment_id);
        } catch (e) {
            setPayment({
                ...payment,
                milestones: payment.milestones.map(m =>
                    m.id === milestoneId ? { ...m, status: 'verified' } : m
                )
            });
        }
        setLoading(false);
    };

    const releaseMilestone = async (milestoneId: string) => {
        if (!payment) return;
        setLoading(true);

        try {
            await fetch(`https://rainforge-api.onrender.com/api/v1/payments/${payment.payment_id}/milestones/${milestoneId}/release`, { method: 'POST' });
            await fetchPayment(payment.payment_id);
        } catch (e) {
            const milestone = payment.milestones.find(m => m.id === milestoneId);
            if (milestone) {
                setPayment({
                    ...payment,
                    released_amount: payment.released_amount + milestone.amount,
                    escrow_amount: payment.escrow_amount - milestone.amount,
                    milestones: payment.milestones.map(m =>
                        m.id === milestoneId ? { ...m, status: 'released' } : m
                    )
                });
            }
        }
        setLoading(false);
    };

    const getStatusConfig = (status: string) => {
        switch (status) {
            case 'released': return { icon: CheckCircle, color: 'text-green-400', bg: 'bg-green-500/20', label: 'Released' };
            case 'verified': return { icon: Unlock, color: 'text-blue-400', bg: 'bg-blue-500/20', label: 'Verified' };
            case 'completed': return { icon: Clock, color: 'text-yellow-400', bg: 'bg-yellow-500/20', label: 'Awaiting Verify' };
            case 'in_progress': return { icon: Circle, color: 'text-cyan-400', bg: 'bg-cyan-500/20', label: 'In Progress' };
            default: return { icon: Lock, color: 'text-gray-400', bg: 'bg-white/10', label: 'Pending' };
        }
    };

    return (
        <div className="glass rounded-2xl p-6 space-y-6">
            <div className="flex items-center justify-between">
                <h2 className="text-2xl font-bold text-white flex items-center gap-2">
                    <Wallet className="text-green-400" />
                    Escrow & Milestones
                </h2>
                {payment && (
                    <div className="text-sm">
                        <span className="text-gray-400">Status: </span>
                        <span className={`font-semibold ${payment.status === 'released' ? 'text-green-400' :
                            payment.status === 'escrow' ? 'text-yellow-400' : 'text-gray-400'
                            }`}>
                            {payment.status.toUpperCase()}
                        </span>
                    </div>
                )}
            </div>

            {!payment ? (
                <div className="text-center py-8">
                    <DollarSign className="mx-auto text-gray-500 mb-4" size={48} />
                    <p className="text-gray-400 mb-4">No payment created for this job yet</p>
                    <button
                        onClick={createPayment}
                        disabled={loading}
                        className="px-6 py-3 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold rounded-xl"
                    >
                        Create Escrow Payment
                    </button>
                </div>
            ) : (
                <>
                    {/* Summary Cards */}
                    <div className="grid grid-cols-3 gap-4">
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-sm text-gray-400 mb-1">Total Amount</div>
                            <div className="text-2xl font-bold text-white">₹{payment.total_amount.toLocaleString()}</div>
                        </div>
                        <div className="bg-yellow-500/10 rounded-xl p-4 text-center">
                            <div className="text-sm text-gray-400 mb-1">In Escrow</div>
                            <div className="text-2xl font-bold text-yellow-400">₹{payment.escrow_amount.toLocaleString()}</div>
                        </div>
                        <div className="bg-green-500/10 rounded-xl p-4 text-center">
                            <div className="text-sm text-gray-400 mb-1">Released</div>
                            <div className="text-2xl font-bold text-green-400">₹{payment.released_amount.toLocaleString()}</div>
                        </div>
                    </div>

                    {/* Progress Bar */}
                    <div className="h-3 bg-white/10 rounded-full overflow-hidden">
                        <div
                            className="h-full bg-gradient-to-r from-green-500 to-emerald-500 transition-all"
                            style={{ width: `${(payment.released_amount / payment.total_amount) * 100}%` }}
                        />
                    </div>

                    {/* Milestones */}
                    <div className="space-y-3">
                        {payment.milestones.map((milestone, idx) => {
                            const config = getStatusConfig(milestone.status);
                            const Icon = config.icon;
                            const prevCompleted = idx === 0 || ['completed', 'verified', 'released'].includes(payment.milestones[idx - 1].status);

                            return (
                                <div key={milestone.id} className={`p-4 rounded-xl ${config.bg}`}>
                                    <div className="flex items-center justify-between mb-2">
                                        <div className="flex items-center gap-3">
                                            <div className={`p-2 rounded-lg ${config.bg}`}>
                                                <Icon className={config.color} size={20} />
                                            </div>
                                            <div>
                                                <div className="font-semibold text-white">{milestone.name}</div>
                                                <div className={`text-xs ${config.color}`}>{config.label}</div>
                                            </div>
                                        </div>
                                        <div className="text-lg font-bold text-white">₹{milestone.amount.toLocaleString()}</div>
                                    </div>

                                    {/* Action Buttons */}
                                    <div className="flex gap-2 mt-3">
                                        {milestone.status === 'pending' && prevCompleted && (
                                            <button
                                                onClick={() => completeMilestone(milestone.id)}
                                                disabled={loading}
                                                className="flex-1 py-2 bg-cyan-500 text-white text-sm font-semibold rounded-lg"
                                            >
                                                Mark Complete
                                            </button>
                                        )}
                                        {milestone.status === 'completed' && (
                                            <button
                                                onClick={() => verifyMilestone(milestone.id)}
                                                disabled={loading}
                                                className="flex-1 py-2 bg-blue-500 text-white text-sm font-semibold rounded-lg"
                                            >
                                                Verify (Admin)
                                            </button>
                                        )}
                                        {milestone.status === 'verified' && (
                                            <button
                                                onClick={() => releaseMilestone(milestone.id)}
                                                disabled={loading}
                                                className="flex-1 py-2 bg-green-500 text-white text-sm font-semibold rounded-lg"
                                            >
                                                Release Funds
                                            </button>
                                        )}
                                        {milestone.status === 'released' && (
                                            <div className="flex-1 py-2 text-center text-green-400 text-sm font-semibold">
                                                ✓ Funds Released
                                            </div>
                                        )}
                                    </div>
                                </div>
                            );
                        })}
                    </div>
                </>
            )}
        </div>
    );
};

export default PaymentMilestones;
