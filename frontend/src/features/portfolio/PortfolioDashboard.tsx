import { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import {
    LayoutDashboard, Droplets, DollarSign, Users, TrendingUp,
    CheckCircle, Clock, AlertTriangle, ChevronRight, Download
} from 'lucide-react';
import axios from 'axios';

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

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'installed':
                return <span className="px-2 py-1 bg-green-500/20 text-green-400 rounded-full text-xs font-medium">Installed</span>;
            case 'pending':
                return <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded-full text-xs font-medium">Pending</span>;
            case 'verified':
                return <span className="px-2 py-1 bg-blue-500/20 text-blue-400 rounded-full text-xs font-medium">Verified</span>;
            default:
                return <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded-full text-xs font-medium">{status}</span>;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-12">
            <div className="max-w-7xl mx-auto px-4">
                {/* Header */}
                <div className="flex justify-between items-start mb-8">
                    <div>
                        <div className="inline-flex items-center gap-2 px-4 py-2 bg-indigo-500/10 border border-indigo-500/20 rounded-full mb-4">
                            <LayoutDashboard className="text-indigo-400" size={16} />
                            <span className="text-indigo-300 text-sm font-medium">Government Portal</span>
                        </div>
                        <h1 className="text-5xl font-black text-white mb-2">Portfolio Dashboard</h1>
                        <p className="text-gray-400">District-level RWH deployment overview</p>
                    </div>
                    <button className="px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl flex items-center gap-2 hover:scale-105 transition-transform">
                        <Download size={18} />
                        Export Report
                    </button>
                </div>

                {/* Key Stats */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-6 mb-8">
                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-cyan-500/20 rounded-lg">
                                <Droplets className="text-cyan-400" size={20} />
                            </div>
                            <span className="text-gray-400 font-medium text-sm">Water Captured</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {(stats.total_water_captured_liters / 1000000).toFixed(1)}M L
                        </div>
                        <div className="text-xs text-green-400 mt-1">+12% this quarter</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-green-500/20 rounded-lg">
                                <DollarSign className="text-green-400" size={20} />
                            </div>
                            <span className="text-gray-400 font-medium text-sm">Total Investment</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            ₹{(stats.total_investment_inr / 100000).toFixed(1)}L
                        </div>
                        <div className="text-xs text-gray-400 mt-1">across {stats.total_projects} projects</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-purple-500/20 rounded-lg">
                                <TrendingUp className="text-purple-400" size={20} />
                            </div>
                            <span className="text-gray-400 font-medium text-sm">Avg ROI</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {stats.avg_roi_years} yrs
                        </div>
                        <div className="text-xs text-gray-400 mt-1">payback period</div>
                    </div>

                    <div className="glass rounded-2xl p-6">
                        <div className="flex items-center gap-3 mb-3">
                            <div className="p-2 bg-yellow-500/20 rounded-lg">
                                <Users className="text-yellow-400" size={20} />
                            </div>
                            <span className="text-gray-400 font-medium text-sm">CO₂ Offset</span>
                        </div>
                        <div className="text-3xl font-black text-white">
                            {(stats.co2_offset_kg / 1000).toFixed(1)}T
                        </div>
                        <div className="text-xs text-gray-400 mt-1">kg CO₂ per year</div>
                    </div>
                </div>

                {/* Status Overview */}
                <div className="grid md:grid-cols-3 gap-6 mb-8">
                    <div className="glass rounded-2xl p-6 flex items-center gap-4">
                        <div className="p-3 bg-green-500/20 rounded-xl">
                            <CheckCircle className="text-green-400" size={28} />
                        </div>
                        <div>
                            <div className="text-3xl font-black text-white">{stats.installed_count}</div>
                            <div className="text-gray-400">Installed</div>
                        </div>
                    </div>
                    <div className="glass rounded-2xl p-6 flex items-center gap-4">
                        <div className="p-3 bg-yellow-500/20 rounded-xl">
                            <Clock className="text-yellow-400" size={28} />
                        </div>
                        <div>
                            <div className="text-3xl font-black text-white">{stats.pending_count}</div>
                            <div className="text-gray-400">Pending</div>
                        </div>
                    </div>
                    <div className="glass rounded-2xl p-6 flex items-center gap-4">
                        <div className="p-3 bg-orange-500/20 rounded-xl">
                            <AlertTriangle className="text-orange-400" size={28} />
                        </div>
                        <div>
                            <div className="text-3xl font-black text-white">3</div>
                            <div className="text-gray-400">Need Attention</div>
                        </div>
                    </div>
                </div>

                {/* Projects Table */}
                <div className="glass rounded-2xl p-6">
                    <div className="flex justify-between items-center mb-6">
                        <h3 className="text-xl font-bold text-white">All Projects</h3>
                        <div className="flex gap-2">
                            <button className="px-4 py-2 bg-white/10 hover:bg-white/20 text-white text-sm rounded-lg">All</button>
                            <button className="px-4 py-2 text-gray-400 hover:text-white text-sm rounded-lg">Installed</button>
                            <button className="px-4 py-2 text-gray-400 hover:text-white text-sm rounded-lg">Pending</button>
                        </div>
                    </div>

                    <div className="overflow-x-auto">
                        <table className="w-full">
                            <thead>
                                <tr className="text-left text-gray-400 border-b border-white/10">
                                    <th className="pb-4 font-medium">Project</th>
                                    <th className="pb-4 font-medium">Status</th>
                                    <th className="pb-4 font-medium text-right">Annual Yield</th>
                                    <th className="pb-4 font-medium text-right">Tank Size</th>
                                    <th className="pb-4 font-medium">Verification</th>
                                    <th className="pb-4"></th>
                                </tr>
                            </thead>
                            <tbody>
                                {projects.map((project) => (
                                    <tr key={project.id} className="border-b border-white/5 hover:bg-white/5 cursor-pointer">
                                        <td className="py-4">
                                            <div className="text-white font-medium">{project.address}</div>
                                            <div className="text-gray-500 text-sm">ID: {project.id}</div>
                                        </td>
                                        <td className="py-4">{getStatusBadge(project.status)}</td>
                                        <td className="py-4 text-right text-white font-semibold">
                                            {(project.annual_yield_liters / 1000).toFixed(0)} kL
                                        </td>
                                        <td className="py-4 text-right text-gray-300">
                                            {(project.tank_size_liters / 1000).toFixed(0)} kL
                                        </td>
                                        <td className="py-4">{getStatusBadge(project.verification_status)}</td>
                                        <td className="py-4">
                                            <button
                                                onClick={() => navigate(`/assess/${project.id}`)}
                                                className="p-2 hover:bg-white/10 rounded-lg text-gray-400 hover:text-white"
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
