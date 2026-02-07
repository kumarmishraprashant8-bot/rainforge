/**
 * 🔥 WOW MOMENT #1: FraudInspector Component
 * 
 * Visual fraud detection panel that shows:
 * - Photo with overlays/indicators
 * - Red/yellow/green risk badges
 * - GPS distance mini-map
 * - pHash duplicate matches
 * - Big bold FRAUD DETECTED banner
 */

import React, { useState, useEffect } from 'react';
import './FraudInspector.css';

interface FraudInspectData {
    verification_id: number;
    project_id: number;
    risk_score: number;
    flags: string[];
    flags_detailed: string[];
    exif: {
        lat: number | null;
        lng: number | null;
        timestamp: string | null;
        software: string | null;
        camera: string | null;
        has_gps: boolean;
        has_exif: boolean;
    };
    phash: string;
    phash_matches: Array<{
        verification_id: string;
        distance: number;
    }>;
    gps_distance_m: number | null;
    expected_location: {
        lat: number | null;
        lng: number | null;
    };
    recommendation: string;
    status: string;
    submitted_at: string;
    fraud_detected: boolean;
    payment_blocked: boolean;
}

interface FraudInspectorProps {
    verificationId?: number;
    onApprove?: (id: number) => void;
    onReject?: (id: number) => void;
    onRequestEvidence?: (id: number) => void;
}

