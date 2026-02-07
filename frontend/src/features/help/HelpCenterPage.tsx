/**
 * Help Center / Education Page
 * FAQs, tutorials, and maintenance guides
 */

import { useState } from 'react';
import {
    HelpCircle, BookOpen, Video, Wrench, ChevronDown, ChevronRight,
    Search, MessageCircle, Phone, Mail, ExternalLink, Play,
    Droplets, Filter, AlertTriangle, CheckCircle, Clock
} from 'lucide-react';

interface FAQ {
    question: string;
    answer: string;
    category: string;
}

interface Tutorial {
    id: string;
    title: string;
    duration: string;
    thumbnail: string;
    type: 'video' | 'article';
}

interface MaintenanceTask {
    id: string;
    title: string;
    frequency: string;
    difficulty: 'easy' | 'medium' | 'hard';
    estimatedTime: string;
    steps: string[];
    completed?: boolean;
}

const HelpCenterPage = () => {
    const [activeTab, setActiveTab] = useState<'faq' | 'tutorials' | 'maintenance' | 'contact'>('faq');
    const [searchQuery, setSearchQuery] = useState('');
    const [expandedFaq, setExpandedFaq] = useState<string | null>(null);
    const [expandedTask, setExpandedTask] = useState<string | null>(null);
    const [showConfetti, setShowConfetti] = useState(false);

    const faqs: FAQ[] = [
        {
            question: 'What is rainwater harvesting?',
            answer: 'Rainwater harvesting is the collection and storage of rainwater that falls on roofs, which can then be used for various purposes like gardening, flushing toilets, washing clothes, and with proper filtration, even drinking. It helps reduce water bills and dependence on municipal water supply.',
            category: 'Basics'
        },
        {
            question: 'How much water can I collect from my roof?',
            answer: 'The amount depends on your roof area, annual rainfall, and roof material. Use our formula: Annual Yield = Roof Area (m²) × Rainfall (mm) × Runoff Coefficient (0.8-0.9) × Collection Efficiency (0.9). For a 100m² roof with 800mm annual rainfall, you can collect approximately 65,000 liters per year!',
            category: 'Basics'
        },
        {
            question: 'What size tank do I need?',
            answer: 'Tank size depends on your daily usage and dry spell duration. A general formula: Tank Size = Daily Usage × Number of Dry Days. For a family of 4 using 135L/person/day with 60 dry days consideration, you would need about 16,000-20,000 liters capacity.',
            category: 'Sizing'
        },
        {
            question: 'Is rainwater safe to drink?',
            answer: 'Rainwater can be made safe for drinking with proper filtration and treatment. This includes first flush diverters, mesh filters, sediment filters, activated carbon filters, and UV treatment. For non-potable uses like gardening and flushing, basic filtration is sufficient.',
            category: 'Safety'
        },
        {
            question: 'What government subsidies are available?',
            answer: 'Many Indian states offer subsidies for RWH installation: Delhi (up to ₹50,000), Tamil Nadu (up to 50% subsidy), Karnataka (tax rebates), Maharashtra (property tax discounts). Enter your location in RainForge to see exact subsidies available to you.',
            category: 'Subsidies'
        },
        {
            question: 'How often should I maintain my RWH system?',
            answer: 'Regular maintenance includes: Monthly - check gutters for debris; Quarterly - clean first flush diverter and filters; Annually - inspect tank, clean thoroughly, check pipes. After heavy storms, always inspect for accumulated debris.',
            category: 'Maintenance'
        },
        {
            question: 'Can I connect RWH to my existing plumbing?',
            answer: 'Yes, but it requires careful planning. You need a separate pipe system for rainwater to avoid cross-contamination with municipal supply. Many homeowners use rainwater for garden taps, toilet flushing, and washing machines through dedicated lines.',
            category: 'Installation'
        },
        {
            question: 'What is a first flush diverter?',
            answer: 'A first flush diverter diverts the first few liters of rainfall away from your tank. This "first flush" contains the most contaminants (dust, bird droppings, pollutants) accumulated on your roof. After diversion, cleaner water flows to your storage tank.',
            category: 'Components'
        },
    ];

    const tutorials: Tutorial[] = [
        { id: 't1', title: 'Complete Guide to RWH Installation', duration: '15 min', thumbnail: '🏠', type: 'video' },
        { id: 't2', title: 'Choosing the Right Tank Material', duration: '8 min', thumbnail: '🪣', type: 'video' },
        { id: 't3', title: 'DIY First Flush Diverter', duration: '12 min', thumbnail: '🔧', type: 'video' },
        { id: 't4', title: 'Water Quality Testing at Home', duration: '10 min', thumbnail: '🧪', type: 'video' },
        { id: 't5', title: 'Connecting RWH to Irrigation System', duration: '20 min', thumbnail: '🌱', type: 'article' },
        { id: 't6', title: 'Government Subsidy Application Guide', duration: '5 min', thumbnail: '📋', type: 'article' },
    ];

    const [tasks, setTasks] = useState<MaintenanceTask[]>([
        {
            id: 'm1',
            title: 'Clean Gutters and Downpipes',
            frequency: 'Monthly',
            difficulty: 'easy',
            estimatedTime: '30 mins',
            steps: [
                'Wear safety gloves and use a stable ladder',
                'Remove leaves, twigs, and debris from gutters',
                'Flush downpipes with water to check flow',
                'Check for any leaks or damage',
                'Clear any blockages in mesh filters'
            ],
            completed: false
        },
        {
            id: 'm2',
            title: 'Service First Flush Diverter',
            frequency: 'Quarterly',
            difficulty: 'easy',
            estimatedTime: '20 mins',
            steps: [
                'Open the diverter chamber',
                'Empty accumulated dirty water',
                'Clean the chamber with fresh water',
                'Check the ball valve mechanism',
                'Ensure proper sealing when closed'
            ],
            completed: false
        },
        {
            id: 'm3',
            title: 'Clean Storage Tank',
            frequency: 'Annually',
            difficulty: 'medium',
            estimatedTime: '2-3 hours',
            steps: [
                'Drain the tank completely (use water for garden)',
                'Enter tank (if safe) or use long brush',
                'Scrub walls and floor to remove sediment',
                'Rinse thoroughly with clean water',
                'Check for cracks or leaks',
                'Allow to dry before refilling'
            ],
            completed: false
        },
        {
            id: 'm4',
            title: 'Replace Filters',
            frequency: 'Every 6 months',
            difficulty: 'easy',
            estimatedTime: '15 mins',
            steps: [
                'Turn off water supply to filter housing',
                'Remove old filter cartridge',
                'Clean filter housing if needed',
                'Insert new filter (note flow direction)',
                'Turn on supply and check for leaks'
            ],
            completed: false
        },
    ]);

    const toggleTaskCompletion = (taskId: string) => {
        setTasks(tasks.map(task =>
            task.id === taskId ? { ...task, completed: !task.completed } : task
        ));
        setShowConfetti(true);
        setTimeout(() => setShowConfetti(false), 3000);
    };

    const filteredFaqs = faqs.filter(faq =>
        faq.question.toLowerCase().includes(searchQuery.toLowerCase()) ||
        faq.answer.toLowerCase().includes(searchQuery.toLowerCase())
    );

    const getDifficultyColor = (difficulty: string) => {
        switch (difficulty) {
            case 'easy': return 'text-green-400 bg-green-400/10';
            case 'medium': return 'text-yellow-400 bg-yellow-400/10';
            case 'hard': return 'text-red-400 bg-red-400/10';
            default: return 'text-gray-400 bg-gray-400/10';
        }
    };

    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 py-8">
            <div className="max-w-5xl mx-auto px-4 sm:px-6 lg:px-8 space-y-6">

                {/* Header */}
                <div className="text-center mb-8">
                    <div className="inline-flex items-center gap-3 mb-4">
                        <div className="p-3 bg-gradient-to-r from-green-500 to-emerald-500 rounded-2xl">
                            <HelpCircle className="text-white" size={32} />
                        </div>
                        <h1 className="text-4xl font-black text-white">Help Center</h1>
                    </div>
                    <p className="text-gray-400 text-lg">Learn, maintain, and get support for your RWH system</p>
                </div>

                {/* Search */}
                <div className="relative max-w-2xl mx-auto">
                    <Search className="absolute left-4 top-1/2 -translate-y-1/2 text-gray-400" size={20} />
                    <input
                        type="text"
                        placeholder="Search for help..."
                        value={searchQuery}
                        onChange={(e) => setSearchQuery(e.target.value)}
                        className="w-full pl-12 pr-4 py-4 bg-white/5 border border-white/10 rounded-2xl text-white placeholder-gray-500 focus:outline-none focus:border-cyan-500 text-lg"
                    />
                </div>

                {/* Tabs */}
                <div className="flex flex-wrap gap-2 justify-center">
                    {[
                        { id: 'faq', label: 'FAQs', icon: HelpCircle },
                        { id: 'tutorials', label: 'Tutorials', icon: Video },
                        { id: 'maintenance', label: 'Maintenance', icon: Wrench },
                        { id: 'contact', label: 'Contact', icon: MessageCircle },
                    ].map(tab => (
                        <button
                            key={tab.id}
                            onClick={() => setActiveTab(tab.id as typeof activeTab)}
                            className={`flex items-center gap-2 px-5 py-3 rounded-xl font-medium transition-all ${activeTab === tab.id
                                ? 'bg-gradient-to-r from-cyan-500 to-blue-500 text-white'
                                : 'bg-white/5 text-gray-400 hover:text-white'
                                }`}
                        >
                            <tab.icon size={18} />
                            {tab.label}
                        </button>
                    ))}
                </div>

                {/* FAQs */}
                {activeTab === 'faq' && (
                    <div className="glass rounded-2xl overflow-hidden">
                        <div className="p-4 border-b border-white/10">
                            <h3 className="text-lg font-bold text-white">Frequently Asked Questions</h3>
                        </div>
                        <div className="divide-y divide-white/5">
                            {filteredFaqs.map((faq, idx) => (
                                <div key={idx} className="p-4">
                                    <button
                                        onClick={() => setExpandedFaq(expandedFaq === faq.question ? null : faq.question)}
                                        className="w-full flex items-start gap-3 text-left"
                                    >
                                        <div className={`mt-1 transition-transform ${expandedFaq === faq.question ? 'rotate-90' : ''}`}>
                                            <ChevronRight className="text-cyan-400" size={18} />
                                        </div>
                                        <div className="flex-1">
                                            <div className="text-white font-medium">{faq.question}</div>
                                            <span className="text-xs text-gray-500 bg-white/5 px-2 py-0.5 rounded-full mt-1 inline-block">
                                                {faq.category}
                                            </span>
                                        </div>
                                    </button>
                                    {expandedFaq === faq.question && (
                                        <div className="mt-3 ml-7 text-gray-400 leading-relaxed animate-fadeIn">
                                            {faq.answer}
                                        </div>
                                    )}
                                </div>
                            ))}
                        </div>
                    </div>
                )}

                {/* Tutorials */}
                {activeTab === 'tutorials' && (
                    <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-4">
                        {tutorials.map(tutorial => (
                            <div key={tutorial.id} className="glass rounded-2xl overflow-hidden hover:border-cyan-500/30 border-2 border-transparent transition-all cursor-pointer group">
                                <div className="aspect-video bg-gradient-to-br from-slate-700 to-slate-800 flex items-center justify-center relative">
                                    <span className="text-6xl">{tutorial.thumbnail}</span>
                                    {tutorial.type === 'video' && (
                                        <div className="absolute inset-0 flex items-center justify-center bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity">
                                            <div className="w-16 h-16 rounded-full bg-white/20 backdrop-blur flex items-center justify-center">
                                                <Play className="text-white ml-1" size={28} fill="white" />
                                            </div>
                                        </div>
                                    )}
                                </div>
                                <div className="p-4">
                                    <h4 className="text-white font-semibold mb-2">{tutorial.title}</h4>
                                    <div className="flex items-center gap-3 text-sm text-gray-500">
                                        <span className="flex items-center gap-1">
                                            {tutorial.type === 'video' ? <Video size={14} /> : <BookOpen size={14} />}
                                            {tutorial.type === 'video' ? 'Video' : 'Article'}
                                        </span>
                                        <span className="flex items-center gap-1">
                                            <Clock size={14} />
                                            {tutorial.duration}
                                        </span>
                                    </div>
                                </div>
                            </div>
                        ))}
                    </div>
                )}

                {/* Maintenance */}
                {activeTab === 'maintenance' && (
                    <div className="space-y-4">
                        {/* Reminder Banner */}
                        <div className="glass rounded-2xl p-4 bg-yellow-500/10 border border-yellow-500/30 flex items-center gap-4">
                            <AlertTriangle className="text-yellow-400 flex-shrink-0" size={24} />
                            <div>
                                <p className="text-white font-semibold">Maintenance Reminder</p>
                                <p className="text-yellow-400 text-sm">Your gutter cleaning is overdue by 5 days</p>
                            </div>
                            <button className="ml-auto px-4 py-2 bg-yellow-500 text-black font-semibold rounded-lg hover:bg-yellow-400 transition-colors">
                                Mark Done
                            </button>
                        </div>

                        {/* Tasks */}
                        {tasks.map(task => (
                            <div key={task.id} className={`glass rounded-2xl overflow-hidden transition-all ${task.completed ? 'opacity-70' : ''}`}>
                                <button
                                    onClick={() => setExpandedTask(expandedTask === task.id ? null : task.id)}
                                    className="w-full p-4 flex items-center gap-4"
                                >
                                    <div className={`p-3 rounded-xl transition-colors ${task.completed ? 'bg-green-500/20' : 'bg-cyan-500/20'}`}>
                                        {task.completed ? <CheckCircle className="text-green-400" size={24} /> : <Wrench className="text-cyan-400" size={24} />}
                                    </div>
                                    <div className="flex-1 text-left">
                                        <h4 className={`text-white font-semibold flex items-center gap-2 ${task.completed ? 'line-through text-gray-400' : ''}`}>
                                            {task.title}
                                            {task.completed && <span className="text-xs no-underline bg-green-500/20 text-green-400 px-2 py-0.5 rounded-full">Completed</span>}
                                        </h4>
                                        <div className="flex flex-wrap gap-2 mt-1">
                                            <span className="text-xs text-gray-400 bg-white/5 px-2 py-0.5 rounded-full flex items-center gap-1">
                                                <Clock size={10} /> {task.frequency}
                                            </span>
                                            <span className={`text-xs px-2 py-0.5 rounded-full ${getDifficultyColor(task.difficulty)}`}>
                                                {task.difficulty}
                                            </span>
                                            <span className="text-xs text-gray-400 bg-white/5 px-2 py-0.5 rounded-full">
                                                ~{task.estimatedTime}
                                            </span>
                                        </div>
                                    </div>
                                    <ChevronDown className={`text-gray-400 transition-transform ${expandedTask === task.id ? 'rotate-180' : ''}`} size={20} />
                                </button>

                                {expandedTask === task.id && (
                                    <div className="px-4 pb-4 animate-fadeIn">
                                        <div className="bg-white/5 rounded-xl p-4">
                                            <h5 className="text-white font-medium mb-3">Steps:</h5>
                                            <ol className="space-y-2">
                                                {task.steps.map((step, idx) => (
                                                    <li key={idx} className="flex items-start gap-3">
                                                        <span className={`w-6 h-6 rounded-full text-xs flex items-center justify-center flex-shrink-0 ${task.completed ? 'bg-green-500/20 text-green-400' : 'bg-cyan-500/20 text-cyan-400'}`}>
                                                            {idx + 1}
                                                        </span>
                                                        <span className="text-gray-400">{step}</span>
                                                    </li>
                                                ))}
                                            </ol>
                                            <button
                                                onClick={() => toggleTaskCompletion(task.id)}
                                                className={`mt-4 w-full py-2 rounded-lg font-medium flex items-center justify-center gap-2 transition-colors ${task.completed
                                                        ? 'bg-red-500/20 text-red-400 hover:bg-red-500/30'
                                                        : 'bg-green-500/20 text-green-400 hover:bg-green-500/30'
                                                    }`}
                                            >
                                                {task.completed ? (
                                                    <>
                                                        <AlertTriangle size={18} /> Mark as Incomplete
                                                    </>
                                                ) : (
                                                    <>
                                                        <CheckCircle size={18} /> Mark as Completed
                                                    </>
                                                )}
                                            </button>
                                        </div>
                                    </div>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                {/* Contact */}
                {activeTab === 'contact' && (
                    <div className="grid md:grid-cols-2 gap-6">
                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-4">Get in Touch</h3>
                            <div className="space-y-4">
                                <a href="tel:1800-123-4567" className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                                    <Phone className="text-green-400" size={24} />
                                    <div>
                                        <div className="text-white font-medium">Call Us</div>
                                        <div className="text-gray-400">1800-123-4567 (Toll Free)</div>
                                    </div>
                                </a>
                                <a href="mailto:support@rainforge.in" className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                                    <Mail className="text-cyan-400" size={24} />
                                    <div>
                                        <div className="text-white font-medium">Email Support</div>
                                        <div className="text-gray-400">support@rainforge.in</div>
                                    </div>
                                </a>
                                <a href="#" className="flex items-center gap-4 p-4 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                                    <MessageCircle className="text-purple-400" size={24} />
                                    <div>
                                        <div className="text-white font-medium">Live Chat</div>
                                        <div className="text-gray-400">Available 9 AM - 6 PM</div>
                                    </div>
                                </a>
                            </div>
                        </div>

                        <div className="glass rounded-2xl p-6">
                            <h3 className="text-lg font-bold text-white mb-4">Quick Links</h3>
                            <div className="space-y-3">
                                {[
                                    { label: 'Report a Bug', icon: AlertTriangle },
                                    { label: 'Request a Feature', icon: Droplets },
                                    { label: 'API Documentation', icon: BookOpen },
                                    { label: 'Partner with Us', icon: ExternalLink },
                                ].map((link, idx) => (
                                    <a key={idx} href="#" className="flex items-center gap-3 p-3 bg-white/5 rounded-xl hover:bg-white/10 transition-colors">
                                        <link.icon className="text-gray-400" size={18} />
                                        <span className="text-white">{link.label}</span>
                                        <ChevronRight className="text-gray-500 ml-auto" size={16} />
                                    </a>
                                ))}
                            </div>
                        </div>
                    </div>
                )}
            </div>
        </div>
    );
};

export default HelpCenterPage;
