import { Link } from 'react-router-dom';
import {
    Droplets, ArrowRight, Shield,
    FileSpreadsheet, Activity, Camera, LayoutDashboard,
    Building2, Zap
} from 'lucide-react';

const LandingPage = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">
            {/* Nav */}
            <nav className="max-w-7xl mx-auto px-4 py-6 flex justify-between items-center">
                <div className="flex items-center gap-3">
                    <Droplets className="h-10 w-10 text-cyan-400" />
                    <span className="text-2xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">
                        RainForge
                    </span>
                    <span className="text-xs bg-indigo-500/20 text-indigo-300 px-2 py-1 rounded-full border border-indigo-500/30">
                        Government Edition
                    </span>
                    <span className="hidden md:inline-block text-xs text-gray-500 ml-2">
                        | Made by <span className="text-cyan-400 font-medium">Prashant Mishra</span> & <span className="text-purple-400 font-medium">Ishita Parmar</span>
                    </span>
                </div>
                <div className="hidden md:flex items-center gap-6">
                    <Link to="/portfolio" className="text-gray-300 hover:text-white font-medium">Dashboard</Link>
                    <Link to="/bulk" className="text-gray-300 hover:text-white font-medium">Bulk Upload</Link>
                    <Link to="/intake" className="px-6 py-2 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-lg hover:scale-105 transition-transform">
                        Start Assessment
                    </Link>
                </div>
            </nav>

            {/* Hero */}
            <section className="max-w-7xl mx-auto px-4 py-20 text-center">
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-green-500/10 border border-green-500/20 rounded-full mb-4">
                    <Shield className="text-green-400" size={16} />
                    <span className="text-green-300 text-sm font-medium">Jal Shakti Abhiyan Aligned</span>
                </div>
                <div className="mb-8">
                    <span className="text-sm text-gray-400">Made by </span>
                    <span className="text-sm font-semibold text-cyan-400">Prashant Mishra</span>
                    <span className="text-sm text-gray-400"> & </span>
                    <span className="text-sm font-semibold text-purple-400">Ishita Parmar</span>
                </div>

                <h1 className="text-6xl md:text-7xl font-black text-white mb-6 leading-tight">
                    Rainwater Harvesting<br />
                    <span className="bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 animate-gradient">
                        at National Scale
                    </span>
                </h1>

                <p className="text-xl text-gray-300 max-w-3xl mx-auto mb-10">
                    AI-powered platform for government-grade RWH planning, deployment, verification, and impact reporting.
                    From 1 rooftop to 10,000 buildings — RainForge scales with you.
                </p>

                <div className="flex flex-col sm:flex-row gap-4 justify-center">
                    <Link
                        to="/intake"
                        className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl text-lg hover:scale-105 transition-transform shadow-2xl hover:shadow-cyan-500/50 flex items-center justify-center gap-2"
                    >
                        Single Site Assessment
                        <ArrowRight size={20} />
                    </Link>
                    <Link
                        to="/bulk"
                        className="px-8 py-4 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl text-lg border border-white/20 flex items-center justify-center gap-2"
                    >
                        <FileSpreadsheet size={20} />
                        Bulk / City Mode
                    </Link>
                </div>
            </section>

            {/* Stats */}
            <section className="max-w-7xl mx-auto px-4 py-16">
                <div className="glass rounded-3xl p-8 grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                    <div>
                        <div className="text-4xl font-black text-cyan-400">50K+</div>
                        <div className="text-gray-400 mt-1">Sites Assessed</div>
                    </div>
                    <div>
                        <div className="text-4xl font-black text-green-400">2.5B L</div>
                        <div className="text-gray-400 mt-1">Water Potential Found</div>
                    </div>
                    <div>
                        <div className="text-4xl font-black text-purple-400">12</div>
                        <div className="text-gray-400 mt-1">States Onboarded</div>
                    </div>
                    <div>
                        <div className="text-4xl font-black text-yellow-400">₹850Cr</div>
                        <div className="text-gray-400 mt-1">Investment Planned</div>
                    </div>
                </div>
            </section>

            {/* Platform Features */}
            <section className="max-w-7xl mx-auto px-4 py-16">
                <h2 className="text-4xl font-black text-white text-center mb-4">
                    Complete Platform
                </h2>
                <p className="text-gray-400 text-center mb-12 max-w-2xl mx-auto">
                    Everything you need to plan, deploy, verify, and monitor RWH systems at scale
                </p>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
                    {[
                        {
                            icon: Zap,
                            title: "Scenario Modes",
                            desc: "Cost-Optimized, Max Capture, or Dry-Season reliability modes",
                            color: "cyan"
                        },
                        {
                            icon: FileSpreadsheet,
                            title: "Bulk Upload",
                            desc: "CSV upload for 10,000+ sites with automatic batch processing",
                            color: "green"
                        },
                        {
                            icon: LayoutDashboard,
                            title: "Portfolio View",
                            desc: "District-level dashboard with aggregate KPIs and trends",
                            color: "purple"
                        },
                        {
                            icon: Camera,
                            title: "Verification",
                            desc: "Photo uploads with geo-tagging for installation proof",
                            color: "pink"
                        },
                        {
                            icon: Activity,
                            title: "Live Monitoring",
                            desc: "IoT-ready tank levels, predictions, and maintenance alerts",
                            color: "yellow"
                        },
                        {
                            icon: Building2,
                            title: "Policy Compliance",
                            desc: "State-wise subsidy eligibility and compliance scoring",
                            color: "indigo"
                        }
                    ].map((feature, i) => (
                        <div key={i} className="glass rounded-2xl p-6 hover:scale-105 transition-transform">
                            <div className={`p-3 bg-${feature.color}-500/20 rounded-xl w-fit mb-4`}>
                                <feature.icon className={`text-${feature.color}-400`} size={24} />
                            </div>
                            <h3 className="text-xl font-bold text-white mb-2">{feature.title}</h3>
                            <p className="text-gray-400">{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* How It Works */}
            <section className="max-w-7xl mx-auto px-4 py-16">
                <h2 className="text-4xl font-black text-white text-center mb-12">
                    City-Scale Workflow
                </h2>

                <div className="grid md:grid-cols-4 gap-6">
                    {[
                        { step: "1", title: "Upload Sites", desc: "CSV with addresses or GIS data" },
                        { step: "2", title: "Batch Assess", desc: "AI processes all sites in minutes" },
                        { step: "3", title: "Deploy", desc: "Connect with certified installers" },
                        { step: "4", title: "Monitor", desc: "Track impact across portfolio" }
                    ].map((item, i) => (
                        <div key={i} className="text-center">
                            <div className="w-16 h-16 mx-auto mb-4 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-2xl font-black text-white">
                                {item.step}
                            </div>
                            <h3 className="text-lg font-bold text-white mb-2">{item.title}</h3>
                            <p className="text-gray-400 text-sm">{item.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="max-w-4xl mx-auto px-4 py-20">
                <div className="glass rounded-3xl p-12 text-center bg-gradient-to-r from-cyan-500/10 to-blue-500/10 border-cyan-500/20">
                    <h2 className="text-3xl font-black text-white mb-4">
                        Ready to transform water management?
                    </h2>
                    <p className="text-gray-300 mb-8">
                        Join 12 states already using RainForge for Jal Shakti mission targets
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link
                            to="/portfolio"
                            className="px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl text-lg"
                        >
                            View Demo Dashboard
                        </Link>
                        <Link
                            to="/bulk"
                            className="px-8 py-4 bg-white/10 text-white font-bold rounded-xl text-lg border border-white/20"
                        >
                            Try Bulk Upload
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="border-t border-white/10 py-8">
                <div className="max-w-7xl mx-auto px-4 flex flex-col md:flex-row justify-between items-center gap-4">
                    <div className="flex items-center gap-2">
                        <Droplets className="h-6 w-6 text-cyan-400" />
                        <span className="text-gray-400 text-sm">
                            © 2024 RainForge • Ministry of Jal Shakti
                        </span>
                    </div>
                    <div className="text-sm text-gray-400">
                        Made by <span className="text-cyan-400 font-medium">Prashant Mishra</span> & <span className="text-purple-400 font-medium">Ishita Parmar</span>
                    </div>
                    <div className="flex gap-6 text-sm text-gray-400">
                        <a href="#" className="hover:text-cyan-400">Documentation</a>
                        <a href="#" className="hover:text-cyan-400">API</a>
                        <a href="#" className="hover:text-cyan-400">Contact</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
