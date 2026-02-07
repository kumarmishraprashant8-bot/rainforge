/**
 * EMI Calculator Component
 * Financing calculator for RWH installation
 */

import { useState, useEffect } from 'react';
import { Calculator, Building, CreditCard, Check, Info, ChevronRight, Percent, Calendar, DollarSign } from 'lucide-react';

interface EMIResult {
    emi: number;
    totalPayment: number;
    totalInterest: number;
    monthlyBreakdown: { month: number; principal: number; interest: number; balance: number }[];
}

interface LoanPartner {
    id: string;
    name: string;
    logo: string;
    interestRate: number;
    maxTenure: number;
    processingFee: number;
    features: string[];
}

const EMICalculator = () => {
    const [principal, setPrincipal] = useState(50000);
    const [interestRate, setInterestRate] = useState(12);
    const [tenure, setTenure] = useState(12);
    const [result, setResult] = useState<EMIResult | null>(null);
    const [selectedPartner, setSelectedPartner] = useState<string | null>(null);

    const loanPartners: LoanPartner[] = [
        {
            id: 'sbi',
            name: 'SBI Green Loan',
            logo: '🏦',
            interestRate: 9.5,
            maxTenure: 60,
            processingFee: 0.5,
            features: ['No collateral up to ₹2L', 'Quick approval', 'Minimal documentation']
        },
        {
            id: 'hdfc',
            name: 'HDFC Eco Finance',
            logo: '💳',
            interestRate: 10.5,
            maxTenure: 48,
            processingFee: 1,
            features: ['Instant approval', 'Flexible repayment', 'Zero foreclosure charges']
        },
        {
            id: 'axis',
            name: 'Axis Green Credit',
            logo: '🌿',
            interestRate: 11,
            maxTenure: 36,
            processingFee: 0.75,
            features: ['Special rates for solar+RWH', 'Cashback on timely payment']
        },
        {
            id: 'bajaj',
            name: 'Bajaj Finserv',
            logo: '⚡',
            interestRate: 12.5,
            maxTenure: 24,
            processingFee: 1.5,
            features: ['No income proof needed', 'EMI starting ₹999', 'Pre-approved offers']
        }
    ];

    // Calculate EMI
    useEffect(() => {
        const monthlyRate = interestRate / 12 / 100;
        const n = tenure;

        if (monthlyRate > 0) {
            const emi = principal * monthlyRate * Math.pow(1 + monthlyRate, n) / (Math.pow(1 + monthlyRate, n) - 1);
            const totalPayment = emi * n;
            const totalInterest = totalPayment - principal;

            // Generate monthly breakdown
            let balance = principal;
            const breakdown = [];
            for (let i = 1; i <= n; i++) {
                const interestPart = balance * monthlyRate;
                const principalPart = emi - interestPart;
                balance -= principalPart;
                breakdown.push({
                    month: i,
                    principal: Math.round(principalPart),
                    interest: Math.round(interestPart),
                    balance: Math.max(0, Math.round(balance))
                });
            }

            setResult({
                emi: Math.round(emi),
                totalPayment: Math.round(totalPayment),
                totalInterest: Math.round(totalInterest),
                monthlyBreakdown: breakdown
            });
        }
    }, [principal, interestRate, tenure]);

    const handlePartnerSelect = (partner: LoanPartner) => {
        setSelectedPartner(partner.id);
        setInterestRate(partner.interestRate);
        if (tenure > partner.maxTenure) setTenure(partner.maxTenure);
    };

    return (
        <div className="glass rounded-2xl p-6 space-y-6">
            <div className="flex items-center gap-3 mb-2">
                <div className="p-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
                    <Calculator className="text-white" size={24} />
                </div>
                <div>
                    <h2 className="text-xl font-bold text-white">EMI Calculator</h2>
                    <p className="text-gray-400 text-sm">Finance your RWH installation</p>
                </div>
            </div>

            {/* Loan Partners */}
            <div>
                <h3 className="text-sm font-medium text-gray-400 mb-3">Select Financing Partner</h3>
                <div className="grid grid-cols-2 lg:grid-cols-4 gap-3">
                    {loanPartners.map(partner => (
                        <button
                            key={partner.id}
                            onClick={() => handlePartnerSelect(partner)}
                            className={`p-3 rounded-xl text-left transition-all ${selectedPartner === partner.id
                                    ? 'bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border-2 border-cyan-500'
                                    : 'bg-white/5 border-2 border-transparent hover:border-white/20'
                                }`}
                        >
                            <div className="text-2xl mb-1">{partner.logo}</div>
                            <div className="text-white font-medium text-sm">{partner.name}</div>
                            <div className="text-cyan-400 text-xs">{partner.interestRate}% p.a.</div>
                        </button>
                    ))}
                </div>
            </div>

            {/* Sliders */}
            <div className="space-y-6">
                {/* Loan Amount */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-gray-400 text-sm flex items-center gap-2">
                            <DollarSign size={14} /> Loan Amount
                        </label>
                        <span className="text-white font-bold">₹{principal.toLocaleString()}</span>
                    </div>
                    <input
                        type="range"
                        min={10000}
                        max={500000}
                        step={5000}
                        value={principal}
                        onChange={(e) => setPrincipal(Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-cyan-500 [&::-webkit-slider-thumb]:to-blue-500"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>₹10,000</span>
                        <span>₹5,00,000</span>
                    </div>
                </div>

                {/* Interest Rate */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-gray-400 text-sm flex items-center gap-2">
                            <Percent size={14} /> Interest Rate
                        </label>
                        <span className="text-white font-bold">{interestRate}%</span>
                    </div>
                    <input
                        type="range"
                        min={6}
                        max={18}
                        step={0.5}
                        value={interestRate}
                        onChange={(e) => setInterestRate(Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-green-500 [&::-webkit-slider-thumb]:to-emerald-500"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>6%</span>
                        <span>18%</span>
                    </div>
                </div>

                {/* Tenure */}
                <div>
                    <div className="flex justify-between mb-2">
                        <label className="text-gray-400 text-sm flex items-center gap-2">
                            <Calendar size={14} /> Loan Tenure
                        </label>
                        <span className="text-white font-bold">{tenure} months</span>
                    </div>
                    <input
                        type="range"
                        min={6}
                        max={60}
                        step={6}
                        value={tenure}
                        onChange={(e) => setTenure(Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer [&::-webkit-slider-thumb]:appearance-none [&::-webkit-slider-thumb]:w-5 [&::-webkit-slider-thumb]:h-5 [&::-webkit-slider-thumb]:rounded-full [&::-webkit-slider-thumb]:bg-gradient-to-r [&::-webkit-slider-thumb]:from-purple-500 [&::-webkit-slider-thumb]:to-pink-500"
                    />
                    <div className="flex justify-between text-xs text-gray-500 mt-1">
                        <span>6 months</span>
                        <span>60 months</span>
                    </div>
                </div>
            </div>

            {/* Results */}
            {result && (
                <div className="space-y-4">
                    {/* EMI Display */}
                    <div className="bg-gradient-to-r from-cyan-500/20 to-blue-500/20 border border-cyan-500/30 rounded-2xl p-6 text-center">
                        <p className="text-gray-400 text-sm mb-1">Your Monthly EMI</p>
                        <div className="text-4xl font-black text-white">₹{result.emi.toLocaleString()}</div>
                        <p className="text-cyan-400 text-sm mt-2">
                            for {tenure} months
                        </p>
                    </div>

                    {/* Breakdown */}
                    <div className="grid grid-cols-2 gap-4">
                        <div className="bg-white/5 rounded-xl p-4">
                            <div className="text-gray-400 text-sm">Total Payment</div>
                            <div className="text-xl font-bold text-white">₹{result.totalPayment.toLocaleString()}</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4">
                            <div className="text-gray-400 text-sm">Total Interest</div>
                            <div className="text-xl font-bold text-yellow-400">₹{result.totalInterest.toLocaleString()}</div>
                        </div>
                    </div>

                    {/* Visual Breakdown */}
                    <div className="bg-white/5 rounded-xl p-4">
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-400">Principal vs Interest</span>
                        </div>
                        <div className="flex h-4 rounded-full overflow-hidden">
                            <div
                                className="bg-gradient-to-r from-cyan-500 to-blue-500"
                                style={{ width: `${(principal / result.totalPayment) * 100}%` }}
                            />
                            <div
                                className="bg-gradient-to-r from-yellow-500 to-orange-500"
                                style={{ width: `${(result.totalInterest / result.totalPayment) * 100}%` }}
                            />
                        </div>
                        <div className="flex justify-between text-xs mt-2">
                            <span className="text-cyan-400">Principal: ₹{principal.toLocaleString()}</span>
                            <span className="text-yellow-400">Interest: ₹{result.totalInterest.toLocaleString()}</span>
                        </div>
                    </div>

                    {/* Apply Button */}
                    <button className="w-full py-4 bg-gradient-to-r from-green-500 to-emerald-500 text-white font-bold rounded-xl hover:scale-[1.02] transition-transform flex items-center justify-center gap-2">
                        <CreditCard size={20} />
                        Apply for Loan
                        <ChevronRight size={18} />
                    </button>

                    {/* Note */}
                    <div className="flex items-start gap-2 text-gray-500 text-xs">
                        <Info size={14} className="flex-shrink-0 mt-0.5" />
                        <p>EMI calculation is indicative. Actual EMI may vary based on credit score and bank policies. Subject to approval.</p>
                    </div>
                </div>
            )}
        </div>
    );
};

export default EMICalculator;
