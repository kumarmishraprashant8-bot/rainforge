/**
 * User Profile Form Component
 * Complete user profile with KYC, bank details, and preferences
 */

import React, { useState } from 'react';

interface UserProfile {
    fullName: string;
    email: string;
    phone: string;
    alternatePhone: string;
    addressLine1: string;
    addressLine2: string;
    city: string;
    district: string;
    state: string;
    pincode: string;
    preferredLanguage: string;
    emailNotifications: boolean;
    smsNotifications: boolean;
    whatsappNotifications: boolean;
    pushNotifications: boolean;
}

interface KYCDetails {
    aadhaarNumber: string;
    panNumber: string;
    voterId: string;
    aadhaarVerified: boolean;
    panVerified: boolean;
}

interface BankDetails {
    accountHolderName: string;
    accountNumber: string;
    confirmAccountNumber: string;
    ifscCode: string;
    bankName: string;
    branchName: string;
    accountType: string;
    upiId: string;
    verified: boolean;
}

interface UserProfileFormProps {
    initialProfile?: Partial<UserProfile>;
    onSave: (profile: UserProfile, kyc: KYCDetails, bank: BankDetails) => void;
    onCancel?: () => void;
}

const LANGUAGES = [
    { code: 'en', name: 'English' },
    { code: 'hi', name: 'हिंदी (Hindi)' },
    { code: 'ta', name: 'தமிழ் (Tamil)' },
    { code: 'te', name: 'తెలుగు (Telugu)' },
    { code: 'kn', name: 'ಕನ್ನಡ (Kannada)' },
    { code: 'mr', name: 'मराठी (Marathi)' },
    { code: 'gu', name: 'ગુજરાતી (Gujarati)' },
    { code: 'bn', name: 'বাংলা (Bengali)' },
    { code: 'ml', name: 'മലയാളം (Malayalam)' },
    { code: 'pa', name: 'ਪੰਜਾਬੀ (Punjabi)' },
    { code: 'or', name: 'ଓଡ଼ିଆ (Odia)' },
];

const STATES = [
    'Andhra Pradesh', 'Arunachal Pradesh', 'Assam', 'Bihar', 'Chhattisgarh',
    'Goa', 'Gujarat', 'Haryana', 'Himachal Pradesh', 'Jharkhand', 'Karnataka',
    'Kerala', 'Madhya Pradesh', 'Maharashtra', 'Manipur', 'Meghalaya', 'Mizoram',
    'Nagaland', 'Odisha', 'Punjab', 'Rajasthan', 'Sikkim', 'Tamil Nadu',
    'Telangana', 'Tripura', 'Uttar Pradesh', 'Uttarakhand', 'West Bengal',
    'Delhi', 'Jammu and Kashmir', 'Ladakh', 'Puducherry', 'Chandigarh'
];