const FraudInspector: React.FC<FraudInspectorProps> = ({
    verificationId,
    onApprove,
    onReject,
    onRequestEvidence
}) => {
    const [data, setData] = useState<FraudInspectData | null>(null);
    const [loading, setLoading] = useState(false);
    const [error, setError] = useState<string | null>(null);

    useEffect(() => {
        if (verificationId) {
            fetchInspectData(verificationId);
        }
    }, [verificationId]);

    const fetchInspectData = async (id: number) => {
        setLoading(true);
        setError(null);
        try {
            const response = await fetch(`/api/v1/verify/${id}/inspect`);
            if (!response.ok) throw new Error('Failed to fetch inspection data');
            const result = await response.json();
            setData(result);
        } catch (err) {
            setError(err instanceof Error ? err.message : 'Unknown error');
        } finally {
            setLoading(false);
        }
    };

    const getRiskBadgeClass = (score: number): string => {
        if (score >= 0.7) return 'risk-badge risk-high';
        if (score >= 0.4) return 'risk-badge risk-medium';
        return 'risk-badge risk-low';
    };

    const getRiskLabel = (score: number): string => {
        if (score >= 0.7) return 'HIGH RISK';
        if (score >= 0.4) return 'MEDIUM RISK';
        return 'LOW RISK';
    };

    const getFlagIcon = (flag: string): string => {
        if (flag.includes('DUPLICATE')) return '📋';
        if (flag.includes('GPS')) return '📍';
        if (flag.includes('EXIF')) return '📷';
        if (flag.includes('SOFTWARE')) return '🖥️';
        if (flag.includes('TIMESTAMP')) return '⏰';
        return '⚠️';
    };

    if (loading) {
        return (
            <div className="fraud-inspector loading">
                <div className="loading-spinner" />
                <p>Analyzing verification...</p>
            </div>
        );
    }

    if (error) {
        return (
            <div className="fraud-inspector error">
                <p className="error-message">❌ {error}</p>
            </div>
        );
    }

    if (!data) {
        return (
            <div className="fraud-inspector empty">
                <p>Select a verification to inspect</p>
            </div>
        );
    }

    return (
        <div className="fraud-inspector">
            {/* Header with Fraud Alert */}
            {data.fraud_detected && (
                <div className="fraud-banner">
                    <span className="fraud-icon">❌</span>
                    <span className="fraud-text">FRAUD DETECTED – PAYMENT BLOCKED</span>
                </div>
            )}

            {/* Risk Score */}
            <div className="risk-section">
                <div className={getRiskBadgeClass(data.risk_score)}>
                    <span className="risk-score">{Math.round(data.risk_score * 100)}%</span>
                    <span className="risk-label">{getRiskLabel(data.risk_score)}</span>
                </div>
                <div className="recommendation-badge" data-rec={data.recommendation}>
                    {data.recommendation.replace('_', ' ')}
                </div>
            </div>

            {/* Fraud Flags */}
            {data.flags.length > 0 && (
                <div className="flags-section">
                    <h4>🚨 Fraud Flags Detected</h4>
                    <ul className="flags-list">
                        {data.flags.map((flag, idx) => (
                            <li key={idx} className="flag-item">
                                <span className="flag-icon">{getFlagIcon(flag)}</span>
                                <span className="flag-text">{flag.replace('_', ' ')}</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* GPS Distance */}
            {data.gps_distance_m !== null && (
                <div className="gps-section">
                    <h4>📍 Location Verification</h4>
                    <div className={`gps-indicator ${data.gps_distance_m > 100 ? 'warning' : 'ok'}`}>
                        <span className="gps-distance">
                            {data.gps_distance_m > 1000
                                ? `${(data.gps_distance_m / 1000).toFixed(1)} km`
                                : `${Math.round(data.gps_distance_m)} m`}
                        </span>
                        <span className="gps-label">from expected location</span>
                    </div>
                    <div className="mini-map">
                        <div className="map-marker expected" title="Expected Location">📍</div>
                        <div
                            className="map-marker actual"
                            title="Photo Location"
                            style={{
                                left: `${Math.min(90, Math.max(10, 50 + (data.gps_distance_m || 0) / 20))}%`
                            }}
                        >
                            📸
                        </div>
                    </div>
                </div>
            )}

            {/* EXIF Metadata */}
            <div className="exif-section">
                <h4>📷 Photo Metadata</h4>
                <table className="exif-table">
                    <tbody>
                        <tr>
                            <td>GPS Data</td>
                            <td className={data.exif.has_gps ? 'ok' : 'warning'}>
                                {data.exif.has_gps ? '✅ Present' : '⚠️ Missing'}
                            </td>
                        </tr>
                        <tr>
                            <td>EXIF Data</td>
                            <td className={data.exif.has_exif ? 'ok' : 'warning'}>
                                {data.exif.has_exif ? '✅ Present' : '⚠️ Missing'}
                            </td>
                        </tr>
                        {data.exif.timestamp && (
                            <tr>
                                <td>Timestamp</td>
                                <td>{new Date(data.exif.timestamp).toLocaleString()}</td>
                            </tr>
                        )}
                        {data.exif.software && (
                            <tr className={data.exif.software.toLowerCase().includes('photoshop') ? 'danger' : ''}>
                                <td>Software</td>
                                <td>
                                    {data.exif.software.toLowerCase().includes('photoshop') && '⚠️ '}
                                    {data.exif.software}
                                </td>
                            </tr>
                        )}
                        {data.exif.camera && data.exif.camera.trim() && (
                            <tr>
                                <td>Camera</td>
                                <td>{data.exif.camera}</td>
                            </tr>
                        )}
                    </tbody>
                </table>
            </div>

            {/* Duplicate Photos */}
            {data.phash_matches.length > 0 && (
                <div className="duplicates-section">
                    <h4>📋 Duplicate Photo Matches</h4>
                    <ul className="duplicates-list">
                        {data.phash_matches.map((match, idx) => (
                            <li key={idx} className="duplicate-item" onClick={() => {
                                // Could navigate to matching verification
                                console.log('Navigate to', match.verification_id);
                            }}>
                                <span className="match-id">V-{match.verification_id}</span>
                                <span className="match-distance">Similarity: {100 - match.distance}%</span>
                            </li>
                        ))}
                    </ul>
                </div>
            )}

            {/* Action Buttons */}
            <div className="actions-section">
                {data.fraud_detected ? (
                    <>
                        <button
                            className="action-btn reject"
                            onClick={() => onReject?.(data.verification_id)}
                        >
                            ❌ Confirm Rejection
                        </button>
                        <button
                            className="action-btn evidence"
                            onClick={() => onRequestEvidence?.(data.verification_id)}
                        >
                            📤 Request New Evidence
                        </button>
                    </>
                ) : (
                    <>
                        <button
                            className="action-btn approve"
                            onClick={() => onApprove?.(data.verification_id)}
                        >
                            ✅ Approve
                        </button>
                        <button
                            className="action-btn flag"
                            onClick={() => onRequestEvidence?.(data.verification_id)}
                        >
                            🚩 Flag for Review
                        </button>
                    </>
                )}
            </div>

            {/* Status Footer */}
            <div className="status-footer">
                <span className="verification-id">ID: V-{data.verification_id}</span>
                <span className="status-badge" data-status={data.status}>
                    {data.status.toUpperCase()}
                </span>
                {data.submitted_at && (
                    <span className="submitted-at">
                        Submitted: {new Date(data.submitted_at).toLocaleDateString()}
                    </span>
                )}
            </div>
        </div>
    );
};

export default FraudInspector;
