/**
 * Project History Page
 * View all past assessments and projects
 */

import { useState } from 'react';
import { Link } from 'react-router-dom';
import {
    History, Search, Filter, Download, ChevronRight, Calendar,
    MapPin, Droplets, DollarSign, CheckCircle, Clock, AlertCircle
} from 'lucide-react';

interface Project {
    id: string;
    name: string;
    address: string;
    date: string;
    roofArea: number;
    tankSize: number;
    annualYield: number;
    estimatedSavings: number;
    status: 'completed' | 'in-progress' | 'pending';
    subsidyStatus?: 'approved' | 'pending' | 'rejected';
}

const ProjectHistoryPage = () => {
    const [searchQuery, setSearchQuery] = useState('');
    const [statusFilter, setStatusFilter] = useState<string>('all');

    // Demo data
    const projects: Project[] = [
        {
            id: 'proj-001',
            name: 'Home RWH System',
            address: '42, Green Valley, Bangalore',
            date: '2026-01-15',
            roofArea: 150,
            tankSize: 5000,
            annualYield: 120000,
            estimatedSavings: 15600,
            status: 'completed',
            subsidyStatus: 'approved'
        },
        {
            id: 'proj-002',
            name: 'Office Building',
            address: 'Tech Park, Whitefield',
            date: '2026-01-28',
            roofArea: 500,
            tankSize: 20000,
            annualYield: 400000,
            estimatedSavings: 52000,
            status: 'in-progress',
            subsidyStatus: 'pending'
        },
        {
            id: 'proj-003',
            name: 'Community Center',
            address: 'HSR Layout',
            date: '2026-02-05',
            roofArea: 300,
            tankSize: 10000,
            annualYield: 240000,
            estimatedSavings: 31200,
            status: 'pending'
        }
    ];

    const filteredProjects = projects.filter(p => {
        const matchesSearch = p.name.toLowerCase().includes(searchQuery.toLowerCase()) ||
            p.address.toLowerCase().includes(searchQuery.toLowerCase());
        const matchesStatus = statusFilter === 'all' || p.status === statusFilter;
        return matchesSearch && matchesStatus;
    });

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'completed':
                return <span className="flex items-center gap-1 text-green-400 bg-green-400/10 px-2 py-1 rounded-full text-xs"><CheckCircle size={12} />Completed</span>;
            case 'in-progress':
                return <span className="flex items-center gap-1 text-yellow-400 bg-yellow-400/10 px-2 py-1 rounded-full text-xs"><Clock size={12} />In Progress</span>;
            case 'pending':
                return <span className="flex items-center gap-1 text-gray-400 bg-gray-400/10 px-2 py-1 rounded-full text-xs"><AlertCircle size={12} />Pending</span>;
            default:
                return null;
        }
    };

    const getSubsidyBadge = (status?: string) => {
        switch (status) {
            case 'approved':
                return <span className="text-green-400 text-xs">Subsidy ✓</span>;
            case 'pending':
                return <span className="text-yellow-400 text-xs">Subsidy Pending</span>;
            case 'rejected':
                return <span className="text-red-400 text-xs">Subsidy Rejected</span>;
            default:
                return null;
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="flex flex-col md:flex-row justify-between items-start md:items-center gap-4">
                    <div className="flex items-center gap-3">
                        <div className="p-3 bg-gradient-to-r from-purple-500 to-pink-500 rounded-2xl">
                            <History className="text-white" size={28} />
                        </div>
                        <div>
                            <h1 className="text-3xl font-black text-white">Project History</h1>
                            <p className="text-gray-400">View all your RWH assessments and projects</p>
                        </div>
                    </div>
                    <Link
                        to="/intake"
                        className="px-5 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-semibold rounded-xl hover:opacity-90 transition-opacity"
                    >
                        + New Assessment
                    </Link>
                </div>

                {/* Filters */}
                <div className="flex flex-col sm:flex-row gap-4">
                    <div className="relative flex-1">
                        <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={18} />
                        <input
                            type="text"
                            placeholder="Search projects..."
                            value={searchQuery}
                            onChange={(e) => setSearchQuery(e.target.value)}
                            className="w-full pl-12 pr-4 py-3 bg-white/5 border border-white/10 rounded-xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500"
                        />
                    </div>
                    <div className="flex gap-2">
                        {['all', 'completed', 'in-progress', 'pending'].map(status => (
                            <button
                                key={status}
                                onClick={() => setStatusFilter(status)}
                                className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${statusFilter === status
                                        ? 'bg-cyan-500 text-white'
                                        : 'bg-white/5 text-gray-400 hover:text-white'
                                    }`}
                            >
                                {status === 'all' ? 'All' : status.replace('-', ' ').replace(/\b\w/g, l => l.toUpperCase())}
                            </button>
                        ))}
                    </div>
                </div>

                {/* Projects List */}
                <div className="space-y-4">
                    {filteredProjects.length === 0 ? (
                        <div className="glass rounded-2xl p-12 text-center">
                            <History className="text-gray-500 mx-auto mb-4" size={48} />
                            <p className="text-gray-400">No projects found</p>
                        </div>
                    ) : (
                        filteredProjects.map(project => (
                            <Link
                                key={project.id}
                                to={`/assess/${project.id}`}
                                className="glass rounded-2xl p-6 flex flex-col md:flex-row gap-4 hover:border-cyan-500/30 border-2 border-transparent transition-all group"
                            >
                                <div className="flex-1">
                                    <div className="flex items-center gap-3 mb-2">
                                        <h3 className="text-lg font-bold text-white">{project.name}</h3>
                                        {getStatusBadge(project.status)}
                                        {getSubsidyBadge(project.subsidyStatus)}
                                    </div>
                                    <div className="flex flex-wrap gap-4 text-sm text-gray-400">
                                        <span className="flex items-center gap-1">
                                            <MapPin size={14} /> {project.address}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Calendar size={14} /> {new Date(project.date).toLocaleDateString()}
                                        </span>
                                    </div>
                                </div>

                                <div className="flex gap-6 items-center">
                                    <div className="text-center">
                                        <div className="text-cyan-400 font-bold">{project.roofArea} m²</div>
                                        <div className="text-gray-500 text-xs">Roof Area</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-blue-400 font-bold">{(project.annualYield / 1000).toFixed(0)}k L</div>
                                        <div className="text-gray-500 text-xs">Annual Yield</div>
                                    </div>
                                    <div className="text-center">
                                        <div className="text-green-400 font-bold">₹{project.estimatedSavings.toLocaleString()}</div>
                                        <div className="text-gray-500 text-xs">Savings/Year</div>
                                    </div>
                                    <ChevronRight className="text-gray-500 group-hover:text-cyan-400 transition-colors" size={20} />
                                </div>
                            </Link>
                        ))
                    )}
                </div>

                {/* Summary */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-lg font-bold text-white mb-4">Summary</h3>
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-2xl font-bold text-white">{projects.length}</div>
                            <div className="text-gray-400 text-sm">Total Projects</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-2xl font-bold text-cyan-400">
                                {projects.reduce((sum, p) => sum + p.roofArea, 0)} m²
                            </div>
                            <div className="text-gray-400 text-sm">Total Roof Area</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-2xl font-bold text-blue-400">
                                {(projects.reduce((sum, p) => sum + p.annualYield, 0) / 1000).toFixed(0)}k L
                            </div>
                            <div className="text-gray-400 text-sm">Potential Yield</div>
                        </div>
                        <div className="bg-white/5 rounded-xl p-4 text-center">
                            <div className="text-2xl font-bold text-green-400">
                                ₹{projects.reduce((sum, p) => sum + p.estimatedSavings, 0).toLocaleString()}
                            </div>
                            <div className="text-gray-400 text-sm">Total Savings</div>
                        </div>
                    </div>
                </div>
            </div>
        </div>
    );
};

export default ProjectHistoryPage;
