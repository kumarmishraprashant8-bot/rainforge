/**
 * ROI Calculator Component
 * Calculate return on investment for RWH installation
 */

import { useState, useEffect } from 'react';
import { Calculator, TrendingUp, DollarSign, Calendar, Droplets, Zap, CheckCircle } from 'lucide-react';

interface ROIInputs {
    installationCost: number;
    monthlyWaterBill: number;
    roofArea: number;
    tankSize: number;
    waterRate: number;
}

const ROICalculator = () => {
    const [inputs, setInputs] = useState<ROIInputs>({
        installationCost: 35000,
        monthlyWaterBill: 1500,
        roofArea: 100,
        tankSize: 5000,
        waterRate: 0.05 // ₹ per liter
    });

    const [results, setResults] = useState({
        annualSavings: 0,
        paybackMonths: 0,
        fiveYearSavings: 0,
        tenYearSavings: 0,
        roi: 0,
        waterSavedAnnually: 0
    });

    useEffect(() => {
        // Calculate ROI
        const avgRainfallMm = 800; // Average annual rainfall
        const runoffCoefficient = 0.8;
        const annualCollection = inputs.roofArea * avgRainfallMm * runoffCoefficient; // Liters

        const annualSavings = Math.min(annualCollection * inputs.waterRate, inputs.monthlyWaterBill * 12 * 0.6);
        const paybackMonths = Math.ceil(inputs.installationCost / (annualSavings / 12));
        const fiveYearSavings = (annualSavings * 5) - inputs.installationCost;
        const tenYearSavings = (annualSavings * 10) - inputs.installationCost;
        const roi = ((annualSavings * 10 - inputs.installationCost) / inputs.installationCost) * 100;

        setResults({
            annualSavings: Math.round(annualSavings),
            paybackMonths,
            fiveYearSavings: Math.round(fiveYearSavings),
            tenYearSavings: Math.round(tenYearSavings),
            roi: Math.round(roi),
            waterSavedAnnually: Math.round(annualCollection)
        });
    }, [inputs]);

    const updateInput = (key: keyof ROIInputs, value: number) => {
        setInputs(prev => ({ ...prev, [key]: value }));
    };

    return (
        <div className="glass rounded-2xl p-6 bg-gradient-to-r from-green-500/10 to-emerald-500/10 border border-green-500/20">
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl">
                    <Calculator className="text-white" size={24} />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white">ROI Calculator</h3>
                    <p className="text-gray-400 text-sm">See when your investment pays off</p>
                </div>
            </div>

            {/* Input Sliders */}
            <div className="space-y-5 mb-6">
                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Installation Cost</span>
                        <span className="text-white font-medium">₹{inputs.installationCost.toLocaleString()}</span>
                    </div>
                    <input
                        type="range"
                        min="10000"
                        max="100000"
                        step="5000"
                        value={inputs.installationCost}
                        onChange={(e) => updateInput('installationCost', Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-green-500"
                    />
                </div>

                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Monthly Water Bill</span>
                        <span className="text-white font-medium">₹{inputs.monthlyWaterBill.toLocaleString()}</span>
                    </div>
                    <input
                        type="range"
                        min="500"
                        max="5000"
                        step="100"
                        value={inputs.monthlyWaterBill}
                        onChange={(e) => updateInput('monthlyWaterBill', Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-green-500"
                    />
                </div>

                <div>
                    <div className="flex justify-between text-sm mb-2">
                        <span className="text-gray-400">Roof Area</span>
                        <span className="text-white font-medium">{inputs.roofArea} m²</span>
                    </div>
                    <input
                        type="range"
                        min="50"
                        max="500"
                        step="10"
                        value={inputs.roofArea}
                        onChange={(e) => updateInput('roofArea', Number(e.target.value))}
                        className="w-full h-2 bg-white/10 rounded-full appearance-none cursor-pointer accent-green-500"
                    />
                </div>
            </div>

            {/* Results */}
            <div className="grid grid-cols-2 gap-4 mb-6">
                <div className="bg-white/5 rounded-xl p-4 text-center">
                    <Calendar className="mx-auto text-yellow-400 mb-2" size={20} />
                    <div className="text-3xl font-black text-white">{results.paybackMonths}</div>
                    <div className="text-gray-500 text-xs">Months to Payback</div>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                    <DollarSign className="mx-auto text-green-400 mb-2" size={20} />
                    <div className="text-3xl font-black text-green-400">₹{(results.annualSavings / 1000).toFixed(1)}k</div>
                    <div className="text-gray-500 text-xs">Annual Savings</div>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                    <TrendingUp className="mx-auto text-cyan-400 mb-2" size={20} />
                    <div className="text-3xl font-black text-cyan-400">{results.roi}%</div>
                    <div className="text-gray-500 text-xs">10-Year ROI</div>
                </div>
                <div className="bg-white/5 rounded-xl p-4 text-center">
                    <Droplets className="mx-auto text-blue-400 mb-2" size={20} />
                    <div className="text-3xl font-black text-blue-400">{(results.waterSavedAnnually / 1000).toFixed(0)}k L</div>
                    <div className="text-gray-500 text-xs">Water/Year</div>
                </div>
            </div>

            {/* Timeline */}
            <div className="bg-white/5 rounded-xl p-4 mb-4">
                <div className="text-sm text-gray-400 mb-3">Savings Timeline</div>
                <div className="relative">
                    <div className="h-2 bg-white/10 rounded-full">
                        <div
                            className="absolute left-0 h-2 bg-gradient-to-r from-green-500 to-emerald-500 rounded-full"
                            style={{ width: `${Math.min(100, (results.paybackMonths / 60) * 100)}%` }}
                        />
                    </div>
                    <div className="flex justify-between mt-2 text-xs text-gray-500">
                        <span>Now</span>
                        <span className="text-yellow-400">← Payback ({results.paybackMonths}mo)</span>
                        <span>5 Years</span>
                    </div>
                </div>
                <div className="grid grid-cols-2 gap-4 mt-4">
                    <div>
                        <div className="text-gray-500 text-xs">5-Year Net Savings</div>
                        <div className={`text-lg font-bold ${results.fiveYearSavings > 0 ? 'text-green-400' : 'text-red-400'}`}>
                            ₹{results.fiveYearSavings.toLocaleString()}
                        </div>
                    </div>
                    <div>
                        <div className="text-gray-500 text-xs">10-Year Net Savings</div>
                        <div className="text-lg font-bold text-green-400">₹{results.tenYearSavings.toLocaleString()}</div>
                    </div>
                </div>
            </div>

            {/* Verdict */}
            <div className={`flex items-center gap-3 p-4 rounded-xl ${results.paybackMonths < 36
                    ? 'bg-green-500/10 border border-green-500/20'
                    : 'bg-yellow-500/10 border border-yellow-500/20'
                }`}>
                {results.paybackMonths < 36 ? (
                    <>
                        <CheckCircle className="text-green-400" size={24} />
                        <div>
                            <div className="text-green-400 font-bold">Excellent Investment! 🎉</div>
                            <div className="text-gray-400 text-sm">Your system pays for itself in under 3 years</div>
                        </div>
                    </>
                ) : (
                    <>
                        <Zap className="text-yellow-400" size={24} />
                        <div>
                            <div className="text-yellow-400 font-bold">Good Long-term Investment</div>
                            <div className="text-gray-400 text-sm">Consider a larger roof area or subsidy options</div>
                        </div>
                    </>
                )}
            </div>
        </div>
    );
};

export default ROICalculator;
