import React, { useState, useEffect } from 'react';
import { Shield, CheckCircle, X, Loader2, Lock } from 'lucide-react';

interface AadhaarKycModalProps {
    isOpen: boolean;
    onClose: () => void;
    onSuccess: (details: any) => void;
}

type Step = 'input' | 'otp' | 'verifying' | 'success';

const AadhaarKycModal: React.FC<AadhaarKycModalProps> = ({ isOpen, onClose, onSuccess }) => {
    const [step, setStep] = useState<Step>('input');
    const [aadhaarNum, setAadhaarNum] = useState('');
    const [otp, setOtp] = useState('');
    const [isLoading, setIsLoading] = useState(false);

    // Reset state when opening
    useEffect(() => {
        if (isOpen) {
            setStep('input');
            setAadhaarNum('');
            setOtp('');
            setIsLoading(false);
        }
    }, [isOpen]);

    if (!isOpen) return null;

    const handleSendOtp = () => {
        if (!aadhaarNum) return;
        setIsLoading(true);
        // Simulate API delay
        setTimeout(() => {
            setIsLoading(false);
            setStep('otp');
        }, 1500);
    };

    const handleVerifyOtp = () => {
        if (!otp) return;
        setIsLoading(true);
        setStep('verifying');
        // Simulate verification delay
        setTimeout(() => {
            setIsLoading(false);
            setStep('success');
            // Trigger success callback after showing the success card for a moment
            // but we keep the modal open so they can see the card
        }, 2000);
    };

    const handleComplete = () => {
        onSuccess({
            status: 'verified',
            verifiedAt: new Date().toISOString(),
            aadhaarLast4: aadhaarNum.slice(-4)
        });
        onClose();
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center p-4 bg-black/80 backdrop-blur-sm animate-fade-in">
            <div className="bg-white rounded-2xl w-full max-w-md overflow-hidden relative shadow-2xl animate-scale-up">

                {/* Close Button */}
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 p-2 text-gray-400 hover:text-gray-600 rounded-full hover:bg-gray-100 transition-colors z-10"
                >
                    <X size={20} />
                </button>

                {/* Header with Govt Branding */}
                <div className="bg-[#fadbac] p-6 text-center border-b border-[#eeba76]">
                    <div className="flex justify-center mb-2">
                        <img src="https://upload.wikimedia.org/wikipedia/en/thumb/c/cf/Aadhaar_Logo.svg/1200px-Aadhaar_Logo.svg.png"
                            alt="Aadhaar"
                            className="h-12 object-contain mix-blend-multiply"
                            onError={(e) => {
                                // Fallback if image fails to load
                                (e.target as HTMLImageElement).src = '';
                                (e.target as HTMLImageElement).style.display = 'none';
                            }}
                        />
                        {/* Fallback Text if image fails */}
                        <div className="text-3xl font-bold text-[#cf3e34] tracking-tighter" style={{ display: 'none' }}>aadhaar</div>
                    </div>
                    <div className="text-[#a42721] font-bold text-lg">Unique Identification Authority of India</div>
                    <div className="text-[#a42721]/70 text-xs tracking-wider uppercase">Government of India</div>
                </div>

                <div className="p-8">
                    {/* STEP 1: INPUT */}
                    {step === 'input' && (
                        <div className="space-y-6">
                            <div className="text-center">
                                <h3 className="text-xl font-bold text-gray-800">e-KYC Verification</h3>
                                <p className="text-gray-500 text-sm mt-1">Enter your 12-digit Aadhaar number to verify your identity.</p>
                            </div>

                            <div className="space-y-2">
                                <label className="text-xs font-bold text-gray-500 uppercase tracking-wider">Aadhaar Number</label>
                                <div className="relative">
                                    <input
                                        type="text"
                                        maxLength={12}
                                        value={aadhaarNum}
                                        onChange={(e) => setAadhaarNum(e.target.value)}
                                        placeholder="0000 0000 0000"
                                        className="w-full px-4 py-3 text-lg font-mono tracking-widest border-2 border-gray-200 rounded-xl focus:border-[#a42721] focus:ring-4 focus:ring-[#a42721]/10 outline-none transition-all placeholder:text-gray-300 text-black bg-white"
                                    />
                                    <div className="absolute right-3 top-1/2 -translate-y-1/2 text-gray-400">
                                        <Shield size={20} />
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleSendOtp}
                                disabled={isLoading}
                                className="w-full py-3 bg-[#a42721] hover:bg-[#86201b] text-white font-bold rounded-xl shadow-lg shadow-red-500/20 disabled:opacity-50 disabled:shadow-none transition-all flex items-center justify-center gap-2"
                            >
                                {isLoading ? <Loader2 className="animate-spin" /> : 'Get OTP'}
                            </button>

                            <div className="flex items-center justify-center gap-2 text-xs text-gray-400">
                                <Lock size={12} />
                                Secured by UIDAI Standard Encryption
                            </div>
                        </div>
                    )}

                    {/* STEP 2: OTP */}
                    {(step === 'otp' || step === 'verifying') && (
                        <div className="space-y-6 animate-fade-in">
                            <div className="text-center">
                                <div className="w-16 h-16 bg-[#e1f5fe] rounded-full flex items-center justify-center mx-auto mb-4 text-[#0288d1]">
                                    <Shield size={32} />
                                </div>
                                <h3 className="text-xl font-bold text-gray-800">Enter OTP</h3>
                                <p className="text-gray-500 text-sm mt-1">
                                    One Time Password sent to mobile ending in ******{aadhaarNum.slice(-4) || '8921'}
                                </p>
                            </div>

                            <div className="space-y-2">
                                <div className="flex justify-center gap-3">
                                    {/* Mock OTP Input Visualization */}
                                    <input
                                        type="text"
                                        maxLength={6}
                                        value={otp}
                                        onChange={(e) => setOtp(e.target.value)}
                                        placeholder="• • • • • •"
                                        className="w-48 text-center px-4 py-3 text-2xl font-mono tracking-[0.5em] border-2 border-gray-200 rounded-xl focus:border-[#0288d1] focus:ring-4 focus:ring-[#0288d1]/10 outline-none transition-all placeholder:text-gray-300 text-black bg-white"
                                        disabled={step === 'verifying'}
                                        autoFocus
                                    />
                                </div>
                                <div className="text-center">
                                    <button className="text-xs text-[#0288d1] font-medium hover:underline">Resend OTP</button>
                                </div>
                            </div>

                            <button
                                onClick={handleVerifyOtp}
                                disabled={otp.length === 0 || step === 'verifying'}
                                className="w-full py-3 bg-[#0288d1] hover:bg-[#0277bd] text-white font-bold rounded-xl shadow-lg shadow-blue-500/20 disabled:opacity-50 disabled:shadow-none transition-all flex items-center justify-center gap-2"
                            >
                                {step === 'verifying' ? (
                                    <>
                                        <Loader2 className="animate-spin" /> Verifying...
                                    </>
                                ) : (
                                    'Verify & Proceed'
                                )}
                            </button>
                        </div>
                    )}

                    {/* STEP 3: SUCCESS (Digital Card) */}
                    {step === 'success' && (
                        <div className="animate-flip-in">
                            <div className="text-center mb-6">
                                <div className="inline-flex items-center justify-center w-12 h-12 bg-green-100 text-green-600 rounded-full mb-2">
                                    <CheckCircle size={24} />
                                </div>
                                <h3 className="text-xl font-bold text-gray-800">Verification Successful!</h3>
                            </div>

                            {/* Digital Aadhaar Card Mock */}
                            <div className="relative overflow-hidden rounded-xl border border-gray-200 shadow-xl bg-white mb-6">
                                {/* Card Header */}
                                <div className="h-12 bg-gradient-to-r from-orange-400 via-white to-green-400 opacity-20 absolute top-0 left-0 right-0"></div>
                                <div className="p-4 pt-6 relative">
                                    <div className="flex gap-4">
                                        <div className="w-20 h-24 bg-gray-200 rounded-lg overflow-hidden flex-shrink-0">
                                            <img src="https://api.dicebear.com/7.x/avataaars/svg?seed=gov_user_123" alt="Profile" className="w-full h-full object-cover" />
                                        </div>
                                        <div className="flex-1 space-y-1">
                                            <div className="text-xs text-gray-500 uppercase font-bold">Name</div>
                                            <div className="font-bold text-gray-800">Rahul Sharma</div>

                                            <div className="text-xs text-gray-500 uppercase font-bold mt-2">DOB</div>
                                            <div className="text-sm text-gray-800">12-08-1994</div>

                                            <div className="text-xs text-gray-500 uppercase font-bold mt-2">Gender</div>
                                            <div className="text-sm text-gray-800">Male</div>
                                        </div>
                                        <div className="w-12 pt-2">
                                            <div className="border-2 border-black p-1 bg-white">
                                                <div className="w-full h-full bg-black/10 aspect-square"></div>
                                            </div>
                                        </div>
                                    </div>
                                    <div className="mt-4 pt-3 border-t border-dashed border-gray-300 flex justify-between items-center">
                                        <div className="text-lg font-mono font-bold tracking-wider text-gray-700">
                                            XXXX XXXX {aadhaarNum.slice(-4)}
                                        </div>
                                        <div className="text-green-600 font-bold text-xs flex items-center gap-1">
                                            <CheckCircle size={10} /> VERIFIED
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <button
                                onClick={handleComplete}
                                className="w-full py-3 bg-green-600 hover:bg-green-700 text-white font-bold rounded-xl shadow-lg shadow-green-500/20 transition-all flex items-center justify-center gap-2"
                            >
                                Continue to Profile
                            </button>
                        </div>
                    )}

                </div>
            </div>
        </div>
    );
};

export default AadhaarKycModal;
