/**
 * Performance Dashboard Component
 * Track actual vs projected, neighbor comparison, leaderboard, maintenance
 */

import React, { useState, useEffect } from 'react';

interface MonthlyData {
    month: string;
    actual_collection_liters: number;
    projected_collection_liters: number;
    efficiency_percent: number;
    avg_tank_level_percent: number;
}

interface PerformanceReport {
    project_id: number;
    year: number;
    total_collection_liters: number;
    projected_collection_liters: number;
    actual_vs_projected_percent: number;
    total_savings_inr: number;
    carbon_offset_kg: number;
    performance_score: number;
    reliability_score: number;
    monthly_data: MonthlyData[];
}

interface NeighborComparison {
    your_collection_liters: number;
    area_average_collection: number;
    vs_average_collection_percent: number;
    area_rank: number;
    total_in_area: number;
    percentile: number;
    message: string;
    top_performers: Array<{
        rank: number;
        area: string;
        collection_liters: number;
        efficiency_percent: number;
    }>;
}

interface MaintenanceTask {
    task_id: string;
    task_name: string;
    description: string;
    next_due: string;
    is_overdue: boolean;
    days_until_due: number;
    priority: string;
    estimated_cost: number;
}

interface PerformanceDashboardProps {
    projectId: number;
    city: string;
    year?: number;
}

