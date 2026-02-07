/**
 * Contractor Marketplace Component
 * Find contractors, get quotes, manage work orders
 */

import React, { useState, useEffect } from 'react';

interface Contractor {
    id: string;
    company_name: string;
    owner_name: string;
    phone: string;
    city: string;
    state: string;
    years_experience: number;
    projects_completed: number;
    average_rating: number;
    total_reviews: number;
    verified: boolean;
    certifications: string[];
    service_areas: string[];
}

interface Quote {
    quote_id: string;
    contractor_id: string;
    contractor_name: string;
    material_cost: number;
    labor_cost: number;
    total_cost: number;
    estimated_days: number;
    warranty_months: number;
    status: string;
    created_at: string;
}

interface ContractorMarketplaceProps {
    projectId: number;
    city: string;
    state: string;
    roofAreaSqm: number;
    tankCapacityLiters: number;
    onQuoteAccepted?: (workOrderId: string) => void;
}

export const ContractorMarketplace: React.FC<ContractorMarketplaceProps> = ({
    projectId,
    city,
    state,
    roofAreaSqm,
    tankCapacityLiters,
    onQuoteAccepted,
}) => {
    const [activeView, setActiveView] = useState<'search' | 'quotes' | 'orders'>('search');
    const [contractors, setContractors] = useState<Contractor[]>([]);
    const [quotes, setQuotes] = useState<Quote[]>([]);
    const [loading, setLoading] = useState(false);
    const [selectedContractor, setSelectedContractor] = useState<Contractor | null>(null);
    const [quoteRequestSent, setQuoteRequestSent] = useState(false);

    // Form state for quote request
    const [quoteForm, setQuoteForm] = useState({
        requirements: '',
        includesRecharge: false,
        preferredStartDate: '',
        budgetMin: '',
        budgetMax: '',
        contactName: '',
        contactPhone: '',
    });

    useEffect(() => {
        fetchContractors();
    }, [city, state]);

    const fetchContractors = async () => {
        setLoading(true);
        try {
            // Demo data for now
            const demoContractors: Contractor[] = [
                {
                    id: 'CTR001',
                    company_name: 'AquaHarvest Solutions',
                    owner_name: 'Rajesh Kumar',
                    phone: '+919876543210',
                    city: 'Bangalore',
                    state: 'Karnataka',
                    years_experience: 8,
                    projects_completed: 150,
                    average_rating: 4.7,
                    total_reviews: 89,
                    verified: true,
                    certifications: ['ISO 9001', 'Government Empanelled'],
                    service_areas: ['Bangalore', 'Mysore', 'Mangalore'],
                },
                {
                    id: 'CTR002',
                    company_name: 'JalSanchay Enterprises',
                    owner_name: 'Suresh Patel',
                    phone: '+919888777666',
                    city: 'Ahmedabad',
                    state: 'Gujarat',
                    years_experience: 12,
                    projects_completed: 280,
                    average_rating: 4.8,
                    total_reviews: 156,
                    verified: true,
                    certifications: ['GRIHA Certified', 'IGBC Approved'],
                    service_areas: ['Ahmedabad', 'Surat', 'Vadodara', 'Rajkot'],
                },
                {
                    id: 'CTR003',
                    company_name: 'RainCatch India',
                    owner_name: 'Priya Sharma',
                    phone: '+919777888999',
                    city: 'Chennai',
                    state: 'Tamil Nadu',
                    years_experience: 6,
                    projects_completed: 95,
                    average_rating: 4.5,
                    total_reviews: 52,
                    verified: true,
                    certifications: ['TNPCB Registered'],
                    service_areas: ['Chennai', 'Coimbatore', 'Madurai'],
                },
            ];
            setContractors(demoContractors);
        } finally {
            setLoading(false);
        }
    };

    const handleRequestQuotes = async () => {
        setLoading(true);
        try {
            // In production, this would call the API
            await new Promise(resolve => setTimeout(resolve, 1500));
            setQuoteRequestSent(true);
            setActiveView('quotes');

            // Simulate receiving quotes
            setTimeout(() => {
                setQuotes([
                    {
                        quote_id: 'Q001',
                        contractor_id: 'CTR001',
                        contractor_name: 'AquaHarvest Solutions',
                        material_cost: 35000,
                        labor_cost: 15000,
                        total_cost: 50000,
                        estimated_days: 7,
                        warranty_months: 24,
                        status: 'submitted',
                        created_at: new Date().toISOString(),
                    },
                    {
                        quote_id: 'Q002',
                        contractor_id: 'CTR002',
                        contractor_name: 'JalSanchay Enterprises',
                        material_cost: 38000,
                        labor_cost: 12000,
                        total_cost: 50000,
                        estimated_days: 5,
                        warranty_months: 36,
                        status: 'submitted',
                        created_at: new Date().toISOString(),
                    },
                ]);
            }, 3000);
        } finally {
            setLoading(false);
        }
    };

    const handleAcceptQuote = async (quoteId: string) => {
        setLoading(true);
        try {
            await new Promise(resolve => setTimeout(resolve, 1000));
            onQuoteAccepted?.(`WO-${projectId}-${Date.now()}`);
            setActiveView('orders');
        } finally {
            setLoading(false);
        }
    };

    const renderStars = (rating: number) => {
        return '⭐'.repeat(Math.floor(rating)) + (rating % 1 >= 0.5 ? '½' : '');
    };

    return (
        <div style={{
            maxWidth: '1000px',
            margin: '0 auto',
            padding: '24px',
        }}>
            <h2 style={{
                fontSize: '24px',
                fontWeight: 700,
                marginBottom: '8px',
                color: '#1a1a2e',
            }}>
                🔧 Contractor Marketplace
            </h2>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
                Find verified contractors for your {tankCapacityLiters.toLocaleString()}L RWH system
            </p>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'search', label: 'Find Contractors', icon: '🔍' },
                    { id: 'quotes', label: `Quotes ${quotes.length ? `(${quotes.length})` : ''}`, icon: '📋' },
                    { id: 'orders', label: 'Work Orders', icon: '📦' },
                ].map((tab) => (
                    <button
                        key={tab.id}
                        onClick={() => setActiveView(tab.id as any)}
                        style={{
                            flex: 1,
                            padding: '12px 16px',
                            background: activeView === tab.id
                                ? 'linear-gradient(135deg, #3b82f6, #2563eb)'
                                : 'white',
                            color: activeView === tab.id ? 'white' : '#64748b',
                            border: activeView === tab.id ? 'none' : '1px solid #e2e8f0',
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

            {/* Search View */}
            {activeView === 'search' && (
                <div>
                    {/* Quote Request Form */}
                    {!quoteRequestSent ? (
                        <div style={{
                            background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(147,51,234,0.05))',
                            borderRadius: '16px',
                            padding: '24px',
                            marginBottom: '24px',
                            border: '1px solid rgba(59,130,246,0.2)',
                        }}>
                            <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>📝 Request Quotes</h3>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                <div>
                                    <label style={labelStyle}>Your Name *</label>
                                    <input
                                        type="text"
                                        value={quoteForm.contactName}
                                        onChange={(e) => setQuoteForm({ ...quoteForm, contactName: e.target.value })}
                                        style={inputStyle}
                                        placeholder="Full name"
                                    />
                                </div>
                                <div>
                                    <label style={labelStyle}>Phone Number *</label>
                                    <input
                                        type="tel"
                                        value={quoteForm.contactPhone}
                                        onChange={(e) => setQuoteForm({ ...quoteForm, contactPhone: e.target.value })}
                                        style={inputStyle}
                                        placeholder="+91 9XXXXXXXXX"
                                    />
                                </div>
                            </div>

                            <div style={{ marginBottom: '16px' }}>
                                <label style={labelStyle}>Requirements</label>
                                <textarea
                                    value={quoteForm.requirements}
                                    onChange={(e) => setQuoteForm({ ...quoteForm, requirements: e.target.value })}
                                    style={{ ...inputStyle, minHeight: '80px', resize: 'vertical' }}
                                    placeholder="Any specific requirements or preferences..."
                                />
                            </div>

                            <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr 1fr', gap: '16px', marginBottom: '16px' }}>
                                <div>
                                    <label style={labelStyle}>Preferred Start Date</label>
                                    <input
                                        type="date"
                                        value={quoteForm.preferredStartDate}
                                        onChange={(e) => setQuoteForm({ ...quoteForm, preferredStartDate: e.target.value })}
                                        style={inputStyle}
                                    />
                                </div>
                                <div>
                                    <label style={labelStyle}>Budget Min (₹)</label>
                                    <input
                                        type="number"
                                        value={quoteForm.budgetMin}
                                        onChange={(e) => setQuoteForm({ ...quoteForm, budgetMin: e.target.value })}
                                        style={inputStyle}
                                        placeholder="Min budget"
                                    />
                                </div>
                                <div>
                                    <label style={labelStyle}>Budget Max (₹)</label>
                                    <input
                                        type="number"
                                        value={quoteForm.budgetMax}
                                        onChange={(e) => setQuoteForm({ ...quoteForm, budgetMax: e.target.value })}
                                        style={inputStyle}
                                        placeholder="Max budget"
                                    />
                                </div>
                            </div>

                            <label style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '16px' }}>
                                <input
                                    type="checkbox"
                                    checked={quoteForm.includesRecharge}
                                    onChange={(e) => setQuoteForm({ ...quoteForm, includesRecharge: e.target.checked })}
                                    style={{ width: '18px', height: '18px' }}
                                />
                                <span>Include groundwater recharge pit</span>
                            </label>

                            <button
                                onClick={handleRequestQuotes}
                                disabled={loading || !quoteForm.contactName || !quoteForm.contactPhone}
                                style={{
                                    width: '100%',
                                    padding: '14px',
                                    background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                                    border: 'none',
                                    borderRadius: '10px',
                                    color: 'white',
                                    fontWeight: 600,
                                    fontSize: '16px',
                                    cursor: 'pointer',
                                }}
                            >
                                {loading ? '⏳ Sending Request...' : '📤 Send Quote Request to All Contractors'}
                            </button>
                        </div>
                    ) : (
                        <div style={{
                            background: '#dcfce7',
                            borderRadius: '12px',
                            padding: '16px',
                            marginBottom: '24px',
                            textAlign: 'center',
                        }}>
                            <p style={{ margin: 0, color: '#166534', fontWeight: 600 }}>
                                ✅ Quote request sent! Contractors will respond within 24-48 hours.
                            </p>
                        </div>
                    )}

                    {/* Contractor List */}
                    <h3 style={{ marginBottom: '16px', fontWeight: 600 }}>🏗️ Verified Contractors in {city}</h3>

                    <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                        {contractors.map(contractor => (
                            <div
                                key={contractor.id}
                                style={{
                                    background: 'white',
                                    borderRadius: '12px',
                                    padding: '20px',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                    border: '1px solid #e2e8f0',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                            <h4 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
                                                {contractor.company_name}
                                            </h4>
                                            {contractor.verified && (
                                                <span style={{
                                                    background: '#dcfce7',
                                                    color: '#166534',
                                                    padding: '2px 8px',
                                                    borderRadius: '12px',
                                                    fontSize: '12px',
                                                    fontWeight: 600,
                                                }}>
                                                    ✓ Verified
                                                </span>
                                            )}
                                        </div>
                                        <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>
                                            👤 {contractor.owner_name} • 📍 {contractor.city}, {contractor.state}
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontSize: '18px', fontWeight: 700, color: '#f59e0b' }}>
                                            {renderStars(contractor.average_rating)} {contractor.average_rating}
                                        </div>
                                        <div style={{ fontSize: '12px', color: '#64748b' }}>
                                            {contractor.total_reviews} reviews
                                        </div>
                                    </div>
                                </div>

                                <div style={{
                                    display: 'grid',
                                    gridTemplateColumns: 'repeat(4, 1fr)',
                                    gap: '16px',
                                    marginTop: '16px',
                                    padding: '12px',
                                    background: '#f8fafc',
                                    borderRadius: '8px',
                                }}>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#64748b' }}>Experience</div>
                                        <div style={{ fontWeight: 600 }}>{contractor.years_experience} years</div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#64748b' }}>Projects</div>
                                        <div style={{ fontWeight: 600 }}>{contractor.projects_completed}</div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#64748b' }}>Service Areas</div>
                                        <div style={{ fontWeight: 600, fontSize: '13px' }}>
                                            {contractor.service_areas.slice(0, 2).join(', ')}
                                            {contractor.service_areas.length > 2 && ` +${contractor.service_areas.length - 2}`}
                                        </div>
                                    </div>
                                    <div>
                                        <div style={{ fontSize: '12px', color: '#64748b' }}>Certifications</div>
                                        <div style={{ fontWeight: 600, fontSize: '13px' }}>
                                            {contractor.certifications.length} cert.
                                        </div>
                                    </div>
                                </div>

                                <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                                    <button
                                        style={{
                                            flex: 1,
                                            padding: '10px',
                                            background: 'white',
                                            border: '1px solid #3b82f6',
                                            borderRadius: '8px',
                                            color: '#3b82f6',
                                            fontWeight: 600,
                                            cursor: 'pointer',
                                        }}
                                    >
                                        📞 Call
                                    </button>
                                    <button
                                        onClick={() => setSelectedContractor(contractor)}
                                        style={{
                                            flex: 1,
                                            padding: '10px',
                                            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                            border: 'none',
                                            borderRadius: '8px',
                                            color: 'white',
                                            fontWeight: 600,
                                            cursor: 'pointer',
                                        }}
                                    >
                                        View Profile
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            )}

            {/* Quotes View */}
            {activeView === 'quotes' && (
                <div>
                    {quotes.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '48px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <div style={{ fontSize: '48px', marginBottom: '16px' }}>📬</div>
                            <h3 style={{ marginBottom: '8px' }}>Waiting for Quotes</h3>
                            <p style={{ color: '#64748b' }}>
                                Contractors are reviewing your request. You'll receive quotes within 24-48 hours.
                            </p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {quotes.map(quote => (
                                <div
                                    key={quote.quote_id}
                                    style={{
                                        background: 'white',
                                        borderRadius: '12px',
                                        padding: '20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: '1px solid #e2e8f0',
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                        <div>
                                            <h4 style={{ margin: 0, fontSize: '18px', fontWeight: 600 }}>
                                                {quote.contractor_name}
                                            </h4>
                                            <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
                                                Quote #{quote.quote_id} • Received just now
                                            </p>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{
                                                fontSize: '28px',
                                                fontWeight: 700,
                                                color: '#22c55e',
                                            }}>
                                                ₹{quote.total_cost.toLocaleString()}
                                            </div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>
                                                Total Cost
                                            </div>
                                        </div>
                                    </div>

                                    <div style={{
                                        display: 'grid',
                                        gridTemplateColumns: 'repeat(4, 1fr)',
                                        gap: '16px',
                                        marginTop: '16px',
                                        padding: '12px',
                                        background: '#f8fafc',
                                        borderRadius: '8px',
                                    }}>
                                        <div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>Materials</div>
                                            <div style={{ fontWeight: 600 }}>₹{quote.material_cost.toLocaleString()}</div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>Labor</div>
                                            <div style={{ fontWeight: 600 }}>₹{quote.labor_cost.toLocaleString()}</div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>Duration</div>
                                            <div style={{ fontWeight: 600 }}>{quote.estimated_days} days</div>
                                        </div>
                                        <div>
                                            <div style={{ fontSize: '12px', color: '#64748b' }}>Warranty</div>
                                            <div style={{ fontWeight: 600 }}>{quote.warranty_months} months</div>
                                        </div>
                                    </div>

                                    <div style={{ display: 'flex', gap: '12px', marginTop: '16px' }}>
                                        <button
                                            style={{
                                                flex: 1,
                                                padding: '10px',
                                                background: 'white',
                                                border: '1px solid #e2e8f0',
                                                borderRadius: '8px',
                                                color: '#64748b',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                            }}
                                        >
                                            Negotiate
                                        </button>
                                        <button
                                            onClick={() => handleAcceptQuote(quote.quote_id)}
                                            style={{
                                                flex: 2,
                                                padding: '12px',
                                                background: 'linear-gradient(135deg, #22c55e, #16a34a)',
                                                border: 'none',
                                                borderRadius: '8px',
                                                color: 'white',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                                fontSize: '15px',
                                            }}
                                        >
                                            ✓ Accept Quote & Create Work Order
                                        </button>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Work Orders View */}
            {activeView === 'orders' && (
                <div style={{
                    textAlign: 'center',
                    padding: '48px',
                    background: '#f8fafc',
                    borderRadius: '12px',
                }}>
                    <div style={{ fontSize: '48px', marginBottom: '16px' }}>📦</div>
                    <h3 style={{ marginBottom: '8px' }}>No Active Work Orders</h3>
                    <p style={{ color: '#64748b' }}>
                        Accept a quote to create a work order and track installation progress.
                    </p>
                </div>
            )}
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

export default ContractorMarketplace;
