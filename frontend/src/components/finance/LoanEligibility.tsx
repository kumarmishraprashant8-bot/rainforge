/**
 * Loan Eligibility Checker Component
 * NBFC partner integration for RWH microloans
 */

import React, { useState } from 'react';
import { CreditCard, TrendingUp, Check, AlertCircle, Loader2 } from 'lucide-react';
import { financeAPI } from '../../services/unbeatableAPI';

interface LoanOffer {
    partner: string;
    amount: number;
    tenure_months: number;
    interest_rate: number;
    emi: number;
    total_payable: number;
}

interface LoanEligibilityProps {
    userId: string;
    projectCost?: number;
    onApply?: (offer: LoanOffer) => void;
}

const LoanEligibility: React.FC<LoanEligibilityProps> = ({ userId, projectCost = 75000, onApply }) => {
    const [amount, setAmount] = useState(projectCost);
    const [income, setIncome] = useState(50000);
    const [isChecking, setIsChecking] = useState(false);
    const [isApplying, setIsApplying] = useState(false);
    const [result, setResult] = useState<any>(null);
    const [selectedOffer, setSelectedOffer] = useState<LoanOffer | null>(null);
    const [error, setError] = useState<string | null>(null);

    const checkEligibility = async () => {
        setIsChecking(true);
        setError(null);
        try {
            const response = await financeAPI.checkLoanEligibility(userId, amount, income);
            setResult(response.data);
        } catch (err: any) {
            setError(err.response?.data?.error || 'Error checking eligibility');
        } finally {
            setIsChecking(false);
        }
    };

    const applyForLoan = async (offer: LoanOffer) => {
        setIsApplying(true);
        setSelectedOffer(offer);
        try {
            await financeAPI.applyForLoan(userId, offer.partner, offer.amount, offer.tenure_months);
            onApply?.(offer);
            // Show success state
        } catch (err: any) {
            setError(err.response?.data?.error || 'Error applying for loan');
        } finally {
            setIsApplying(false);
        }
    };

    const formatCurrency = (num: number) => `₹${new Intl.NumberFormat('en-IN').format(Math.round(num))}`;

    const getPartnerLogo = (partner: string) => {
        const logos: Record<string, string> = {
            capital_float: '💳',
            bajaj_finserv: '🏦',
            kisetsu: '🌱'
        };
        return logos[partner] || '💰';
    };

    const getPartnerName = (partner: string) => {
        const names: Record<string, string> = {
            capital_float: 'Capital Float',
            bajaj_finserv: 'Bajaj Finserv',
            kisetsu: 'Kisetsu'
        };
        return names[partner] || partner;
    };

    return (
        <div className="bg-white rounded-2xl shadow-lg overflow-hidden">
            {/* Header */}
            <div className="bg-gradient-to-r from-emerald-500 to-teal-600 p-6">
                <div className="flex items-center gap-3 mb-4">
                    <div className="w-12 h-12 bg-white/20 rounded-xl flex items-center justify-center">
                        <CreditCard className="w-6 h-6 text-white" />
                    </div>
                    <div>
                        <h2 className="text-xl font-bold text-white">RWH Green Loans</h2>
                        <p className="text-white/70 text-sm">0% processing fee • Instant approval</p>
                    </div>
                </div>
            </div>

            <div className="p-6 space-y-6">
                {/* Input Form */}
                <div className="grid grid-cols-2 gap-4">
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Loan Amount
                        </label>
                        <div className="relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
                            <input
                                type="number"
                                value={amount}
                                onChange={(e) => setAmount(Number(e.target.value))}
                                className="w-full pl-8 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                            />
                        </div>
                        <p className="text-xs text-gray-500 mt-1">₹10,000 - ₹5,00,000</p>
                    </div>
                    <div>
                        <label className="block text-sm font-medium text-gray-700 mb-2">
                            Monthly Income
                        </label>
                        <div className="relative">
                            <span className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-500">₹</span>
                            <input
                                type="number"
                                value={income}
                                onChange={(e) => setIncome(Number(e.target.value))}
                                className="w-full pl-8 pr-4 py-3 border rounded-xl focus:ring-2 focus:ring-emerald-500 focus:border-transparent"
                            />
                        </div>
                    </div>
                </div>

                <button
                    onClick={checkEligibility}
                    disabled={isChecking}
                    className="w-full py-4 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-semibold hover:opacity-90 transition-opacity disabled:opacity-50 flex items-center justify-center gap-2"
                >
                    {isChecking ? (
                        <>
                            <Loader2 className="w-5 h-5 animate-spin" />
                            Checking...
                        </>
                    ) : (
                        <>
                            <TrendingUp className="w-5 h-5" />
                            Check Eligibility
                        </>
                    )}
                </button>

                {error && (
                    <div className="p-4 bg-red-50 border border-red-200 rounded-xl flex items-center gap-3">
                        <AlertCircle className="w-5 h-5 text-red-500" />
                        <p className="text-red-700">{error}</p>
                    </div>
                )}

                {/* Results */}
                {result && (
                    <div className="space-y-4">
                        {/* Eligibility Status */}
                        <div className={`p-4 rounded-xl ${result.eligible ? 'bg-green-50 border border-green-200' : 'bg-yellow-50 border border-yellow-200'}`}>
                            <div className="flex items-center gap-3">
                                {result.eligible ? (
                                    <Check className="w-6 h-6 text-green-600" />
                                ) : (
                                    <AlertCircle className="w-6 h-6 text-yellow-600" />
                                )}
                                <div>
                                    <p className={`font-semibold ${result.eligible ? 'text-green-800' : 'text-yellow-800'}`}>
                                        {result.eligible ? '✅ Pre-approved!' : '⚠️ Partial Eligibility'}
                                    </p>
                                    <p className="text-sm text-gray-600">
                                        Credit Score: {result.credit_score_range} • Max: {formatCurrency(result.max_amount)}
                                    </p>
                                </div>
                            </div>
                        </div>

                        {/* Offers */}
                        {result.offers && result.offers.length > 0 && (
                            <div className="space-y-3">
                                <h3 className="font-semibold text-gray-800">Available Offers</h3>
                                {result.offers.slice(0, 4).map((offer: LoanOffer, idx: number) => (
                                    <div
                                        key={idx}
                                        className="border rounded-xl p-4 hover:border-emerald-400 hover:shadow-md transition-all cursor-pointer"
                                        onClick={() => setSelectedOffer(offer)}
                                    >
                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-3">
                                                <span className="text-2xl">{getPartnerLogo(offer.partner)}</span>
                                                <div>
                                                    <p className="font-semibold text-gray-800">{getPartnerName(offer.partner)}</p>
                                                    <p className="text-sm text-gray-500">{offer.tenure_months} months @ {offer.interest_rate}% p.a.</p>
                                                </div>
                                            </div>
                                            <div className="text-right">
                                                <p className="text-lg font-bold text-emerald-600">{formatCurrency(offer.emi)}/mo</p>
                                                <p className="text-xs text-gray-500">Total: {formatCurrency(offer.total_payable)}</p>
                                            </div>
                                        </div>

                                        {selectedOffer?.partner === offer.partner && selectedOffer?.tenure_months === offer.tenure_months && (
                                            <div className="mt-4 pt-4 border-t">
                                                <button
                                                    onClick={(e) => { e.stopPropagation(); applyForLoan(offer); }}
                                                    disabled={isApplying}
                                                    className="w-full py-3 bg-gradient-to-r from-emerald-500 to-teal-600 text-white rounded-xl font-semibold hover:opacity-90 transition-opacity disabled:opacity-50"
                                                >
                                                    {isApplying ? 'Applying...' : 'Apply Now - Instant Approval'}
                                                </button>
                                            </div>
                                        )}
                                    </div>
                                ))}
                            </div>
                        )}
                    </div>
                )}
            </div>
        </div>
    );
};

export default LoanEligibility;
