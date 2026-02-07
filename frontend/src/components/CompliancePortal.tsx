/**
 * Compliance Portal Component
 * Government certificates, permits, and regulatory compliance
 */

import React, { useState, useEffect } from 'react';

interface ComplianceRequirement {
    id: string;
    name: string;
    description: string;
    is_mandatory: boolean;
    applies_from_sqm: number;
    penalty_per_month: number | null;
    status: 'compliant' | 'pending' | 'non_compliant';
}

interface Certificate {
    certificate_id: string;
    certificate_type: string;
    certificate_number: string;
    issue_date: string;
    valid_until: string;
    status: string;
    download_url: string;
}

interface PermitApplication {
    application_id: string;
    application_number: string;
    status: string;
    submitted_date: string | null;
    expected_approval_date: string | null;
}

interface CompliancePortalProps {
    projectId: number;
    state: string;
    city: string;
    roofAreaSqm: number;
}

export const CompliancePortal: React.FC<CompliancePortalProps> = ({
    projectId,
    state,
    city,
    roofAreaSqm,
}) => {
    const [activeTab, setActiveTab] = useState<'requirements' | 'certificates' | 'permits'>('requirements');
    const [requirements, setRequirements] = useState<ComplianceRequirement[]>([]);
    const [certificates, setCertificates] = useState<Certificate[]>([]);
    const [permits, setPermits] = useState<PermitApplication[]>([]);
    const [loading, setLoading] = useState(true);
    const [generatingCert, setGeneratingCert] = useState<string | null>(null);

    useEffect(() => {
        fetchData();
    }, [projectId, state, city]);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Demo data
            setRequirements([
                {
                    id: 'REQ001',
                    name: 'Rainwater Harvesting Installation',
                    description: `Mandatory for buildings with roof area > 100 sqm in ${state}`,
                    is_mandatory: true,
                    applies_from_sqm: 100,
                    penalty_per_month: 1000,
                    status: 'compliant',
                },
                {
                    id: 'REQ002',
                    name: 'Groundwater Recharge',
                    description: 'Additional recharge pit required for buildings > 300 sqm',
                    is_mandatory: roofAreaSqm > 300,
                    applies_from_sqm: 300,
                    penalty_per_month: 2000,
                    status: roofAreaSqm > 300 ? 'pending' : 'compliant',
                },
                {
                    id: 'REQ003',
                    name: 'Municipal Water Connection Eligibility',
                    description: 'RWH certificate required for new water connections',
                    is_mandatory: true,
                    applies_from_sqm: 0,
                    penalty_per_month: null,
                    status: 'compliant',
                },
                {
                    id: 'REQ004',
                    name: 'Annual Inspection',
                    description: 'Yearly inspection by PWD for commercial buildings',
                    is_mandatory: false,
                    applies_from_sqm: 500,
                    penalty_per_month: null,
                    status: 'pending',
                },
            ]);

            setCertificates([
                {
                    certificate_id: 'CERT001',
                    certificate_type: 'installation',
                    certificate_number: `RWH/${state.toUpperCase()}/2024/001234`,
                    issue_date: '2024-06-15',
                    valid_until: '2025-06-15',
                    status: 'valid',
                    download_url: '#',
                },
            ]);

            setPermits([
                {
                    application_id: 'APP001',
                    application_number: `PWD/${city.toUpperCase()}/RWH/2024/5678`,
                    status: 'approved',
                    submitted_date: '2024-05-20',
                    expected_approval_date: '2024-06-01',
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const handleGenerateCertificate = async (type: string) => {
        setGeneratingCert(type);
        try {
            await new Promise(resolve => setTimeout(resolve, 2000));
            // In production, this would call the API to generate a certificate
            const newCert: Certificate = {
                certificate_id: `CERT${Date.now()}`,
                certificate_type: type,
                certificate_number: `RWH/${state.toUpperCase()}/${new Date().getFullYear()}/${Math.random().toString(36).substring(7).toUpperCase()}`,
                issue_date: new Date().toISOString().split('T')[0],
                valid_until: new Date(Date.now() + 365 * 24 * 60 * 60 * 1000).toISOString().split('T')[0],
                status: 'valid',
                download_url: '#',
            };
            setCertificates([...certificates, newCert]);
        } finally {
            setGeneratingCert(null);
        }
    };

    const getStatusBadge = (status: string) => {
        const colors: Record<string, { bg: string; text: string }> = {
            compliant: { bg: '#dcfce7', text: '#166534' },
            valid: { bg: '#dcfce7', text: '#166534' },
            approved: { bg: '#dcfce7', text: '#166534' },
            pending: { bg: '#fef3c7', text: '#b45309' },
            processing: { bg: '#dbeafe', text: '#1e40af' },
            non_compliant: { bg: '#fee2e2', text: '#991b1b' },
            expired: { bg: '#fee2e2', text: '#991b1b' },
            rejected: { bg: '#fee2e2', text: '#991b1b' },
        };
        const color = colors[status] || { bg: '#f1f5f9', text: '#64748b' };

        return (
            <span style={{
                padding: '4px 12px',
                background: color.bg,
                color: color.text,
                borderRadius: '12px',
                fontSize: '12px',
                fontWeight: 600,
                textTransform: 'capitalize',
            }}>
                {status.replace(/_/g, ' ')}
            </span>
        );
    };

    const complianceScore = requirements.length > 0
        ? Math.round((requirements.filter(r => r.status === 'compliant').length / requirements.length) * 100)
        : 0;

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '48px' }}>
                <div style={{ fontSize: '36px', marginBottom: '16px' }}>📋</div>
                <p>Loading compliance data...</p>
            </div>
        );
    }

    return (
        <div style={{
            maxWidth: '900px',
            margin: '0 auto',
            padding: '24px',
        }}>
            <h2 style={{
                fontSize: '24px',
                fontWeight: 700,
                marginBottom: '8px',
                color: '#1a1a2e',
            }}>
                📋 Compliance Portal
            </h2>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
                Government requirements and certificates for {city}, {state}
            </p>

            {/* Compliance Score */}
            <div style={{
                background: complianceScore === 100
                    ? 'linear-gradient(135deg, rgba(34,197,94,0.1), rgba(22,163,74,0.1))'
                    : 'linear-gradient(135deg, rgba(251,191,36,0.1), rgba(245,158,11,0.1))',
                borderRadius: '16px',
                padding: '24px',
                marginBottom: '24px',
                border: `1px solid ${complianceScore === 100 ? '#bbf7d0' : '#fde68a'}`,
            }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between' }}>
                    <div>
                        <h3 style={{ margin: 0, fontSize: '18px' }}>Compliance Score</h3>
                        <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
                            {requirements.filter(r => r.status === 'compliant').length} of {requirements.length} requirements met
                        </p>
                    </div>
                    <div style={{
                        width: '80px',
                        height: '80px',
                        borderRadius: '50%',
                        background: `conic-gradient(${complianceScore === 100 ? '#22c55e' : '#f59e0b'} ${complianceScore}%, #e2e8f0 0%)`,
                        display: 'flex',
                        alignItems: 'center',
                        justifyContent: 'center',
                    }}>
                        <div style={{
                            width: '64px',
                            height: '64px',
                            borderRadius: '50%',
                            background: 'white',
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            fontSize: '20px',
                            fontWeight: 700,
                            color: complianceScore === 100 ? '#22c55e' : '#f59e0b',
                        }}>
                            {complianceScore}%
                        </div>
                    </div>
                </div>
                {complianceScore < 100 && (
                    <div style={{
                        marginTop: '16px',
                        padding: '12px',
                        background: 'white',
                        borderRadius: '8px',
                        fontSize: '14px',
                    }}>
                        ⚠️ Complete pending requirements to avoid penalties and unlock municipal services
                    </div>
                )}
            </div>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'requirements', label: 'Requirements', icon: '📜' },
                    { id: 'certificates', label: 'Certificates', icon: '🏆' },
                    { id: 'permits', label: 'Permits', icon: '📝' },
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

            {/* Requirements Tab */}
            {activeTab === 'requirements' && (
                <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                    {requirements.map(req => (
                        <div
                            key={req.id}
                            style={{
                                background: 'white',
                                borderRadius: '12px',
                                padding: '20px',
                                boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                border: `1px solid ${req.status === 'non_compliant' ? '#fecaca' : '#e2e8f0'}`,
                            }}
                        >
                            <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                <div>
                                    <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                        <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                                            {req.name}
                                        </h4>
                                        {req.is_mandatory && (
                                            <span style={{
                                                padding: '2px 8px',
                                                background: '#fef2f2',
                                                color: '#991b1b',
                                                borderRadius: '12px',
                                                fontSize: '11px',
                                                fontWeight: 600,
                                            }}>
                                                MANDATORY
                                            </span>
                                        )}
                                    </div>
                                    <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>
                                        {req.description}
                                    </p>
                                    {req.penalty_per_month && req.status !== 'compliant' && (
                                        <p style={{ margin: '8px 0 0', color: '#ef4444', fontSize: '13px' }}>
                                            ⚠️ Penalty: ₹{req.penalty_per_month.toLocaleString()}/month
                                        </p>
                                    )}
                                </div>
                                <div>
                                    {getStatusBadge(req.status)}
                                </div>
                            </div>

                            {req.status !== 'compliant' && (
                                <div style={{ marginTop: '12px' }}>
                                    <button style={{
                                        padding: '8px 16px',
                                        background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        fontSize: '13px',
                                    }}>
                                        Take Action →
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            )}

            {/* Certificates Tab */}
            {activeTab === 'certificates' && (
                <div>
                    {/* Generate Certificate Cards */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(3, 1fr)',
                        gap: '16px',
                        marginBottom: '24px',
                    }}>
                        {[
                            { type: 'installation', name: 'Installation Certificate', icon: '📄', desc: 'Proof of RWH installation' },
                            { type: 'compliance', name: 'Compliance Certificate', icon: '✅', desc: 'State PWD compliance' },
                            { type: 'water_credit', name: 'Water Credit Certificate', icon: '💧', desc: 'Tradeable water credits' },
                        ].map(cert => (
                            <div
                                key={cert.type}
                                style={{
                                    background: 'white',
                                    borderRadius: '12px',
                                    padding: '20px',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                    border: '1px solid #e2e8f0',
                                    textAlign: 'center',
                                }}
                            >
                                <div style={{ fontSize: '36px', marginBottom: '8px' }}>{cert.icon}</div>
                                <h4 style={{ margin: '0 0 4px', fontSize: '14px' }}>{cert.name}</h4>
                                <p style={{ margin: '0 0 12px', fontSize: '12px', color: '#64748b' }}>{cert.desc}</p>
                                <button
                                    onClick={() => handleGenerateCertificate(cert.type)}
                                    disabled={generatingCert === cert.type}
                                    style={{
                                        width: '100%',
                                        padding: '8px',
                                        background: generatingCert === cert.type
                                            ? '#e2e8f0'
                                            : 'linear-gradient(135deg, #3b82f6, #2563eb)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: generatingCert === cert.type ? '#64748b' : 'white',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        fontSize: '12px',
                                    }}
                                >
                                    {generatingCert === cert.type ? '⏳ Generating...' : 'Generate'}
                                </button>
                            </div>
                        ))}
                    </div>

                    {/* Existing Certificates */}
                    <h4 style={{ marginBottom: '12px' }}>Your Certificates</h4>
                    {certificates.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '32px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <p style={{ color: '#64748b' }}>No certificates generated yet</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {certificates.map(cert => (
                                <div
                                    key={cert.certificate_id}
                                    style={{
                                        background: 'white',
                                        borderRadius: '12px',
                                        padding: '20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: '1px solid #e2e8f0',
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600, textTransform: 'capitalize' }}>
                                                {cert.certificate_type.replace(/_/g, ' ')} Certificate
                                            </h4>
                                            <p style={{ margin: '4px 0', color: '#64748b', fontSize: '13px' }}>
                                                #{cert.certificate_number}
                                            </p>
                                            <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                                                Valid: {new Date(cert.issue_date).toLocaleDateString()} - {new Date(cert.valid_until).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            {getStatusBadge(cert.status)}
                                            <button style={{
                                                padding: '8px 16px',
                                                background: 'linear-gradient(135deg, #10b981, #059669)',
                                                border: 'none',
                                                borderRadius: '8px',
                                                color: 'white',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                                fontSize: '13px',
                                            }}>
                                                ⬇️ Download
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}

            {/* Permits Tab */}
            {activeTab === 'permits' && (
                <div>
                    <div style={{
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(147,51,234,0.05))',
                        borderRadius: '12px',
                        padding: '20px',
                        marginBottom: '24px',
                        border: '1px solid rgba(59,130,246,0.2)',
                    }}>
                        <h4 style={{ margin: '0 0 8px' }}>📝 Apply for Building Permit</h4>
                        <p style={{ margin: '0 0 16px', color: '#64748b', fontSize: '14px' }}>
                            Pre-filled application form for RWH installation permit from PWD/Municipal Corporation
                        </p>
                        <button style={{
                            padding: '12px 24px',
                            background: 'linear-gradient(135deg, #3b82f6, #2563eb)',
                            border: 'none',
                            borderRadius: '10px',
                            color: 'white',
                            fontWeight: 600,
                            cursor: 'pointer',
                        }}>
                            Start New Application
                        </button>
                    </div>

                    {/* Existing Applications */}
                    <h4 style={{ marginBottom: '12px' }}>Your Applications</h4>
                    {permits.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '32px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <p style={{ color: '#64748b' }}>No permit applications yet</p>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {permits.map(permit => (
                                <div
                                    key={permit.application_id}
                                    style={{
                                        background: 'white',
                                        borderRadius: '12px',
                                        padding: '20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: '1px solid #e2e8f0',
                                    }}
                                >
                                    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                                        <div>
                                            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                                                RWH Installation Permit
                                            </h4>
                                            <p style={{ margin: '4px 0', color: '#64748b', fontSize: '13px' }}>
                                                Application #{permit.application_number}
                                            </p>
                                            {permit.submitted_date && (
                                                <p style={{ margin: 0, fontSize: '12px', color: '#94a3b8' }}>
                                                    Submitted: {new Date(permit.submitted_date).toLocaleDateString()}
                                                </p>
                                            )}
                                        </div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '12px' }}>
                                            {getStatusBadge(permit.status)}
                                            <button style={{
                                                padding: '8px 16px',
                                                background: 'white',
                                                border: '1px solid #e2e8f0',
                                                borderRadius: '8px',
                                                color: '#64748b',
                                                fontWeight: 600,
                                                cursor: 'pointer',
                                                fontSize: '13px',
                                            }}>
                                                View Details
                                            </button>
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

export default CompliancePortal;
