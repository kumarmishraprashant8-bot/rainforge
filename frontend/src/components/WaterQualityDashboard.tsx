/**
 * Water Quality Dashboard Component
 * Display water quality readings, trends, and treatment recommendations
 */

import React, { useState, useEffect } from 'react';

interface QualityReading {
    reading_id: string;
    timestamp: string;
    ph: number | null;
    tds_ppm: number | null;
    turbidity_ntu: number | null;
    temperature_c: number | null;
    quality_grade: string;
    potable: boolean;
    suitable_uses: string[];
}

interface LabTest {
    test_id: string;
    test_date: string;
    lab_name: string;
    suitable_for_drinking: boolean;
    quality_grade: string;
    treatment_required: string[];
}

interface WaterQualityDashboardProps {
    projectId: number;
}

export const WaterQualityDashboard: React.FC<WaterQualityDashboardProps> = ({
    projectId,
}) => {
    const [activeView, setActiveView] = useState<'current' | 'history' | 'lab'>('current');
    const [latestReading, setLatestReading] = useState<QualityReading | null>(null);
    const [readingHistory, setReadingHistory] = useState<QualityReading[]>([]);
    const [labTests, setLabTests] = useState<LabTest[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [projectId]);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Demo data
            setLatestReading({
                reading_id: 'QR001',
                timestamp: new Date().toISOString(),
                ph: 7.2,
                tds_ppm: 185,
                turbidity_ntu: 1.8,
                temperature_c: 24.5,
                quality_grade: 'A',
                potable: true,
                suitable_uses: ['Drinking (with basic treatment)', 'Cooking', 'Bathing', 'Washing', 'Gardening'],
            });

            setReadingHistory([
                { reading_id: 'QR001', timestamp: new Date().toISOString(), ph: 7.2, tds_ppm: 185, turbidity_ntu: 1.8, temperature_c: 24.5, quality_grade: 'A', potable: true, suitable_uses: [] },
                { reading_id: 'QR002', timestamp: new Date(Date.now() - 3600000).toISOString(), ph: 7.1, tds_ppm: 192, turbidity_ntu: 2.1, temperature_c: 24.2, quality_grade: 'A', potable: true, suitable_uses: [] },
                { reading_id: 'QR003', timestamp: new Date(Date.now() - 7200000).toISOString(), ph: 7.3, tds_ppm: 178, turbidity_ntu: 1.5, temperature_c: 24.8, quality_grade: 'A', potable: true, suitable_uses: [] },
                { reading_id: 'QR004', timestamp: new Date(Date.now() - 10800000).toISOString(), ph: 6.9, tds_ppm: 205, turbidity_ntu: 2.8, temperature_c: 25.1, quality_grade: 'B', potable: false, suitable_uses: [] },
                { reading_id: 'QR005', timestamp: new Date(Date.now() - 14400000).toISOString(), ph: 7.0, tds_ppm: 198, turbidity_ntu: 2.2, temperature_c: 24.6, quality_grade: 'A', potable: true, suitable_uses: [] },
            ]);

            setLabTests([
                {
                    test_id: 'LAB001',
                    test_date: new Date(Date.now() - 86400000 * 30).toISOString(),
                    lab_name: 'State Water Testing Lab',
                    suitable_for_drinking: true,
                    quality_grade: 'A',
                    treatment_required: [],
                },
                {
                    test_id: 'LAB002',
                    test_date: new Date(Date.now() - 86400000 * 120).toISOString(),
                    lab_name: 'Jal Jeevan Lab Services',
                    suitable_for_drinking: true,
                    quality_grade: 'A',
                    treatment_required: ['Light chlorination recommended'],
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const getGradeColor = (grade: string) => {
        switch (grade) {
            case 'A': return '#22c55e';
            case 'B': return '#f59e0b';
            case 'C': return '#ef4444';
            default: return '#64748b';
        }
    };

    const getParameterStatus = (param: string, value: number | null) => {
        if (value === null) return { status: 'unknown', color: '#64748b' };

        const standards: Record<string, { min: number; max: number }> = {
            ph: { min: 6.5, max: 8.5 },
            tds: { min: 0, max: 500 },
            turbidity: { min: 0, max: 5 },
        };

        const standard = standards[param];
        if (!standard) return { status: 'unknown', color: '#64748b' };

        if (value >= standard.min && value <= standard.max) {
            return { status: 'Good', color: '#22c55e' };
        } else if (value < standard.min * 0.9 || value > standard.max * 1.1) {
            return { status: 'Poor', color: '#ef4444' };
        }
        return { status: 'Fair', color: '#f59e0b' };
    };

    const formatTime = (timestamp: string) => {
        const date = new Date(timestamp);
        return date.toLocaleString('en-IN', {
            hour: '2-digit',
            minute: '2-digit',
            hour12: true,
        });
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '48px' }}>
                <div style={{ fontSize: '36px', marginBottom: '16px' }}>🔬</div>
                <p>Loading water quality data...</p>
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
                💧 Water Quality Monitor
            </h2>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
                Real-time water quality monitoring for your harvested rainwater
            </p>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'current', label: 'Current Status', icon: '📊' },
                    { id: 'history', label: 'History', icon: '📈' },
                    { id: 'lab', label: 'Lab Tests', icon: '🔬' },
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

            {/* Current Status View */}
            {activeView === 'current' && latestReading && (
                <div>
                    {/* Overall Grade */}
                    <div style={{
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(147,51,234,0.05))',
                        borderRadius: '16px',
                        padding: '32px',
                        textAlign: 'center',
                        marginBottom: '24px',
                        border: '1px solid rgba(59,130,246,0.2)',
                    }}>
                        <div style={{
                            width: '120px',
                            height: '120px',
                            borderRadius: '50%',
                            background: `linear-gradient(135deg, ${getGradeColor(latestReading.quality_grade)}20, ${getGradeColor(latestReading.quality_grade)}40)`,
                            border: `4px solid ${getGradeColor(latestReading.quality_grade)}`,
                            display: 'flex',
                            alignItems: 'center',
                            justifyContent: 'center',
                            margin: '0 auto 16px',
                        }}>
                            <span style={{
                                fontSize: '48px',
                                fontWeight: 700,
                                color: getGradeColor(latestReading.quality_grade)
                            }}>
                                {latestReading.quality_grade}
                            </span>
                        </div>
                        <h3 style={{ marginBottom: '8px', fontSize: '20px' }}>
                            {latestReading.quality_grade === 'A' ? 'Excellent Quality' :
                                latestReading.quality_grade === 'B' ? 'Acceptable Quality' : 'Poor Quality'}
                        </h3>
                        <p style={{ color: '#64748b', marginBottom: '16px' }}>
                            Last updated: {new Date(latestReading.timestamp).toLocaleString()}
                        </p>
                        <div style={{
                            display: 'inline-flex',
                            alignItems: 'center',
                            gap: '8px',
                            padding: '8px 16px',
                            background: latestReading.potable ? '#dcfce7' : '#fef2f2',
                            color: latestReading.potable ? '#166534' : '#991b1b',
                            borderRadius: '20px',
                            fontWeight: 600,
                        }}>
                            {latestReading.potable ? '✓ Safe for Drinking' : '✗ Not Potable'}
                        </div>
                    </div>

                    {/* Parameter Cards */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(4, 1fr)',
                        gap: '16px',
                        marginBottom: '24px',
                    }}>
                        {[
                            { label: 'pH', value: latestReading.ph, unit: '', icon: '⚗️', key: 'ph', range: '6.5-8.5' },
                            { label: 'TDS', value: latestReading.tds_ppm, unit: 'ppm', icon: '🧪', key: 'tds', range: '<500' },
                            { label: 'Turbidity', value: latestReading.turbidity_ntu, unit: 'NTU', icon: '💎', key: 'turbidity', range: '<5' },
                            { label: 'Temp', value: latestReading.temperature_c, unit: '°C', icon: '🌡️', key: 'temp', range: '20-30' },
                        ].map(param => {
                            const status = getParameterStatus(param.key, param.value);
                            return (
                                <div
                                    key={param.key}
                                    style={{
                                        background: 'white',
                                        borderRadius: '16px',
                                        padding: '20px',
                                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                        border: `2px solid ${status.color}20`,
                                        textAlign: 'center',
                                    }}
                                >
                                    <div style={{ fontSize: '28px', marginBottom: '8px' }}>{param.icon}</div>
                                    <div style={{ fontSize: '12px', color: '#64748b', marginBottom: '4px' }}>{param.label}</div>
                                    <div style={{
                                        fontSize: '28px',
                                        fontWeight: 700,
                                        color: status.color,
                                    }}>
                                        {param.value !== null ? param.value.toFixed(1) : '--'}
                                        <span style={{ fontSize: '16px', fontWeight: 400 }}>{param.unit}</span>
                                    </div>
                                    <div style={{
                                        fontSize: '11px',
                                        color: status.color,
                                        fontWeight: 600,
                                        marginTop: '4px',
                                    }}>
                                        {status.status}
                                    </div>
                                    <div style={{ fontSize: '10px', color: '#94a3b8', marginTop: '4px' }}>
                                        Std: {param.range}
                                    </div>
                                </div>
                            );
                        })}
                    </div>

                    {/* Suitable Uses */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        border: '1px solid #e2e8f0',
                    }}>
                        <h4 style={{ marginBottom: '16px' }}>✅ Suitable Uses</h4>
                        <div style={{ display: 'flex', flexWrap: 'wrap', gap: '8px' }}>
                            {latestReading.suitable_uses.map((use, i) => (
                                <span
                                    key={i}
                                    style={{
                                        padding: '8px 16px',
                                        background: '#f0fdf4',
                                        color: '#166534',
                                        borderRadius: '20px',
                                        fontSize: '14px',
                                        border: '1px solid #bbf7d0',
                                    }}
                                >
                                    {use}
                                </span>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* History View */}
            {activeView === 'history' && (
                <div>
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        border: '1px solid #e2e8f0',
                    }}>
                        <h4 style={{ marginBottom: '16px' }}>Recent Readings</h4>
                        <div style={{ overflowX: 'auto' }}>
                            <table style={{ width: '100%', borderCollapse: 'collapse' }}>
                                <thead>
                                    <tr style={{ borderBottom: '2px solid #e2e8f0' }}>
                                        <th style={thStyle}>Time</th>
                                        <th style={thStyle}>pH</th>
                                        <th style={thStyle}>TDS (ppm)</th>
                                        <th style={thStyle}>Turbidity (NTU)</th>
                                        <th style={thStyle}>Temp (°C)</th>
                                        <th style={thStyle}>Grade</th>
                                        <th style={thStyle}>Potable</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {readingHistory.map(reading => (
                                        <tr key={reading.reading_id} style={{ borderBottom: '1px solid #f1f5f9' }}>
                                            <td style={tdStyle}>{formatTime(reading.timestamp)}</td>
                                            <td style={tdStyle}>
                                                <span style={{ color: getParameterStatus('ph', reading.ph).color }}>
                                                    {reading.ph?.toFixed(1) || '--'}
                                                </span>
                                            </td>
                                            <td style={tdStyle}>
                                                <span style={{ color: getParameterStatus('tds', reading.tds_ppm).color }}>
                                                    {reading.tds_ppm || '--'}
                                                </span>
                                            </td>
                                            <td style={tdStyle}>
                                                <span style={{ color: getParameterStatus('turbidity', reading.turbidity_ntu).color }}>
                                                    {reading.turbidity_ntu?.toFixed(1) || '--'}
                                                </span>
                                            </td>
                                            <td style={tdStyle}>{reading.temperature_c?.toFixed(1) || '--'}</td>
                                            <td style={tdStyle}>
                                                <span style={{
                                                    display: 'inline-block',
                                                    padding: '2px 8px',
                                                    background: `${getGradeColor(reading.quality_grade)}20`,
                                                    color: getGradeColor(reading.quality_grade),
                                                    borderRadius: '12px',
                                                    fontWeight: 600,
                                                }}>
                                                    {reading.quality_grade}
                                                </span>
                                            </td>
                                            <td style={tdStyle}>
                                                {reading.potable ? '✅' : '❌'}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </div>
            )}

            {/* Lab Tests View */}
            {activeView === 'lab' && (
                <div>
                    <div style={{
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(147,51,234,0.05))',
                        borderRadius: '12px',
                        padding: '16px',
                        marginBottom: '24px',
                        border: '1px solid rgba(59,130,246,0.2)',
                    }}>
                        <p style={{ margin: 0, fontSize: '14px' }}>
                            💡 <strong>Tip:</strong> Get a lab test done every 6 months for a comprehensive water quality analysis
                        </p>
                    </div>

                    {labTests.length === 0 ? (
                        <div style={{
                            textAlign: 'center',
                            padding: '48px',
                            background: '#f8fafc',
                            borderRadius: '12px',
                        }}>
                            <div style={{ fontSize: '48px', marginBottom: '16px' }}>🔬</div>
                            <h3 style={{ marginBottom: '8px' }}>No Lab Tests Yet</h3>
                            <p style={{ color: '#64748b', marginBottom: '16px' }}>
                                Upload your first lab test report for comprehensive analysis
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
                                📤 Upload Lab Report
                            </button>
                        </div>
                    ) : (
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '16px' }}>
                            {labTests.map(test => (
                                <div
                                    key={test.test_id}
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
                                            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                                                {test.lab_name}
                                            </h4>
                                            <p style={{ margin: '4px 0 0', color: '#64748b', fontSize: '14px' }}>
                                                Test Date: {new Date(test.test_date).toLocaleDateString()}
                                            </p>
                                        </div>
                                        <div style={{ textAlign: 'right' }}>
                                            <div style={{
                                                display: 'inline-block',
                                                padding: '4px 12px',
                                                background: `${getGradeColor(test.quality_grade)}20`,
                                                color: getGradeColor(test.quality_grade),
                                                borderRadius: '12px',
                                                fontWeight: 600,
                                                marginBottom: '4px',
                                            }}>
                                                Grade {test.quality_grade}
                                            </div>
                                            <div style={{
                                                fontSize: '12px',
                                                color: test.suitable_for_drinking ? '#166534' : '#991b1b',
                                            }}>
                                                {test.suitable_for_drinking ? '✓ Safe for Drinking' : '✗ Not Potable'}
                                            </div>
                                        </div>
                                    </div>

                                    {test.treatment_required.length > 0 && (
                                        <div style={{ marginTop: '12px', padding: '12px', background: '#fffbeb', borderRadius: '8px' }}>
                                            <div style={{ fontSize: '13px', fontWeight: 600, color: '#b45309', marginBottom: '4px' }}>
                                                ⚠️ Treatment Recommendations:
                                            </div>
                                            <ul style={{ margin: 0, paddingLeft: '20px', fontSize: '13px', color: '#b45309' }}>
                                                {test.treatment_required.map((t, i) => (
                                                    <li key={i}>{t}</li>
                                                ))}
                                            </ul>
                                        </div>
                                    )}
                                </div>
                            ))}

                            <button style={{
                                padding: '14px',
                                background: 'white',
                                border: '2px dashed #e2e8f0',
                                borderRadius: '12px',
                                color: '#64748b',
                                fontWeight: 600,
                                cursor: 'pointer',
                            }}>
                                + Upload New Lab Report
                            </button>
                        </div>
                    )}
                </div>
            )}
        </div>
    );
};

const thStyle: React.CSSProperties = {
    padding: '12px 16px',
    textAlign: 'left',
    fontSize: '12px',
    fontWeight: 600,
    color: '#64748b',
    textTransform: 'uppercase',
};

const tdStyle: React.CSSProperties = {
    padding: '12px 16px',
    fontSize: '14px',
};

export default WaterQualityDashboard;