export const UserProfileForm: React.FC<UserProfileFormProps> = ({
    initialProfile,
    onSave,
    onCancel
}) => {
    const [activeTab, setActiveTab] = useState<'profile' | 'kyc' | 'bank'>('profile');

    const [profile, setProfile] = useState<UserProfile>({
        fullName: initialProfile?.fullName || '',
        email: initialProfile?.email || '',
        phone: initialProfile?.phone || '',
        alternatePhone: '',
        addressLine1: '',
        addressLine2: '',
        city: '',
        district: '',
        state: '',
        pincode: '',
        preferredLanguage: 'en',
        emailNotifications: true,
        smsNotifications: true,
        whatsappNotifications: false,
        pushNotifications: true,
    });

    const [kyc, setKyc] = useState<KYCDetails>({
        aadhaarNumber: '',
        panNumber: '',
        voterId: '',
        aadhaarVerified: false,
        panVerified: false,
    });

    const [bank, setBank] = useState<BankDetails>({
        accountHolderName: '',
        accountNumber: '',
        confirmAccountNumber: '',
        ifscCode: '',
        bankName: '',
        branchName: '',
        accountType: 'savings',
        upiId: '',
        verified: false,
    });

    const [verifying, setVerifying] = useState<'aadhaar' | 'pan' | 'bank' | null>(null);
    const [errors, setErrors] = useState<Record<string, string>>({});

    const validateAadhaar = (aadhaar: string): boolean => {
        return /^\d{12}$/.test(aadhaar);
    };

    const validatePAN = (pan: string): boolean => {
        return /^[A-Z]{5}[0-9]{4}[A-Z]{1}$/.test(pan.toUpperCase());
    };

    const validateIFSC = (ifsc: string): boolean => {
        return /^[A-Z]{4}0[A-Z0-9]{6}$/.test(ifsc.toUpperCase());
    };

    const handleVerifyAadhaar = async () => {
        if (!validateAadhaar(kyc.aadhaarNumber)) {
            setErrors({ ...errors, aadhaar: 'Aadhaar must be 12 digits' });
            return;
        }

        setVerifying('aadhaar');

        try {
            const response = await fetch('/api/v1/enhanced/profile/verify-aadhaar', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    user_id: 1, // Replace with actual user ID
                    aadhaar_number: kyc.aadhaarNumber,
                    name: profile.fullName,
                }),
            });

            if (response.ok) {
                setKyc({ ...kyc, aadhaarVerified: true });
                setErrors({ ...errors, aadhaar: '' });
            }
        } catch (error) {
            console.error('Aadhaar verification failed:', error);
        } finally {
            setVerifying(null);
        }
    };

    const handleVerifyPAN = async () => {
        if (!validatePAN(kyc.panNumber)) {
            setErrors({ ...errors, pan: 'Invalid PAN format (ABCDE1234F)' });
            return;
        }

        setVerifying('pan');

        try {
            // Mock verification
            await new Promise(resolve => setTimeout(resolve, 1000));
            setKyc({ ...kyc, panVerified: true });
            setErrors({ ...errors, pan: '' });
        } catch (error) {
            console.error('PAN verification failed:', error);
        } finally {
            setVerifying(null);
        }
    };

    const handleVerifyBank = async () => {
        if (bank.accountNumber !== bank.confirmAccountNumber) {
            setErrors({ ...errors, bank: 'Account numbers do not match' });
            return;
        }

        if (!validateIFSC(bank.ifscCode)) {
            setErrors({ ...errors, ifsc: 'Invalid IFSC code format' });
            return;
        }

        setVerifying('bank');

        try {
            // Mock penny drop verification
            await new Promise(resolve => setTimeout(resolve, 2000));
            setBank({ ...bank, verified: true });
            setErrors({ ...errors, bank: '', ifsc: '' });
        } catch (error) {
            console.error('Bank verification failed:', error);
        } finally {
            setVerifying(null);
        }
    };

    const handleSubmit = () => {
        onSave(profile, kyc, bank);
    };

    return (
        <div className="profile-form-container" style={{
            maxWidth: '800px',
            margin: '0 auto',
            padding: '24px',
            background: 'linear-gradient(135deg, rgba(255,255,255,0.95), rgba(248,250,252,0.98))',
            borderRadius: '16px',
            boxShadow: '0 4px 20px rgba(0,0,0,0.08)',
        }}>
            <h2 style={{
                fontSize: '24px',
                fontWeight: 700,
                marginBottom: '24px',
                color: '#1a1a2e',
            }}>
                Complete Your Profile
            </h2>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'profile', label: 'Basic Info', icon: '👤' },
                    { id: 'kyc', label: 'KYC Verification', icon: '🪪' },
                    { id: 'bank', label: 'Bank Details', icon: '🏦' },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveTab(tab.id as any)}
                        style={{
                            flex: 1,
                            padding: '12px 16px',
                            background: activeTab === tab.id
                                ? 'linear-gradient(135deg, #3b82f6, #2563eb)'
                                : 'white',
                            color: activeTab === tab.id ? 'white' : '#64748b',
                            border: activeTab === tab.id ? 'none' : '1px solid #e2e8f0',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            transition: 'all 0.2s ease',
                        }}
                    >
                        <span style={{ marginRight: '8px' }}>{tab.icon}</span>
                        {tab.label}
                    </button>
                ))}
            </div>

            {/* Profile Tab */}
            {activeTab === 'profile' && (
                <div className="profile-tab" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>Full Name *</label>
                            <input
                                type="text"
                                value={profile.fullName}
                                onChange={(e) => setProfile({ ...profile, fullName: e.target.value })}
                                style={inputStyle}
                                placeholder="Enter your full name"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>Email</label>
                            <input
                                type="email"
                                value={profile.email}
                                onChange={(e) => setProfile({ ...profile, email: e.target.value })}
                                style={inputStyle}
                                placeholder="email@example.com"
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>Mobile Number *</label>
                            <input
                                type="tel"
                                value={profile.phone}
                                onChange={(e) => setProfile({ ...profile, phone: e.target.value })}
                                style={inputStyle}
                                placeholder="+91 9XXXXXXXXX"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>Alternate Mobile</label>
                            <input
                                type="tel"
                                value={profile.alternatePhone}
                                onChange={(e) => setProfile({ ...profile, alternatePhone: e.target.value })}
                                style={inputStyle}
                                placeholder="+91 9XXXXXXXXX"
                            />
                        </div>
                    </div>

                    <div>
                        <label style={labelStyle}>Address Line 1 *</label>
                        <input
                            type="text"
                            value={profile.addressLine1}
                            onChange={(e) => setProfile({ ...profile, addressLine1: e.target.value })}
                            style={inputStyle}
                            placeholder="House/Building No., Street"
                        />
                    </div>

                    <div>
                        <label style={labelStyle}>Address Line 2</label>
                        <input
                            type="text"
                            value={profile.addressLine2}
                            onChange={(e) => setProfile({ ...profile, addressLine2: e.target.value })}
                            style={inputStyle}
                            placeholder="Locality, Landmark"
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>City *</label>
                            <input
                                type="text"
                                value={profile.city}
                                onChange={(e) => setProfile({ ...profile, city: e.target.value })}
                                style={inputStyle}
                                placeholder="City"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>District</label>
                            <input
                                type="text"
                                value={profile.district}
                                onChange={(e) => setProfile({ ...profile, district: e.target.value })}
                                style={inputStyle}
                                placeholder="District"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>Pincode *</label>
                            <input
                                type="text"
                                value={profile.pincode}
                                onChange={(e) => setProfile({ ...profile, pincode: e.target.value })}
                                style={inputStyle}
                                maxLength={6}
                                placeholder="6-digit PIN"
                            />
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>State *</label>
                            <select
                                value={profile.state}
                                onChange={(e) => setProfile({ ...profile, state: e.target.value })}
                                style={inputStyle}
                            >
                                <option value="">Select State</option>
                                {STATES.map(state => (
                                    <option key={state} value={state}>{state}</option>
                                ))}
                            </select>
                        </div>
                        <div>
                            <label style={labelStyle}>Preferred Language</label>
                            <select
                                value={profile.preferredLanguage}
                                onChange={(e) => setProfile({ ...profile, preferredLanguage: e.target.value })}
                                style={inputStyle}
                            >
                                {LANGUAGES.map(lang => (
                                    <option key={lang.code} value={lang.code}>{lang.name}</option>
                                ))}
                            </select>
                        </div>
                    </div>

                    {/* Notification Preferences */}
                    <div style={{
                        padding: '16px',
                        background: '#f8fafc',
                        borderRadius: '12px',
                        border: '1px solid #e2e8f0'
                    }}>
                        <h4 style={{ marginBottom: '12px', fontWeight: 600 }}>📬 Notification Preferences</h4>
                        <div style={{ display: 'grid', gridTemplateColumns: 'repeat(2, 1fr)', gap: '12px' }}>
                            {[
                                { key: 'emailNotifications', label: 'Email Notifications' },
                                { key: 'smsNotifications', label: 'SMS Alerts' },
                                { key: 'whatsappNotifications', label: 'WhatsApp Updates' },
                                { key: 'pushNotifications', label: 'Push Notifications' },
                            ].map(pref => (
                                <label key={pref.key} style={{ display: 'flex', alignItems: 'center', gap: '8px' }}>
                                    <input
                                        type="checkbox"
                                        checked={(profile as any)[pref.key]}
                                        onChange={(e) => setProfile({ ...profile, [pref.key]: e.target.checked })}
                                        style={{ width: '18px', height: '18px' }}
                                    />
                                    <span>{pref.label}</span>
                                </label>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* KYC Tab */}
            {activeTab === 'kyc' && (
                <div className="kyc-tab" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{
                        padding: '16px',
                        background: '#fefce8',
                        borderRadius: '12px',
                        border: '1px solid #fde047',
                    }}>
                        <p style={{ margin: 0, fontSize: '14px', color: '#854d0e' }}>
                            ⚠️ KYC verification is required for subsidy applications. Your data is encrypted and secure.
                        </p>
                    </div>

                    {/* Aadhaar */}
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                        <div style={{ flex: 1 }}>
                            <label style={labelStyle}>
                                Aadhaar Number
                                {kyc.aadhaarVerified && <span style={{ color: '#22c55e', marginLeft: '8px' }}>✓ Verified</span>}
                            </label>
                            <input
                                type="text"
                                value={kyc.aadhaarNumber}
                                onChange={(e) => setKyc({ ...kyc, aadhaarNumber: e.target.value.replace(/\D/g, '').slice(0, 12) })}
                                style={inputStyle}
                                maxLength={12}
                                placeholder="XXXX XXXX XXXX"
                                disabled={kyc.aadhaarVerified}
                            />
                            {errors.aadhaar && <span style={errorStyle}>{errors.aadhaar}</span>}
                        </div>
                        <button
                            onClick={handleVerifyAadhaar}
                            disabled={verifying === 'aadhaar' || kyc.aadhaarVerified}
                            style={{
                                ...buttonStyle,
                                background: kyc.aadhaarVerified ? '#22c55e' : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                            }}
                        >
                            {verifying === 'aadhaar' ? '⏳ Verifying...' : kyc.aadhaarVerified ? '✓ Verified' : 'Verify'}
                        </button>
                    </div>

                    {/* PAN */}
                    <div style={{ display: 'flex', gap: '12px', alignItems: 'flex-end' }}>
                        <div style={{ flex: 1 }}>
                            <label style={labelStyle}>
                                PAN Number
                                {kyc.panVerified && <span style={{ color: '#22c55e', marginLeft: '8px' }}>✓ Verified</span>}
                            </label>
                            <input
                                type="text"
                                value={kyc.panNumber}
                                onChange={(e) => setKyc({ ...kyc, panNumber: e.target.value.toUpperCase().slice(0, 10) })}
                                style={inputStyle}
                                maxLength={10}
                                placeholder="ABCDE1234F"
                                disabled={kyc.panVerified}
                            />
                            {errors.pan && <span style={errorStyle}>{errors.pan}</span>}
                        </div>
                        <button
                            onClick={handleVerifyPAN}
                            disabled={verifying === 'pan' || kyc.panVerified}
                            style={{
                                ...buttonStyle,
                                background: kyc.panVerified ? '#22c55e' : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                            }}
                        >
                            {verifying === 'pan' ? '⏳ Verifying...' : kyc.panVerified ? '✓ Verified' : 'Verify'}
                        </button>
                    </div>

                    {/* Voter ID */}
                    <div>
                        <label style={labelStyle}>Voter ID (Optional)</label>
                        <input
                            type="text"
                            value={kyc.voterId}
                            onChange={(e) => setKyc({ ...kyc, voterId: e.target.value.toUpperCase() })}
                            style={inputStyle}
                            placeholder="Enter Voter ID"
                        />
                    </div>

                    <div style={{
                        padding: '16px',
                        background: kyc.aadhaarVerified && kyc.panVerified ? '#dcfce7' : '#f1f5f9',
                        borderRadius: '12px',
                        textAlign: 'center'
                    }}>
                        {kyc.aadhaarVerified && kyc.panVerified ? (
                            <p style={{ margin: 0, color: '#166534', fontWeight: 600 }}>
                                ✅ KYC Verification Complete - You are eligible for subsidies!
                            </p>
                        ) : (
                            <p style={{ margin: 0, color: '#64748b' }}>
                                Complete Aadhaar and PAN verification to unlock subsidy benefits
                            </p>
                        )}
                    </div>
                </div>
            )}

            {/* Bank Tab */}
            {activeTab === 'bank' && (
                <div className="bank-tab" style={{ display: 'flex', flexDirection: 'column', gap: '20px' }}>
                    <div style={{
                        padding: '16px',
                        background: '#f0fdf4',
                        borderRadius: '12px',
                        border: '1px solid #bbf7d0',
                    }}>
                        <p style={{ margin: 0, fontSize: '14px', color: '#166534' }}>
                            🔒 Bank details are required for subsidy disbursement. We use penny drop verification to ensure accuracy.
                        </p>
                    </div>

                    <div>
                        <label style={labelStyle}>Account Holder Name *</label>
                        <input
                            type="text"
                            value={bank.accountHolderName}
                            onChange={(e) => setBank({ ...bank, accountHolderName: e.target.value })}
                            style={inputStyle}
                            placeholder="Name as per bank account"
                        />
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>Account Number *</label>
                            <input
                                type="password"
                                value={bank.accountNumber}
                                onChange={(e) => setBank({ ...bank, accountNumber: e.target.value.replace(/\D/g, '') })}
                                style={inputStyle}
                                placeholder="Enter account number"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>Confirm Account Number *</label>
                            <input
                                type="text"
                                value={bank.confirmAccountNumber}
                                onChange={(e) => setBank({ ...bank, confirmAccountNumber: e.target.value.replace(/\D/g, '') })}
                                style={inputStyle}
                                placeholder="Re-enter account number"
                            />
                            {errors.bank && <span style={errorStyle}>{errors.bank}</span>}
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>IFSC Code *</label>
                            <input
                                type="text"
                                value={bank.ifscCode}
                                onChange={(e) => setBank({ ...bank, ifscCode: e.target.value.toUpperCase().slice(0, 11) })}
                                style={inputStyle}
                                maxLength={11}
                                placeholder="ABCD0123456"
                            />
                            {errors.ifsc && <span style={errorStyle}>{errors.ifsc}</span>}
                        </div>
                        <div>
                            <label style={labelStyle}>Account Type *</label>
                            <select
                                value={bank.accountType}
                                onChange={(e) => setBank({ ...bank, accountType: e.target.value })}
                                style={inputStyle}
                            >
                                <option value="savings">Savings</option>
                                <option value="current">Current</option>
                            </select>
                        </div>
                    </div>

                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px' }}>
                        <div>
                            <label style={labelStyle}>Bank Name</label>
                            <input
                                type="text"
                                value={bank.bankName}
                                onChange={(e) => setBank({ ...bank, bankName: e.target.value })}
                                style={inputStyle}
                                placeholder="Auto-filled from IFSC"
                            />
                        </div>
                        <div>
                            <label style={labelStyle}>Branch Name</label>
                            <input
                                type="text"
                                value={bank.branchName}
                                onChange={(e) => setBank({ ...bank, branchName: e.target.value })}
                                style={inputStyle}
                                placeholder="Branch name"
                            />
                        </div>
                    </div>

                    <div>
                        <label style={labelStyle}>UPI ID (Optional)</label>
                        <input
                            type="text"
                            value={bank.upiId}
                            onChange={(e) => setBank({ ...bank, upiId: e.target.value })}
                            style={inputStyle}
                            placeholder="yourname@upi"
                        />
                    </div>

                    <button
                        onClick={handleVerifyBank}
                        disabled={verifying === 'bank' || bank.verified}
                        style={{
                            ...buttonStyle,
                            width: '100%',
                            padding: '16px',
                            fontSize: '16px',
                            background: bank.verified ? '#22c55e' : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                        }}
                    >
                        {verifying === 'bank' ? '⏳ Verifying via Penny Drop...' : bank.verified ? '✓ Bank Account Verified' : '🔐 Verify Bank Account'}
                    </button>
                </div>
            )}

            {/* Action Buttons */}
            <div style={{
                display: 'flex',
                gap: '12px',
                marginTop: '24px',
                paddingTop: '24px',
                borderTop: '1px solid #e2e8f0'
            }}>
                {onCancel && (
                    <button
                        onClick={onCancel}
                        style={{
                            flex: 1,
                            padding: '14px',
                            background: 'white',
                            border: '1px solid #e2e8f0',
                            borderRadius: '10px',
                            cursor: 'pointer',
                            fontWeight: 600,
                            color: '#64748b',
                        }}
                    >
                        Cancel
                    </button>
                )}
                <button
                    onClick={handleSubmit}
                    style={{
                        flex: 2,
                        padding: '14px',
                        background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                        border: 'none',
                        borderRadius: '10px',
                        cursor: 'pointer',
                        fontWeight: 600,
                        color: 'white',
                        fontSize: '16px',
                    }}
                >
                    💾 Save Profile
                </button>
            </div>
        </div>
    );
};

// Styles
const labelStyle: React.CSSProperties = {
    display: 'block',
    marginBottom: '6px',
    fontSize: '14px',
    fontWeight: 500,
    color: '#374151',
};

const inputStyle: React.CSSProperties = {
    width: '100%',
    padding: '12px 14px',
    fontSize: '15px',
    border: '1px solid #e2e8f0',
    borderRadius: '10px',
    outline: 'none',
    transition: 'border-color 0.2s ease',
    boxSizing: 'border-box',
};

const buttonStyle: React.CSSProperties = {
    padding: '12px 20px',
    border: 'none',
    borderRadius: '10px',
    cursor: 'pointer',
    fontWeight: 600,
    color: 'white',
    whiteSpace: 'nowrap',
};

const errorStyle: React.CSSProperties = {
    fontSize: '12px',
    color: '#ef4444',
    marginTop: '4px',
    display: 'block',
};

export default UserProfileForm;
