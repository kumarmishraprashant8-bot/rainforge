/**
 * Admin Dashboard Component
 * Comprehensive admin panel for RainForge
 */

import React, { useState, useEffect } from 'react';

// Types
interface DashboardStats {
    totalProjects: number;
    activeUsers: number;
    verifiedInstallations: number;
    pendingVerifications: number;
    totalWaterSaved: number;
    totalCarbonOffset: number;
    revenueThisMonth: number;
    activeInstallers: number;
}

interface RecentActivity {
    id: string;
    type: 'project' | 'verification' | 'payment' | 'user' | 'alert';
    title: string;
    description: string;
    timestamp: string;
    user?: string;
    status?: string;
}

interface SystemHealth {
    status: 'healthy' | 'degraded' | 'unhealthy';
    uptime: string;
    checks: {
        name: string;
        status: string;
        latency_ms: number;
    }[];
}

export function AdminDashboard() {
    const [stats, setStats] = useState<DashboardStats | null>(null);
    const [activities, setActivities] = useState<RecentActivity[]>([]);
    const [health, setHealth] = useState<SystemHealth | null>(null);
    const [loading, setLoading] = useState(true);
    const [activeTab, setActiveTab] = useState<'overview' | 'users' | 'projects' | 'payments' | 'settings'>('overview');

    useEffect(() => {
        loadDashboardData();
        const interval = setInterval(loadDashboardData, 30000); // Refresh every 30s
        return () => clearInterval(interval);
    }, []);

    const loadDashboardData = async () => {
        try {
            // Mock data - would fetch from API
            setStats({
                totalProjects: 12847,
                activeUsers: 8934,
                verifiedInstallations: 9876,
                pendingVerifications: 234,
                totalWaterSaved: 45200000, // liters
                totalCarbonOffset: 13560, // kg
                revenueThisMonth: 1275000, // INR
                activeInstallers: 456
            });

            setActivities([
                { id: '1', type: 'project', title: 'New Project Registered', description: 'Project #12847 in Mumbai', timestamp: '2 min ago', status: 'pending' },
                { id: '2', type: 'verification', title: 'Verification Approved', description: 'Project #12845 passed QC', timestamp: '5 min ago', status: 'approved' },
                { id: '3', type: 'payment', title: 'Subsidy Disbursed', description: '₹25,000 to Project #12840', timestamp: '12 min ago', status: 'completed' },
                { id: '4', type: 'user', title: 'New Installer Registered', description: 'ABC RWH Solutions - Pune', timestamp: '15 min ago', status: 'pending' },
                { id: '5', type: 'alert', title: 'Low Tank Alert', description: 'Project #12830 at 15% capacity', timestamp: '20 min ago', status: 'warning' }
            ]);

            setHealth({
                status: 'healthy',
                uptime: '45d 12h 34m',
                checks: [
                    { name: 'database', status: 'healthy', latency_ms: 12 },
                    { name: 'redis', status: 'healthy', latency_ms: 3 },
                    { name: 'mqtt', status: 'healthy', latency_ms: 8 },
                    { name: 'disk', status: 'healthy', latency_ms: 0 },
                    { name: 'memory', status: 'healthy', latency_ms: 0 }
                ]
            });

            setLoading(false);
        } catch (err) {
            console.error('Failed to load dashboard data', err);
            setLoading(false);
        }
    };

    const formatNumber = (num: number) => {
        if (num >= 1000000) return `${(num / 1000000).toFixed(1)}M`;
        if (num >= 1000) return `${(num / 1000).toFixed(1)}K`;
        return num.toLocaleString('en-IN');
    };

    const getStatusColor = (status: string) => {
        switch (status) {
            case 'healthy':
            case 'approved':
            case 'completed':
                return '#22c55e';
            case 'degraded':
            case 'pending':
                return '#f59e0b';
            case 'unhealthy':
            case 'rejected':
            case 'warning':
                return '#ef4444';
            default:
                return '#64748b';
        }
    };

    const getActivityIcon = (type: string) => {
        switch (type) {
            case 'project': return '📁';
            case 'verification': return '✅';
            case 'payment': return '💰';
            case 'user': return '👤';
            case 'alert': return '🚨';
            default: return '📌';
        }
    };

    if (loading) {
        return (
            <div className="admin-loading">
                <div className="spinner"></div>
                <p>Loading dashboard...</p>
            </div>
        );
    }

    return (
        <div className="admin-dashboard">
            {/* Header */}
            <header className="admin-header">
                <div className="header-left">
                    <h1>🏛️ RainForge Admin</h1>
                    <span className="status-badge" style={{ backgroundColor: getStatusColor(health?.status || 'healthy') }}>
                        {health?.status || 'healthy'}
                    </span>
                </div>
                <div className="header-right">
                    <span className="uptime">Uptime: {health?.uptime}</span>
                    <button className="refresh-btn" onClick={loadDashboardData}>🔄 Refresh</button>
                </div>
            </header>

            {/* Navigation */}
            <nav className="admin-nav">
                {(['overview', 'users', 'projects', 'payments', 'settings'] as const).map(tab => (
                    <button
                        key={tab}
                        className={`nav-btn ${activeTab === tab ? 'active' : ''}`}
                        onClick={() => setActiveTab(tab)}
                    >
                        {tab === 'overview' && '📊 '}
                        {tab === 'users' && '👥 '}
                        {tab === 'projects' && '📁 '}
                        {tab === 'payments' && '💳 '}
                        {tab === 'settings' && '⚙️ '}
                        {tab.charAt(0).toUpperCase() + tab.slice(1)}
                    </button>
                ))}
            </nav>

            {activeTab === 'overview' && (
                <>
                    {/* Stats Grid */}
                    <div className="stats-grid">
                        <StatCard
                            icon="📁"
                            label="Total Projects"
                            value={formatNumber(stats?.totalProjects || 0)}
                            change="+12%"
                            color="#0ea5e9"
                        />
                        <StatCard
                            icon="👥"
                            label="Active Users"
                            value={formatNumber(stats?.activeUsers || 0)}
                            change="+8%"
                            color="#7c3aed"
                        />
                        <StatCard
                            icon="✅"
                            label="Verified Installations"
                            value={formatNumber(stats?.verifiedInstallations || 0)}
                            change="+15%"
                            color="#22c55e"
                        />
                        <StatCard
                            icon="⏳"
                            label="Pending Verifications"
                            value={stats?.pendingVerifications || 0}
                            change="-5%"
                            color="#f59e0b"
                        />
                        <StatCard
                            icon="💧"
                            label="Water Saved"
                            value={`${formatNumber(stats?.totalWaterSaved || 0)} L`}
                            change="+20%"
                            color="#0ea5e9"
                        />
                        <StatCard
                            icon="🌱"
                            label="CO₂ Offset"
                            value={`${formatNumber(stats?.totalCarbonOffset || 0)} kg`}
                            change="+18%"
                            color="#22c55e"
                        />
                        <StatCard
                            icon="💰"
                            label="Revenue (Month)"
                            value={`₹${formatNumber(stats?.revenueThisMonth || 0)}`}
                            change="+25%"
                            color="#f59e0b"
                        />
                        <StatCard
                            icon="🔧"
                            label="Active Installers"
                            value={stats?.activeInstallers || 0}
                            change="+10%"
                            color="#7c3aed"
                        />
                    </div>

                    {/* Content Grid */}
                    <div className="content-grid">
                        {/* Recent Activity */}
                        <div className="card activity-card">
                            <h3>📋 Recent Activity</h3>
                            <div className="activity-list">
                                {activities.map(activity => (
                                    <div key={activity.id} className="activity-item">
                                        <span className="activity-icon">{getActivityIcon(activity.type)}</span>
                                        <div className="activity-content">
                                            <span className="activity-title">{activity.title}</span>
                                            <span className="activity-desc">{activity.description}</span>
                                        </div>
                                        <div className="activity-meta">
                                            <span className="activity-time">{activity.timestamp}</span>
                                            {activity.status && (
                                                <span className="activity-status" style={{ color: getStatusColor(activity.status) }}>
                                                    {activity.status}
                                                </span>
                                            )}
                                        </div>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* System Health */}
                        <div className="card health-card">
                            <h3>🏥 System Health</h3>
                            <div className="health-checks">
                                {health?.checks.map(check => (
                                    <div key={check.name} className="health-check">
                                        <span className={`health-dot ${check.status}`}></span>
                                        <span className="check-name">{check.name}</span>
                                        <span className="check-latency">{check.latency_ms}ms</span>
                                    </div>
                                ))}
                            </div>
                        </div>

                        {/* Quick Actions */}
                        <div className="card actions-card">
                            <h3>⚡ Quick Actions</h3>
                            <div className="action-buttons">
                                <button className="action-btn primary">📊 Generate Report</button>
                                <button className="action-btn">📤 Export Data</button>
                                <button className="action-btn">📧 Send Notifications</button>
                                <button className="action-btn">🔄 Sync Sensors</button>
                                <button className="action-btn warning">⚠️ View Alerts</button>
                            </div>
                        </div>
                    </div>
                </>
            )}

            <style>{`
        .admin-dashboard {
          min-height: 100vh;
          background: #0f172a;
          color: #f8fafc;
          font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
        }

        .admin-loading {
          display: flex;
          flex-direction: column;
          align-items: center;
          justify-content: center;
          min-height: 100vh;
          background: #0f172a;
          color: #f8fafc;
        }

        .spinner {
          width: 40px;
          height: 40px;
          border: 3px solid #1e293b;
          border-top-color: #0ea5e9;
          border-radius: 50%;
          animation: spin 1s linear infinite;
        }

        @keyframes spin {
          to { transform: rotate(360deg); }
        }

        .admin-header {
          display: flex;
          justify-content: space-between;
          align-items: center;
          padding: 20px 24px;
          background: #1e293b;
          border-bottom: 1px solid #334155;
        }

        .header-left {
          display: flex;
          align-items: center;
          gap: 12px;
        }

        .header-left h1 {
          margin: 0;
          font-size: 24px;
          font-weight: 700;
        }

        .status-badge {
          padding: 4px 10px;
          border-radius: 12px;
          font-size: 12px;
          font-weight: 600;
          color: white;
          text-transform: uppercase;
        }

        .header-right {
          display: flex;
          align-items: center;
          gap: 16px;
        }

        .uptime {
          font-size: 13px;
          color: #94a3b8;
        }

        .refresh-btn {
          padding: 8px 16px;
          background: #334155;
          border: none;
          border-radius: 8px;
          color: white;
          cursor: pointer;
          transition: background 0.2s;
        }

        .refresh-btn:hover {
          background: #475569;
        }

        .admin-nav {
          display: flex;
          gap: 8px;
          padding: 16px 24px;
          background: #1e293b;
          border-bottom: 1px solid #334155;
        }

        .nav-btn {
          padding: 10px 20px;
          background: transparent;
          border: none;
          border-radius: 8px;
          color: #94a3b8;
          cursor: pointer;
          font-size: 14px;
          transition: all 0.2s;
        }

        .nav-btn:hover {
          background: #334155;
          color: white;
        }

        .nav-btn.active {
          background: #0ea5e9;
          color: white;
        }

        .stats-grid {
          display: grid;
          grid-template-columns: repeat(4, 1fr);
          gap: 16px;
          padding: 24px;
        }

        @media (max-width: 1200px) {
          .stats-grid {
            grid-template-columns: repeat(2, 1fr);
          }
        }

        .content-grid {
          display: grid;
          grid-template-columns: 2fr 1fr;
          gap: 16px;
          padding: 0 24px 24px;
        }

        @media (max-width: 1000px) {
          .content-grid {
            grid-template-columns: 1fr;
          }
        }

        .card {
          background: #1e293b;
          border-radius: 12px;
          padding: 20px;
        }

        .card h3 {
          margin: 0 0 16px 0;
          font-size: 16px;
          font-weight: 600;
        }

        .activity-list {
          display: flex;
          flex-direction: column;
          gap: 12px;
        }

        .activity-item {
          display: flex;
          align-items: center;
          gap: 12px;
          padding: 12px;
          background: #0f172a;
          border-radius: 8px;
        }

        .activity-icon {
          font-size: 20px;
        }

        .activity-content {
          flex: 1;
          display: flex;
          flex-direction: column;
        }

        .activity-title {
          font-weight: 500;
        }

        .activity-desc {
          font-size: 13px;
          color: #94a3b8;
        }

        .activity-meta {
          text-align: right;
        }

        .activity-time {
          font-size: 12px;
          color: #64748b;
          display: block;
        }

        .activity-status {
          font-size: 11px;
          font-weight: 600;
          text-transform: uppercase;
        }

        .health-checks {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .health-check {
          display: flex;
          align-items: center;
          gap: 10px;
          padding: 10px;
          background: #0f172a;
          border-radius: 8px;
        }

        .health-dot {
          width: 10px;
          height: 10px;
          border-radius: 50%;
        }

        .health-dot.healthy { background: #22c55e; }
        .health-dot.degraded { background: #f59e0b; }
        .health-dot.unhealthy { background: #ef4444; }

        .check-name {
          flex: 1;
          text-transform: capitalize;
        }

        .check-latency {
          font-size: 12px;
          color: #64748b;
        }

        .action-buttons {
          display: flex;
          flex-direction: column;
          gap: 10px;
        }

        .action-btn {
          padding: 12px 16px;
          background: #334155;
          border: none;
          border-radius: 8px;
          color: white;
          cursor: pointer;
          text-align: left;
          transition: all 0.2s;
        }

        .action-btn:hover {
          background: #475569;
          transform: translateX(4px);
        }

        .action-btn.primary {
          background: #0ea5e9;
        }

        .action-btn.warning {
          background: #f59e0b;
        }
      `}</style>
        </div>
    );
}

// Stat Card Component
function StatCard({ icon, label, value, change, color }: {
    icon: string;
    label: string;
    value: string | number;
    change: string;
    color: string;
}) {
    const isPositive = change.startsWith('+');

    return (
        <div className="stat-card" style={{ borderLeftColor: color }}>
            <div className="stat-icon">{icon}</div>
            <div className="stat-content">
                <span className="stat-label">{label}</span>
                <span className="stat-value">{value}</span>
                <span className={`stat-change ${isPositive ? 'positive' : 'negative'}`}>
                    {change}
                </span>
            </div>
            <style>{`
        .stat-card {
          background: #1e293b;
          border-radius: 12px;
          padding: 20px;
          display: flex;
          align-items: center;
          gap: 16px;
          border-left: 4px solid;
        }

        .stat-icon {
          font-size: 32px;
        }

        .stat-content {
          display: flex;
          flex-direction: column;
        }

        .stat-label {
          font-size: 13px;
          color: #94a3b8;
        }

        .stat-value {
          font-size: 24px;
          font-weight: 700;
          color: #f8fafc;
        }

        .stat-change {
          font-size: 12px;
          font-weight: 600;
        }

        .stat-change.positive {
          color: #22c55e;
        }

        .stat-change.negative {
          color: #ef4444;
        }
      `}</style>
        </div>
    );
}

export default AdminDashboard;
