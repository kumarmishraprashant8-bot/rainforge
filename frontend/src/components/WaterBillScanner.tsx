/**
 * Water Bill Scanner Component
 * OCR simulation - scan/upload bill to auto-calculate savings
 */

import { useState } from 'react';
import { Camera, Upload, FileText, CheckCircle, TrendingDown, Loader, DollarSign, Droplets, RefreshCw } from 'lucide-react';

interface BillData {
    billDate: string;
    units: number;
    amount: number;
    provider: string;
}

const WaterBillScanner = () => {
    const [step, setStep] = useState<'upload' | 'scanning' | 'result'>('upload');
    const [billData, setBillData] = useState<BillData | null>(null);
    const [savings, setSavings] = useState({ amount: 0, percent: 0, liters: 0 });

    const handleFileUpload = () => {
        // Simulate scanning
        setStep('scanning');

        setTimeout(() => {
            // Simulated OCR result
            const mockBill: BillData = {
                billDate: 'January 2026',
                units: 25000,
                amount: 1850,
                provider: 'BWSSB Bangalore'
            };
            setBillData(mockBill);

            // Calculate potential savings (60% reduction with RWH)
            setSavings({
                amount: Math.round(mockBill.amount * 0.6),
                percent: 60,
                liters: Math.round(mockBill.units * 0.6)
            });

            setStep('result');
        }, 2500);
    };

    const resetScanner = () => {
        setStep('upload');
        setBillData(null);
    };

    return (
        <div className="glass rounded-2xl p-6">
            {/* Header */}
            <div className="flex items-center gap-3 mb-6">
                <div className="p-3 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl">
                    <FileText className="text-white" size={24} />
                </div>
                <div>
                    <h3 className="text-xl font-bold text-white">Bill Scanner</h3>
                    <p className="text-gray-400 text-sm">Scan your water bill to see savings</p>
                </div>
            </div>

            {/* Upload Step */}
            {step === 'upload' && (
                <div>
                    <div
                        onClick={handleFileUpload}
                        className="border-2 border-dashed border-white/20 hover:border-blue-500/50 rounded-2xl p-8 text-center cursor-pointer transition-all hover:bg-white/5"
                    >
                        <div className="w-16 h-16 mx-auto mb-4 rounded-2xl bg-blue-500/20 flex items-center justify-center">
                            <Upload className="text-blue-400" size={32} />
                        </div>
                        <h4 className="text-white font-semibold mb-2">Upload Water Bill</h4>
                        <p className="text-gray-500 text-sm mb-4">
                            Drag & drop or click to upload your latest water bill
                        </p>
                        <div className="flex justify-center gap-3">
                            <span className="px-3 py-1 bg-white/10 rounded-lg text-xs text-gray-400">PDF</span>
                            <span className="px-3 py-1 bg-white/10 rounded-lg text-xs text-gray-400">JPG</span>
                            <span className="px-3 py-1 bg-white/10 rounded-lg text-xs text-gray-400">PNG</span>
                        </div>
                    </div>

                    <div className="flex items-center gap-4 my-6">
                        <div className="flex-1 h-px bg-white/10" />
                        <span className="text-gray-500 text-sm">or</span>
                        <div className="flex-1 h-px bg-white/10" />
                    </div>

                    <button
                        onClick={handleFileUpload}
                        className="w-full flex items-center justify-center gap-2 py-4 bg-gradient-to-r from-blue-500 to-purple-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity"
                    >
                        <Camera size={20} />
                        Take Photo of Bill
                    </button>
                </div>
            )}

            {/* Scanning Step */}
            {step === 'scanning' && (
                <div className="text-center py-12">
                    <div className="relative w-24 h-24 mx-auto mb-6">
                        <div className="absolute inset-0 border-4 border-blue-500/30 rounded-full animate-ping" />
                        <div className="absolute inset-0 flex items-center justify-center">
                            <Loader className="text-blue-400 animate-spin" size={40} />
                        </div>
                    </div>
                    <h4 className="text-white font-semibold mb-2">Scanning your bill...</h4>
                    <p className="text-gray-500 text-sm">Extracting water usage and cost data</p>
                    <div className="mt-6 space-y-2">
                        <div className="flex items-center gap-2 justify-center text-sm">
                            <CheckCircle className="text-green-400" size={16} />
                            <span className="text-gray-400">Bill detected</span>
                        </div>
                        <div className="flex items-center gap-2 justify-center text-sm">
                            <div className="w-4 h-4 border-2 border-blue-400 border-t-transparent rounded-full animate-spin" />
                            <span className="text-gray-400">Reading consumption data...</span>
                        </div>
                    </div>
                </div>
            )}

            {/* Result Step */}
            {step === 'result' && billData && (
                <div>
                    {/* Detected Bill Info */}
                    <div className="bg-white/5 rounded-xl p-4 mb-6">
                        <div className="text-sm text-gray-500 mb-2">Detected Bill</div>
                        <div className="flex items-center justify-between">
                            <div>
                                <div className="text-white font-semibold">{billData.provider}</div>
                                <div className="text-gray-400 text-sm">{billData.billDate}</div>
                            </div>
                            <div className="text-right">
                                <div className="text-2xl font-bold text-white">₹{billData.amount}</div>
                                <div className="text-gray-500 text-sm">{billData.units.toLocaleString()} L</div>
                            </div>
                        </div>
                    </div>

                    {/* Savings Result */}
                    <div className="bg-gradient-to-r from-green-500/20 to-emerald-500/20 border border-green-500/30 rounded-2xl p-6 text-center mb-6">
                        <div className="text-sm text-green-400 mb-2">With RainForge, you could save</div>
                        <div className="text-5xl font-black text-green-400 mb-1">
                            ₹{savings.amount.toLocaleString()}
                        </div>
                        <div className="text-gray-400">per month ({savings.percent}% reduction)</div>

                        <div className="grid grid-cols-2 gap-4 mt-6">
                            <div className="bg-white/10 rounded-xl p-3">
                                <TrendingDown className="mx-auto text-green-400 mb-1" size={20} />
                                <div className="text-lg font-bold text-white">₹{(savings.amount * 12).toLocaleString()}</div>
                                <div className="text-gray-500 text-xs">Annual Savings</div>
                            </div>
                            <div className="bg-white/10 rounded-xl p-3">
                                <Droplets className="mx-auto text-cyan-400 mb-1" size={20} />
                                <div className="text-lg font-bold text-white">{(savings.liters / 1000).toFixed(0)}k L</div>
                                <div className="text-gray-500 text-xs">Water Saved/Month</div>
                            </div>
                        </div>
                    </div>

                    {/* Comparison Bar */}
                    <div className="mb-6">
                        <div className="flex justify-between text-sm mb-2">
                            <span className="text-gray-400">Current Bill</span>
                            <span className="text-gray-400">After RWH</span>
                        </div>
                        <div className="flex gap-2 items-end h-16">
                            <div className="flex-1 bg-red-500/30 rounded-lg relative" style={{ height: '100%' }}>
                                <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-white text-sm font-medium">
                                    ₹{billData.amount}
                                </span>
                            </div>
                            <div className="flex-1 bg-green-500/30 rounded-lg relative" style={{ height: '40%' }}>
                                <span className="absolute bottom-2 left-1/2 -translate-x-1/2 text-white text-sm font-medium">
                                    ₹{billData.amount - savings.amount}
                                </span>
                            </div>
                        </div>
                    </div>

                    {/* Actions */}
                    <div className="flex gap-3">
                        <button
                            onClick={resetScanner}
                            className="flex-1 flex items-center justify-center gap-2 py-3 bg-white/10 rounded-xl text-white hover:bg-white/20 transition-colors"
                        >
                            <RefreshCw size={18} />
                            Scan Another
                        </button>
                        <button className="flex-1 flex items-center justify-center gap-2 py-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-xl text-white font-semibold hover:opacity-90 transition-opacity">
                            <DollarSign size={18} />
                            Get Free Quote
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

export default WaterBillScanner;
