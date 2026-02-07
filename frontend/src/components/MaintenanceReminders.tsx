/**
 * Maintenance Reminder Component
 * Scheduled tasks for RWH system upkeep
 */

import { useState } from 'react';
import {
    Wrench, Calendar, CheckCircle, AlertCircle, Clock,
    ChevronRight, Bell, Filter, Trash2, Droplets
} from 'lucide-react';

interface MaintenanceTask {
    id: string;
    title: string;
    description: string;
    frequency: string;
    lastDone: string | null;
    nextDue: string;
    status: 'overdue' | 'due-soon' | 'upcoming' | 'completed';
    priority: 'high' | 'medium' | 'low';
    estimatedTime: string;
    icon: string;
}

const MaintenanceReminders = () => {
    const [filter, setFilter] = useState<'all' | 'overdue' | 'upcoming'>('all');

    const tasks: MaintenanceTask[] = [
        {
            id: 'm1',
            title: 'Clean First-Flush Filter',
            description: 'Remove debris and wash the first-flush diverter',
            frequency: 'Monthly',
            lastDone: '2026-01-15',
            nextDue: '2026-02-15',
            status: 'due-soon',
            priority: 'high',
            estimatedTime: '15 mins',
            icon: '🔧'
        },
        {
            id: 'm2',
            title: 'Inspect Tank for Cracks',
            description: 'Check tank walls and base for any damage',
            frequency: 'Quarterly',
            lastDone: '2025-11-01',
            nextDue: '2026-02-01',
            status: 'overdue',
            priority: 'high',
            estimatedTime: '20 mins',
            icon: '🔍'
        },
        {
            id: 'm3',
            title: 'Clean Gutters',
            description: 'Remove leaves and debris from roof gutters',
            frequency: 'Before Monsoon',
            lastDone: '2025-06-01',
            nextDue: '2026-06-01',
            status: 'upcoming',
            priority: 'medium',
            estimatedTime: '45 mins',
            icon: '🍂'
        },
        {
            id: 'm4',
            title: 'Check Overflow Pipe',
            description: 'Ensure overflow pipe is clear and directing water properly',
            frequency: 'Monthly',
            lastDone: '2026-02-01',
            nextDue: '2026-03-01',
            status: 'completed',
            priority: 'low',
            estimatedTime: '10 mins',
            icon: '💧'
        },
        {
            id: 'm5',
            title: 'Test Water Quality',
            description: 'Check pH, TDS, and chlorine levels',
            frequency: 'Monthly',
            lastDone: '2026-01-20',
            nextDue: '2026-02-20',
            status: 'upcoming',
            priority: 'medium',
            estimatedTime: '5 mins',
            icon: '🧪'
        }
    ];

    const getStatusBadge = (status: string) => {
        switch (status) {
            case 'overdue':
                return <span className="px-2 py-1 text-xs rounded-full bg-red-500/20 text-red-400 flex items-center gap-1"><AlertCircle size={12} /> Overdue</span>;
            case 'due-soon':
                return <span className="px-2 py-1 text-xs rounded-full bg-yellow-500/20 text-yellow-400 flex items-center gap-1"><Clock size={12} /> Due Soon</span>;
            case 'completed':
                return <span className="px-2 py-1 text-xs rounded-full bg-green-500/20 text-green-400 flex items-center gap-1"><CheckCircle size={12} /> Done</span>;
            default:
                return <span className="px-2 py-1 text-xs rounded-full bg-gray-500/20 text-gray-400">Upcoming</span>;
        }
    };

    const getPriorityDot = (priority: string) => {
        switch (priority) {
            case 'high': return 'bg-red-500';
            case 'medium': return 'bg-yellow-500';
            default: return 'bg-green-500';
        }
    };

    const filteredTasks = tasks.filter(t => {
        if (filter === 'overdue') return t.status === 'overdue' || t.status === 'due-soon';
        if (filter === 'upcoming') return t.status === 'upcoming';
        return true;
    });

    const overdueCount = tasks.filter(t => t.status === 'overdue').length;
    const dueSoonCount = tasks.filter(t => t.status === 'due-soon').length;

    return (
        <div className="glass rounded-2xl p-6">
            {/* Header */}
            <div className="flex items-center justify-between mb-6">
                <div className="flex items-center gap-3">
                    <div className="p-3 bg-gradient-to-r from-orange-500 to-red-500 rounded-xl">
                        <Wrench className="text-white" size={24} />
                    </div>
                    <div>
                        <h3 className="text-xl font-bold text-white">Maintenance Schedule</h3>
                        <p className="text-gray-400 text-sm">Keep your RWH system in top shape</p>
                    </div>
                </div>
                <button className="flex items-center gap-2 px-4 py-2 bg-orange-500 text-white rounded-xl font-medium hover:bg-orange-600 transition-colors">
                    <Bell size={16} />
                    Set Reminders
                </button>
            </div>

            {/* Alert Banner */}
            {(overdueCount > 0 || dueSoonCount > 0) && (
                <div className="bg-gradient-to-r from-red-500/10 to-orange-500/10 border border-red-500/20 rounded-xl p-4 mb-6">
                    <div className="flex items-center gap-3">
                        <AlertCircle className="text-red-400" size={24} />
                        <div>
                            <div className="text-white font-medium">
                                {overdueCount > 0 && <span className="text-red-400">{overdueCount} overdue</span>}
                                {overdueCount > 0 && dueSoonCount > 0 && ' • '}
                                {dueSoonCount > 0 && <span className="text-yellow-400">{dueSoonCount} due soon</span>}
                            </div>
                            <div className="text-gray-400 text-sm">Complete these tasks to maintain system efficiency</div>
                        </div>
                    </div>
                </div>
            )}

            {/* Filter Tabs */}
            <div className="flex gap-2 mb-4">
                {(['all', 'overdue', 'upcoming'] as const).map(f => (
                    <button
                        key={f}
                        onClick={() => setFilter(f)}
                        className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${filter === f
                                ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30'
                                : 'bg-white/5 text-gray-400 hover:text-white'
                            }`}
                    >
                        {f.charAt(0).toUpperCase() + f.slice(1)}
                        {f === 'overdue' && overdueCount > 0 && (
                            <span className="ml-2 bg-red-500 text-white text-xs px-1.5 py-0.5 rounded-full">
                                {overdueCount + dueSoonCount}
                            </span>
                        )}
                    </button>
                ))}
            </div>

            {/* Task List */}
            <div className="space-y-3">
                {filteredTasks.map((task) => (
                    <div
                        key={task.id}
                        className={`p-4 rounded-xl border transition-all hover:bg-white/5 ${task.status === 'overdue'
                                ? 'bg-red-500/5 border-red-500/20'
                                : task.status === 'due-soon'
                                    ? 'bg-yellow-500/5 border-yellow-500/20'
                                    : 'bg-white/5 border-white/10'
                            }`}
                    >
                        <div className="flex items-start gap-4">
                            <div className="text-3xl">{task.icon}</div>
                            <div className="flex-1">
                                <div className="flex items-center gap-2 mb-1">
                                    <div className={`w-2 h-2 rounded-full ${getPriorityDot(task.priority)}`} />
                                    <h4 className="text-white font-semibold">{task.title}</h4>
                                    {getStatusBadge(task.status)}
                                </div>
                                <p className="text-gray-400 text-sm mb-2">{task.description}</p>
                                <div className="flex items-center gap-4 text-xs text-gray-500">
                                    <span className="flex items-center gap-1">
                                        <Calendar size={12} />
                                        {task.frequency}
                                    </span>
                                    <span className="flex items-center gap-1">
                                        <Clock size={12} />
                                        {task.estimatedTime}
                                    </span>
                                    <span>Next: {new Date(task.nextDue).toLocaleDateString()}</span>
                                </div>
                            </div>
                            <button className={`px-4 py-2 rounded-xl text-sm font-medium transition-all ${task.status === 'completed'
                                    ? 'bg-green-500/20 text-green-400'
                                    : 'bg-white/10 text-white hover:bg-orange-500'
                                }`}>
                                {task.status === 'completed' ? 'Done ✓' : 'Mark Done'}
                            </button>
                        </div>
                    </div>
                ))}
            </div>

            {/* Quick Tips */}
            <div className="mt-6 p-4 bg-cyan-500/10 border border-cyan-500/20 rounded-xl">
                <div className="flex items-center gap-2 text-cyan-400 font-medium mb-2">
                    <Droplets size={16} />
                    Pro Tip
                </div>
                <p className="text-gray-300 text-sm">
                    Regular maintenance can increase your water collection efficiency by up to 30%!
                    Set monthly reminders to never miss a task.
                </p>
            </div>
        </div>
    );
};

export default MaintenanceReminders;