export const PerformanceDashboard: React.FC<PerformanceDashboardProps> = ({
    projectId,
    city,
    year = new Date().getFullYear(),
}) => {
    const [activeTab, setActiveTab] = useState<'overview' | 'comparison' | 'maintenance'>('overview');
    const [performance, setPerformance] = useState<PerformanceReport | null>(null);
    const [comparison, setComparison] = useState<NeighborComparison | null>(null);
    const [maintenance, setMaintenance] = useState<MaintenanceTask[]>([]);
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        fetchData();
    }, [projectId, year]);

    const fetchData = async () => {
        setLoading(true);
        try {
            // Demo data
            setPerformance({
                project_id: projectId,
                year: year,
                total_collection_liters: 85400,
                projected_collection_liters: 100000,
                actual_vs_projected_percent: 85.4,
                total_savings_inr: 12500,
                carbon_offset_kg: 42.7,
                performance_score: 85,
                reliability_score: 78,
                monthly_data: [
                    { month: 'Jan', actual_collection_liters: 1200, projected_collection_liters: 2000, efficiency_percent: 60, avg_tank_level_percent: 30 },
                    { month: 'Feb', actual_collection_liters: 1500, projected_collection_liters: 2000, efficiency_percent: 75, avg_tank_level_percent: 35 },
                    { month: 'Mar', actual_collection_liters: 2800, projected_collection_liters: 3000, efficiency_percent: 93, avg_tank_level_percent: 45 },
                    { month: 'Apr', actual_collection_liters: 3500, projected_collection_liters: 4000, efficiency_percent: 88, avg_tank_level_percent: 50 },
                    { month: 'May', actual_collection_liters: 4800, projected_collection_liters: 5000, efficiency_percent: 96, avg_tank_level_percent: 55 },
                    { month: 'Jun', actual_collection_liters: 14500, projected_collection_liters: 15000, efficiency_percent: 97, avg_tank_level_percent: 85 },
                    { month: 'Jul', actual_collection_liters: 23000, projected_collection_liters: 25000, efficiency_percent: 92, avg_tank_level_percent: 90 },
                    { month: 'Aug', actual_collection_liters: 20500, projected_collection_liters: 22000, efficiency_percent: 93, avg_tank_level_percent: 88 },
                    { month: 'Sep', actual_collection_liters: 12000, projected_collection_liters: 14000, efficiency_percent: 86, avg_tank_level_percent: 70 },
                    { month: 'Oct', actual_collection_liters: 4200, projected_collection_liters: 5000, efficiency_percent: 84, avg_tank_level_percent: 45 },
                    { month: 'Nov', actual_collection_liters: 1800, projected_collection_liters: 2000, efficiency_percent: 90, avg_tank_level_percent: 35 },
                    { month: 'Dec', actual_collection_liters: 800, projected_collection_liters: 1000, efficiency_percent: 80, avg_tank_level_percent: 25 },
                ],
            });

            setComparison({
                your_collection_liters: 85400,
                area_average_collection: 72000,
                vs_average_collection_percent: 18.6,
                area_rank: 12,
                total_in_area: 156,
                percentile: 92,
                message: '⭐ Excellent! You\'re outperforming 92% of your neighbors!',
                top_performers: [
                    { rank: 1, area: 'Sector 42', collection_liters: 125000, efficiency_percent: 98.5 },
                    { rank: 2, area: 'Sector 18', collection_liters: 118000, efficiency_percent: 97.2 },
                    { rank: 3, area: 'Sector 56', collection_liters: 112000, efficiency_percent: 96.8 },
                    { rank: 4, area: 'Sector 23', collection_liters: 105000, efficiency_percent: 95.1 },
                    { rank: 5, area: 'Sector 9', collection_liters: 98000, efficiency_percent: 94.3 },
                ],
            });

            setMaintenance([
                {
                    task_id: 'T1',
                    task_name: 'Clean Gutters',
                    description: 'Remove leaves, debris, and sediment',
                    next_due: new Date(Date.now() - 86400000 * 3).toISOString(),
                    is_overdue: true,
                    days_until_due: -3,
                    priority: 'high',
                    estimated_cost: 0,
                },
                {
                    task_id: 'T2',
                    task_name: 'Clean Filter',
                    description: 'Replace or clean filter media',
                    next_due: new Date(Date.now() + 86400000 * 5).toISOString(),
                    is_overdue: false,
                    days_until_due: 5,
                    priority: 'high',
                    estimated_cost: 200,
                },
                {
                    task_id: 'T3',
                    task_name: 'Inspect Tank',
                    description: 'Visual inspection for cracks or leaks',
                    next_due: new Date(Date.now() + 86400000 * 15).toISOString(),
                    is_overdue: false,
                    days_until_due: 15,
                    priority: 'medium',
                    estimated_cost: 0,
                },
                {
                    task_id: 'T4',
                    task_name: 'Pre-Monsoon Check',
                    description: 'Complete system check before monsoon',
                    next_due: new Date(Date.now() + 86400000 * 45).toISOString(),
                    is_overdue: false,
                    days_until_due: 45,
                    priority: 'critical',
                    estimated_cost: 500,
                },
            ]);
        } finally {
            setLoading(false);
        }
    };

    const getScoreColor = (score: number) => {
        if (score >= 90) return '#22c55e';
        if (score >= 75) return '#84cc16';
        if (score >= 60) return '#f59e0b';
        return '#ef4444';
    };

    const renderBarChart = (data: MonthlyData[]) => {
        const maxValue = Math.max(...data.map(d => Math.max(d.actual_collection_liters, d.projected_collection_liters)));

        return (
            <div style={{
                display: 'flex',
                gap: '8px',
                alignItems: 'flex-end',
                height: '200px',
                padding: '16px',
                background: '#f8fafc',
                borderRadius: '12px',
            }}>
                {data.map((d, i) => (
                    <div key={i} style={{ flex: 1, display: 'flex', flexDirection: 'column', alignItems: 'center', gap: '4px' }}>
                        <div style={{
                            display: 'flex',
                            gap: '2px',
                            alignItems: 'flex-end',
                            height: '160px',
                        }}>
                            <div
                                style={{
                                    width: '12px',
                                    height: `${(d.projected_collection_liters / maxValue) * 100}%`,
                                    background: '#e2e8f0',
                                    borderRadius: '4px 4px 0 0',
                                }}
                                title={`Projected: ${d.projected_collection_liters.toLocaleString()}L`}
                            />
                            <div
                                style={{
                                    width: '12px',
                                    height: `${(d.actual_collection_liters / maxValue) * 100}%`,
                                    background: d.efficiency_percent >= 90 ? '#22c55e' : d.efficiency_percent >= 75 ? '#3b82f6' : '#f59e0b',
                                    borderRadius: '4px 4px 0 0',
                                }}
                                title={`Actual: ${d.actual_collection_liters.toLocaleString()}L`}
                            />
                        </div>
                        <span style={{ fontSize: '11px', color: '#64748b' }}>{d.month}</span>
                    </div>
                ))}
            </div>
        );
    };

    if (loading) {
        return (
            <div style={{ textAlign: 'center', padding: '48px' }}>
                <div style={{ fontSize: '36px', marginBottom: '16px' }}>⏳</div>
                <p>Loading performance data...</p>
            </div>
        );
    }

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
                📊 Performance Dashboard
            </h2>
            <p style={{ color: '#64748b', marginBottom: '24px' }}>
                Track your rainwater harvesting system performance for {year}
            </p>

            {/* Tab Navigation */}
            <div style={{ display: 'flex', gap: '8px', marginBottom: '24px' }}>
                {[
                    { id: 'overview', label: 'Overview', icon: '📈' },
                    { id: 'comparison', label: 'Neighbor Comparison', icon: '🏆' },
                    { id: 'maintenance', label: 'Maintenance', icon: '🔧' },
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

            {/* Overview Tab */}
            {activeTab === 'overview' && performance && (
                <div>
                    {/* Score Cards */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: 'repeat(4, 1fr)',
                        gap: '16px',
                        marginBottom: '24px',
                    }}>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b' }}>Total Collection</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#3b82f6' }}>
                                {(performance.total_collection_liters / 1000).toFixed(1)}K
                            </div>
                            <div style={{ fontSize: '12px', color: '#64748b' }}>liters</div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b' }}>Efficiency</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: getScoreColor(performance.actual_vs_projected_percent) }}>
                                {performance.actual_vs_projected_percent.toFixed(1)}%
                            </div>
                            <div style={{ fontSize: '12px', color: '#64748b' }}>of projected</div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b' }}>Total Savings</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#22c55e' }}>
                                ₹{performance.total_savings_inr.toLocaleString()}
                            </div>
                            <div style={{ fontSize: '12px', color: '#64748b' }}>this year</div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b' }}>Carbon Offset</div>
                            <div style={{ fontSize: '28px', fontWeight: 700, color: '#10b981' }}>
                                {performance.carbon_offset_kg.toFixed(1)}
                            </div>
                            <div style={{ fontSize: '12px', color: '#64748b' }}>kg CO₂</div>
                        </div>
                    </div>

                    {/* Performance Scores */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '24px',
                        marginBottom: '24px',
                    }}>
                        <div style={{
                            background: 'white',
                            borderRadius: '16px',
                            padding: '24px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                            border: '1px solid #e2e8f0',
                        }}>
                            <h4 style={{ marginBottom: '16px' }}>Performance Score</h4>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <div style={{
                                    width: '100px',
                                    height: '100px',
                                    borderRadius: '50%',
                                    background: `conic-gradient(${getScoreColor(performance.performance_score)} ${performance.performance_score}%, #e2e8f0 0%)`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}>
                                    <div style={{
                                        width: '80px',
                                        height: '80px',
                                        borderRadius: '50%',
                                        background: 'white',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '28px',
                                        fontWeight: 700,
                                        color: getScoreColor(performance.performance_score),
                                    }}>
                                        {performance.performance_score}
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                                        {performance.performance_score >= 90 ? 'Excellent!' :
                                            performance.performance_score >= 75 ? 'Good' :
                                                performance.performance_score >= 60 ? 'Average' : 'Needs Improvement'}
                                    </div>
                                    <div style={{ fontSize: '14px', color: '#64748b' }}>
                                        Based on collection efficiency and system utilization
                                    </div>
                                </div>
                            </div>
                        </div>

                        <div style={{
                            background: 'white',
                            borderRadius: '16px',
                            padding: '24px',
                            boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                            border: '1px solid #e2e8f0',
                        }}>
                            <h4 style={{ marginBottom: '16px' }}>Reliability Score</h4>
                            <div style={{ display: 'flex', alignItems: 'center', gap: '16px' }}>
                                <div style={{
                                    width: '100px',
                                    height: '100px',
                                    borderRadius: '50%',
                                    background: `conic-gradient(${getScoreColor(performance.reliability_score)} ${performance.reliability_score}%, #e2e8f0 0%)`,
                                    display: 'flex',
                                    alignItems: 'center',
                                    justifyContent: 'center',
                                }}>
                                    <div style={{
                                        width: '80px',
                                        height: '80px',
                                        borderRadius: '50%',
                                        background: 'white',
                                        display: 'flex',
                                        alignItems: 'center',
                                        justifyContent: 'center',
                                        fontSize: '28px',
                                        fontWeight: 700,
                                        color: getScoreColor(performance.reliability_score),
                                    }}>
                                        {performance.reliability_score}
                                    </div>
                                </div>
                                <div>
                                    <div style={{ fontWeight: 600, marginBottom: '4px' }}>
                                        {performance.reliability_score >= 90 ? 'Very Reliable' :
                                            performance.reliability_score >= 75 ? 'Reliable' :
                                                performance.reliability_score >= 60 ? 'Moderate' : 'Needs Attention'}
                                    </div>
                                    <div style={{ fontSize: '14px', color: '#64748b' }}>
                                        Based on sensor uptime and data consistency
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>

                    {/* Monthly Chart */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        border: '1px solid #e2e8f0',
                    }}>
                        <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '16px' }}>
                            <h4 style={{ margin: 0 }}>Monthly Collection</h4>
                            <div style={{ display: 'flex', gap: '16px', fontSize: '12px' }}>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <span style={{ width: '12px', height: '12px', background: '#e2e8f0', borderRadius: '2px' }}></span>
                                    Projected
                                </span>
                                <span style={{ display: 'flex', alignItems: 'center', gap: '4px' }}>
                                    <span style={{ width: '12px', height: '12px', background: '#3b82f6', borderRadius: '2px' }}></span>
                                    Actual
                                </span>
                            </div>
                        </div>
                        {renderBarChart(performance.monthly_data)}
                    </div>
                </div>
            )}

            {/* Comparison Tab */}
            {activeTab === 'comparison' && comparison && (
                <div>
                    {/* Ranking Card */}
                    <div style={{
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.1), rgba(147,51,234,0.1))',
                        borderRadius: '16px',
                        padding: '32px',
                        textAlign: 'center',
                        marginBottom: '24px',
                        border: '1px solid rgba(59,130,246,0.2)',
                    }}>
                        <div style={{ fontSize: '64px', marginBottom: '8px' }}>🏆</div>
                        <h3 style={{ fontSize: '24px', marginBottom: '8px' }}>
                            You're #{comparison.area_rank} in {city}!
                        </h3>
                        <p style={{ color: '#64748b', marginBottom: '16px' }}>
                            Out of {comparison.total_in_area} RWH systems
                        </p>
                        <div style={{
                            display: 'inline-block',
                            padding: '8px 24px',
                            background: comparison.percentile >= 90 ? '#22c55e' : comparison.percentile >= 75 ? '#3b82f6' : '#f59e0b',
                            color: 'white',
                            borderRadius: '20px',
                            fontWeight: 600,
                        }}>
                            Top {100 - comparison.percentile}%
                        </div>
                        <p style={{ marginTop: '16px', fontSize: '18px', fontWeight: 500 }}>
                            {comparison.message}
                        </p>
                    </div>

                    {/* Comparison Stats */}
                    <div style={{
                        display: 'grid',
                        gridTemplateColumns: '1fr 1fr',
                        gap: '24px',
                        marginBottom: '24px',
                    }}>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Your Collection</div>
                            <div style={{ fontSize: '32px', fontWeight: 700, color: '#3b82f6' }}>
                                {(comparison.your_collection_liters / 1000).toFixed(1)}K L
                            </div>
                            <div style={{
                                fontSize: '14px',
                                color: comparison.vs_average_collection_percent >= 0 ? '#22c55e' : '#ef4444',
                                marginTop: '8px',
                            }}>
                                {comparison.vs_average_collection_percent >= 0 ? '↑' : '↓'} {Math.abs(comparison.vs_average_collection_percent).toFixed(1)}% vs area average
                            </div>
                        </div>
                        <div style={cardStyle}>
                            <div style={{ fontSize: '14px', color: '#64748b', marginBottom: '8px' }}>Area Average</div>
                            <div style={{ fontSize: '32px', fontWeight: 700, color: '#64748b' }}>
                                {(comparison.area_average_collection / 1000).toFixed(1)}K L
                            </div>
                            <div style={{ fontSize: '14px', color: '#64748b', marginTop: '8px' }}>
                                {comparison.total_in_area} systems in {city}
                            </div>
                        </div>
                    </div>

                    {/* Leaderboard */}
                    <div style={{
                        background: 'white',
                        borderRadius: '16px',
                        padding: '24px',
                        boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                        border: '1px solid #e2e8f0',
                    }}>
                        <h4 style={{ marginBottom: '16px' }}>🏅 Top Performers in {city}</h4>
                        <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                            {comparison.top_performers.map((performer, i) => (
                                <div
                                    key={i}
                                    style={{
                                        display: 'flex',
                                        alignItems: 'center',
                                        gap: '16px',
                                        padding: '12px 16px',
                                        background: i === 0 ? 'linear-gradient(135deg, rgba(250,204,21,0.1), rgba(251,191,36,0.1))' : '#f8fafc',
                                        borderRadius: '10px',
                                        border: i === 0 ? '1px solid #fde047' : '1px solid transparent',
                                    }}
                                >
                                    <div style={{
                                        fontSize: '24px',
                                        width: '40px',
                                        textAlign: 'center',
                                        fontWeight: 700,
                                        color: i === 0 ? '#eab308' : i === 1 ? '#94a3b8' : i === 2 ? '#cd7f32' : '#64748b',
                                    }}>
                                        {i === 0 ? '🥇' : i === 1 ? '🥈' : i === 2 ? '🥉' : `#${performer.rank}`}
                                    </div>
                                    <div style={{ flex: 1 }}>
                                        <div style={{ fontWeight: 600 }}>{performer.area}</div>
                                        <div style={{ fontSize: '13px', color: '#64748b' }}>
                                            {performer.efficiency_percent.toFixed(1)}% efficiency
                                        </div>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        <div style={{ fontWeight: 700, color: '#3b82f6' }}>
                                            {(performer.collection_liters / 1000).toFixed(0)}K L
                                        </div>
                                    </div>
                                </div>
                            ))}
                        </div>
                    </div>
                </div>
            )}

            {/* Maintenance Tab */}
            {activeTab === 'maintenance' && (
                <div>
                    {/* Overdue Alert */}
                    {maintenance.some(m => m.is_overdue) && (
                        <div style={{
                            background: '#fef2f2',
                            borderRadius: '12px',
                            padding: '16px',
                            marginBottom: '24px',
                            border: '1px solid #fecaca',
                            display: 'flex',
                            alignItems: 'center',
                            gap: '12px',
                        }}>
                            <span style={{ fontSize: '24px' }}>⚠️</span>
                            <div>
                                <div style={{ fontWeight: 600, color: '#991b1b' }}>Overdue Maintenance Tasks</div>
                                <div style={{ fontSize: '14px', color: '#b91c1c' }}>
                                    {maintenance.filter(m => m.is_overdue).length} task(s) need immediate attention
                                </div>
                            </div>
                        </div>
                    )}

                    {/* Task List */}
                    <div style={{ display: 'flex', flexDirection: 'column', gap: '12px' }}>
                        {maintenance.map(task => (
                            <div
                                key={task.task_id}
                                style={{
                                    background: 'white',
                                    borderRadius: '12px',
                                    padding: '20px',
                                    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
                                    border: task.is_overdue ? '2px solid #ef4444' : '1px solid #e2e8f0',
                                }}
                            >
                                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                                    <div>
                                        <div style={{ display: 'flex', alignItems: 'center', gap: '8px', marginBottom: '4px' }}>
                                            <h4 style={{ margin: 0, fontSize: '16px', fontWeight: 600 }}>
                                                {task.task_name}
                                            </h4>
                                            <span style={{
                                                padding: '2px 8px',
                                                borderRadius: '12px',
                                                fontSize: '11px',
                                                fontWeight: 600,
                                                background: task.priority === 'critical' ? '#fef2f2' :
                                                    task.priority === 'high' ? '#fef3c7' : '#f1f5f9',
                                                color: task.priority === 'critical' ? '#991b1b' :
                                                    task.priority === 'high' ? '#b45309' : '#64748b',
                                            }}>
                                                {task.priority.toUpperCase()}
                                            </span>
                                        </div>
                                        <p style={{ margin: 0, color: '#64748b', fontSize: '14px' }}>
                                            {task.description}
                                        </p>
                                    </div>
                                    <div style={{ textAlign: 'right' }}>
                                        {task.is_overdue ? (
                                            <div style={{ color: '#ef4444', fontWeight: 600 }}>
                                                Overdue by {Math.abs(task.days_until_due)} days
                                            </div>
                                        ) : (
                                            <div style={{ color: task.days_until_due <= 7 ? '#f59e0b' : '#64748b' }}>
                                                Due in {task.days_until_due} days
                                            </div>
                                        )}
                                        {task.estimated_cost > 0 && (
                                            <div style={{ fontSize: '13px', color: '#64748b' }}>
                                                Est. cost: ₹{task.estimated_cost}
                                            </div>
                                        )}
                                    </div>
                                </div>
                                <div style={{ marginTop: '12px' }}>
                                    <button style={{
                                        padding: '8px 16px',
                                        background: task.is_overdue ? 'linear-gradient(135deg, #ef4444, #dc2626)' :
                                            'linear-gradient(135deg, #22c55e, #16a34a)',
                                        border: 'none',
                                        borderRadius: '8px',
                                        color: 'white',
                                        fontWeight: 600,
                                        cursor: 'pointer',
                                        fontSize: '13px',
                                    }}>
                                        ✓ Mark as Complete
                                    </button>
                                </div>
                            </div>
                        ))}
                    </div>

                    {/* Pre-Monsoon Checklist */}
                    <div style={{
                        background: 'linear-gradient(135deg, rgba(59,130,246,0.05), rgba(147,51,234,0.05))',
                        borderRadius: '16px',
                        padding: '24px',
                        marginTop: '24px',
                        border: '1px solid rgba(59,130,246,0.2)',
                    }}>
                        <h4 style={{ marginBottom: '12px' }}>🌧️ Pre-Monsoon Checklist</h4>
                        <p style={{ color: '#64748b', marginBottom: '16px' }}>
                            Complete these tasks before monsoon season for optimal performance
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
                            📋 View Checklist
                        </button>
                    </div>
                </div>
            )}
        </div>
    );
};

const cardStyle: React.CSSProperties = {
    background: 'white',
    borderRadius: '16px',
    padding: '20px',
    boxShadow: '0 2px 8px rgba(0,0,0,0.06)',
    border: '1px solid #e2e8f0',
    textAlign: 'center',
};

export default PerformanceDashboard;
