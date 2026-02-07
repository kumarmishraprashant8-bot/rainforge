import { useNavigate } from 'react-router-dom';
import {
    Droplets, TrendingUp, Leaf,
    CheckCircle, Clock, AlertTriangle, ChevronRight, Download,
    ArrowUpRight, BarChart3, Building2
} from 'lucide-react';

interface ProjectSummary {
    id: number;
    address: string;
    status: string;
    annual_yield_liters: number;
    tank_size_liters: number;
    verification_status: string;
}

const PortfolioDashboard = () => {
    const navigate = useNavigate();

    // Mock portfolio data
    const stats = {
        total_projects: 47,
        installed_count: 32,
        pending_count: 15,
        total_investment_inr: 4750000,
        total_water_captured_liters: 3250000,
        avg_roi_years: 3.2,
        co2_offset_kg: 2275
    };

    const projects: ProjectSummary[] = [
        { id: 1, address: "Municipal School Sector 5", status: "installed", annual_yield_liters: 85000, tank_size_liters: 15000, verification_status: "verified" },
        { id: 2, address: "Community Hall Block A", status: "installed", annual_yield_liters: 65000, tank_size_liters: 12000, verification_status: "verified" },
        { id: 3, address: "Primary Health Center", status: "pending", annual_yield_liters: 45000, tank_size_liters: 8000, verification_status: "pending" },
        { id: 4, address: "Govt Office Complex", status: "installed", annual_yield_liters: 120000, tank_size_liters: 20000, verification_status: "verified" },
        { id: 5, address: "Anganwadi Center Ward 7", status: "pending", annual_yield_liters: 32000, tank_size_liters: 5000, verification_status: "not_submitted" },
        { id: 6, address: "Public Library Main", status: "installed", annual_yield_liters: 75000, tank_size_liters: 12000, verification_status: "verified" },
    ];

    // Export portfolio data as Direct PDF Download
    const handleExport = () => {
        // Load html2pdf dynamically
        const script = document.createElement('script');
        script.src = 'https://cdnjs.cloudflare.com/ajax/libs/html2pdf.js/0.10.1/html2pdf.bundle.min.js';
        script.onload = () => {
            generatePDF();
        };
        document.body.appendChild(script);

        const generatePDF = () => {
            const date = new Date().toLocaleDateString('en-IN', { day: 'numeric', month: 'long', year: 'numeric' });

            // Create a temporary container for the report
            const container = document.createElement('div');
            container.innerHTML = `
            <div style="font-family: 'Inter', sans-serif; padding: 40px; color: #0f172a; background: white;">
                <div style="display: flex; justify-content: space-between; align-items: center; border-bottom: 2px solid #e2e8f0; padding-bottom: 20px; margin-bottom: 30px;">
                    <div>
                        <div style="background: #f3f4f6; padding: 4px 12px; border-radius: 999px; font-size: 12px; font-weight: 600; color: #4b5563; text-transform: uppercase; display: inline-block; margin-bottom: 8px;">Government Portal</div>
                        <h1 style="margin: 0 0 5px 0; font-size: 32px; color: #1e293b;">Portfolio Overview</h1>
                        <p style="color: #64748b; font-size: 16px; margin: 0;">District-level RWH Deployment Report • ${date}</p>
                    </div>
                    <div style="font-size: 24px; font-weight: 800; color: #7c3aed;">
                         💧 RainForge
                    </div>
                </div>

                <!-- Metrics Grid -->
                <div style="display: grid; grid-template-columns: repeat(4, 1fr); gap: 15px; margin-bottom: 40px;">
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;">
                        <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;">Water Captured</div>
                        <div style="font-size: 24px; font-weight: 700; color: #0f172a;">${(stats.total_water_captured_liters / 1000000).toFixed(1)} ML</div>
                        <div style="font-size: 12px; color: #94a3b8;">12% increase</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;">
                        <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;">Investment</div>
                        <div style="font-size: 24px; font-weight: 700; color: #0f172a;">₹${(stats.total_investment_inr / 100000).toFixed(1)} L</div>
                        <div style="font-size: 12px; color: #94a3b8;">${stats.total_projects} projects</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;">
                        <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;">Avg ROI</div>
                        <div style="font-size: 24px; font-weight: 700; color: #0f172a;">${stats.avg_roi_years} yrs</div>
                        <div style="font-size: 12px; color: #94a3b8;">Payback</div>
                    </div>
                    <div style="background: #f8fafc; border: 1px solid #e2e8f0; border-radius: 12px; padding: 15px;">
                        <div style="font-size: 12px; font-weight: 600; color: #64748b; text-transform: uppercase;">CO2 Offset</div>
                        <div style="font-size: 24px; font-weight: 700; color: #0f172a;">${(stats.co2_offset_kg / 1000).toFixed(1)} T</div>
                        <div style="font-size: 12px; color: #94a3b8;">per year</div>
                    </div>
                </div>

                <h3 style="font-size: 18px; color: #1e293b; margin-bottom: 15px;">Project Details</h3>
                <table style="width: 100%; border-collapse: collapse; font-size: 14px;">
                    <thead>
                        <tr style="background: #f8fafc;">
                            <th style="text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569;">Project</th>
                            <th style="text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569;">Status</th>
                            <th style="text-align: right; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569;">Yield (kL)</th>
                            <th style="text-align: right; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569;">Tank (kL)</th>
                            <th style="text-align: left; padding: 12px; border-bottom: 2px solid #e2e8f0; color: #475569;">Verification</th>
                        </tr>
                    </thead>
                    <tbody>
                        ${projects.map(p => `
                            <tr>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                                    <strong>${p.address}</strong>
                                    <div style="font-size: 11px; color: #94a3b8;">ID: ${p.id}</div>
                                </td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                                    <span style="color: ${p.status === 'installed' ? '#059669' : '#d97706'}">
                                        ${p.status.charAt(0).toUpperCase() + p.status.slice(1)}
                                    </span>
                                </td>
                                <td style="text-align: right; padding: 12px; border-bottom: 1px solid #e2e8f0;">${(p.annual_yield_liters / 1000).toFixed(0)}</td>
                                <td style="text-align: right; padding: 12px; border-bottom: 1px solid #e2e8f0;">${(p.tank_size_liters / 1000).toFixed(0)}</td>
                                <td style="padding: 12px; border-bottom: 1px solid #e2e8f0;">
                                    ${p.verification_status === 'verified' ? '✅ Verified' :
                    p.verification_status === 'pending' ? '⏳ Pending' : '⚠️ Not Submitted'}
                                </td>
                            </tr>
                        `).join('')}
                    </tbody>
                </table>

                <div style="margin-top: 40px; padding-top: 20px; border-top: 1px solid #e2e8f0; display: flex; justify-content: space-between; color: #94a3b8; font-size: 12px;">
                    <div>Generated by RainForge Government Portal</div>
                    <div>Official Record • ${new Date().toISOString().split('T')[0]}</div>
                </div>
            </div>
            `;

            // Use html2pdf to generate and save
            // @ts-ignore
            if (window.html2pdf) {
                const opt = {
                    margin: 10,
                    filename: `RainForge_Report_${new Date().toISOString().split('T')[0]}.pdf`,
                    image: { type: 'jpeg', quality: 0.98 },
                    html2canvas: { scale: 2 },
                    jsPDF: { unit: 'mm', format: 'a4', orientation: 'portrait' }
                };

                // @ts-ignore
                window.html2pdf().from(container).set(opt).save();
            } else {
                alert('PDF Generator is loading... please try again in a second.');
            }
        };
    };

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'installed':
            case 'verified':
                return <span className="badge-green">✓ Verified</span>;
            case 'pending':
                return <span className="badge-yellow">⏳ Pending</span>;
            default:
                return <span className="badge-purple">{status.replace('_', ' ')}</span>;
        }
    };

    return (
        <div className="min-h-screen py-8 px-4 lg:px-8">
            <div className="max-w-7xl mx-auto">
                {/* Header */}
                <div className="flex flex-col lg:flex-row lg:justify-between lg:items-start gap-6 mb-10">
                    <div className="animate-fade-in-up">
                        <div className="badge-purple mb-4 inline-flex items-center gap-2">
                            <Building2 size={14} />
                            <span>Government Portal</span>
                        </div>
                        <h1 className="text-4xl lg:text-5xl font-bold text-white mb-3">
                            Portfolio Overview
                        </h1>
                        <p className="text-zinc-400 text-lg">
                            District-level RWH deployment analytics
                        </p>
                    </div>
                    <button onClick={handleExport} className="btn-primary flex items-center gap-2 animate-fade-in stagger-2">
                        <Download size={18} />
                        Export Report
                    </button>
                </div>

                {/* Key Stats Grid - VIBRANT COLORFUL CARDS */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-5 mb-10">
                    {/* Water Captured - Cyan */}
                    <div className="stat-card stat-card-cyan hover-scale animate-fade-in-up stagger-1">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="stat-icon stat-icon-cyan">
                                <Droplets size={22} />
                            </div>
                            <span className="text-zinc-400 text-sm font-medium">Water Captured</span>
                        </div>
                        <div className="text-3xl font-bold text-white mb-1">
                            {(stats.total_water_captured_liters / 1000000).toFixed(1)}<span className="text-xl font-normal text-zinc-500"> ML</span>
                        </div>
                        <div className="flex items-center gap-1 text-emerald-400 text-sm">
                            <ArrowUpRight size={14} />
                            <span>12% this quarter</span>
                        </div>
                    </div>

                    {/* Total Investment - Green */}
                    <div className="stat-card stat-card-green hover-scale animate-fade-in-up stagger-2">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="stat-icon stat-icon-green">
                                <BarChart3 size={22} />
                            </div>
                            <span className="text-zinc-400 text-sm font-medium">Investment</span>
                        </div>
                        <div className="text-3xl font-bold text-white mb-1">
                            ₹{(stats.total_investment_inr / 100000).toFixed(1)}<span className="text-xl font-normal text-zinc-500"> L</span>
                        </div>
                        <div className="text-zinc-500 text-sm">
                            across {stats.total_projects} projects
                        </div>
                    </div>

                    {/* Avg ROI - Purple */}
                    <div className="stat-card stat-card-purple hover-scale animate-fade-in-up stagger-3">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="stat-icon stat-icon-purple">
                                <TrendingUp size={22} />
                            </div>
                            <span className="text-zinc-400 text-sm font-medium">Avg ROI</span>
                        </div>
                        <div className="text-3xl font-bold text-white mb-1">
                            {stats.avg_roi_years}<span className="text-xl font-normal text-zinc-500"> yrs</span>
                        </div>
                        <div className="text-zinc-500 text-sm">
                            payback period
                        </div>
                    </div>

                    {/* CO2 Offset - Orange */}
                    <div className="stat-card stat-card-orange hover-scale animate-fade-in-up stagger-4">
                        <div className="flex items-center gap-3 mb-4">
                            <div className="stat-icon stat-icon-orange">
                                <Leaf size={22} />
                            </div>
                            <span className="text-zinc-400 text-sm font-medium">CO₂ Offset</span>
                        </div>
                        <div className="text-3xl font-bold text-white mb-1">
                            {(stats.co2_offset_kg / 1000).toFixed(1)}<span className="text-xl font-normal text-zinc-500"> T</span>
                        </div>
                        <div className="text-zinc-500 text-sm">
                            kg CO₂ per year
                        </div>
                    </div>
                </div>

                {/* Status Summary Cards */}
                <div className="grid grid-cols-1 md:grid-cols-3 gap-5 mb-10">
                    <div className="card-glow p-6 flex items-center gap-5 animate-fade-in-up stagger-1">
                        <div className="stat-icon stat-icon-green">
                            <CheckCircle size={24} />
                        </div>
                        <div>
                            <div className="text-3xl font-bold text-white">{stats.installed_count}</div>
                            <div className="text-zinc-400">Installed</div>
                        </div>
                    </div>
                    <div className="card-glow p-6 flex items-center gap-5 animate-fade-in-up stagger-2">
                        <div className="stat-icon stat-icon-yellow">
                            <Clock size={24} />
                        </div>
                        <div>
                            <div className="text-3xl font-bold text-white">{stats.pending_count}</div>
                            <div className="text-zinc-400">In Progress</div>
                        </div>
                    </div>
                    <div className="card-glow p-6 flex items-center gap-5 animate-fade-in-up stagger-3">
                        <div className="stat-icon stat-icon-red">
                            <AlertTriangle size={24} />
                        </div>
                        <div>
                            <div className="text-3xl font-bold text-white">3</div>
                            <div className="text-zinc-400">Need Attention</div>
                        </div>
                    </div>
                </div>

                {/* Projects Table */}
                <div className="card-glow p-6 animate-fade-in-up">
                    <div className="flex flex-col sm:flex-row justify-between items-start sm:items-center gap-4 mb-6">
                        <h3 className="text-xl font-semibold text-white">All Projects</h3>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 text-sm font-medium rounded-lg bg-violet-500/20 text-violet-300 border border-violet-500/30">
                                All
                            </button>
                            <button className="px-4 py-2 text-sm font-medium rounded-lg text-zinc-400 hover:bg-white/5 transition-colors">
                                Installed
                            </button>
                            <button className="px-4 py-2 text-sm font-medium rounded-lg text-zinc-400 hover:bg-white/5 transition-colors">
                                Pending
                            </button>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="table-premium">
                            <thead>
                                <tr>
                                    <th className="text-left">Project</th>
                                    <th className="text-left">Status</th>
                                    <th className="text-right">Annual Yield</th>
                                    <th className="text-right">Tank Size</th>
                                    <th className="text-left">Verification</th>
                                    <th></th>
                                </tr>
                            </thead>
                            <tbody>
                                {projects.map((project, index) => (
                                    <tr
                                        key={project.id}
                                        className="cursor-pointer"
                                        style={{ animationDelay: `${index * 50}ms` }}
                                    >
                                        <td>
                                            <div className="font-medium text-white">{project.address}</div>
                                            <div className="text-sm text-zinc-500">ID: {project.id}</div>
                                        </td>
                                        <td>{getStatusBadge(project.status)}</td>
                                        <td className="text-right font-semibold text-white">
                                            {(project.annual_yield_liters / 1000).toFixed(0)} kL
                                        </td>
                                        <td className="text-right text-zinc-400">
                                            {(project.tank_size_liters / 1000).toFixed(0)} kL
                                        </td>
                                        <td>{getStatusBadge(project.verification_status)}</td>
                                        <td>
                                            <button
                                                onClick={() => navigate(`/assess/${project.id}`)}
                                                className="p-2 rounded-lg text-zinc-500 hover:text-white hover:bg-white/10 transition-all"
                                            >
                                                <ChevronRight size={18} />
                                            </button>
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default PortfolioDashboard;
