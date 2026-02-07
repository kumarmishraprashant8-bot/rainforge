import { Link } from 'react-router-dom';
import {
    Droplets, ArrowRight, Shield,
    FileSpreadsheet, Activity, Camera, LayoutDashboard,
    Building2, Zap, Sparkles
} from 'lucide-react';

const LandingPage = () => {
    const features = [
        {
            icon: Zap,
            title: "Smart Scenarios",
            desc: "Cost-Optimized, Max Capture, or Dry-Season reliability modes",
            gradient: "from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)]"
        },
        {
            icon: FileSpreadsheet,
            title: "Bulk Upload",
            desc: "CSV upload for 10,000+ sites with automatic batch processing",
            gradient: "from-[var(--color-accent-success)] to-emerald-500"
        },
        {
            icon: LayoutDashboard,
            title: "Portfolio View",
            desc: "District-level dashboard with aggregate KPIs and trends",
            gradient: "from-purple-500 to-pink-500"
        },
        {
            icon: Camera,
            title: "Verification",
            desc: "Photo uploads with geo-tagging for installation proof",
            gradient: "from-rose-500 to-orange-500"
        },
        {
            icon: Activity,
            title: "Live Monitoring",
            desc: "IoT-ready tank levels, predictions, and maintenance alerts",
            gradient: "from-amber-500 to-yellow-500"
        },
        {
            icon: Building2,
            title: "Policy Compliance",
            desc: "State-wise subsidy eligibility and compliance scoring",
            gradient: "from-sky-500 to-blue-500"
        }
    ];

    return (
        <div className="min-h-screen">
            {/* Gradient Background Orbs */}
            <div className="fixed inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-[600px] h-[600px] bg-[var(--color-accent-primary)]/5 rounded-full blur-[150px]" />
                <div className="absolute bottom-1/4 right-1/4 w-[500px] h-[500px] bg-purple-500/5 rounded-full blur-[150px]" />
            </div>

            {/* Nav */}
            <nav className="relative z-10 max-w-7xl mx-auto px-6 py-6 flex justify-between items-center">
                <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-2xl bg-gradient-to-br from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] flex items-center justify-center shadow-lg shadow-[var(--color-accent-primary)]/25">
                        <Droplets className="h-6 w-6 text-white" />
                    </div>
                    <div>
                        <span className="text-2xl font-bold text-[var(--color-text-primary)]">
                            RainForge
                        </span>
                        <span className="ml-2 text-[10px] font-semibold px-2.5 py-1 rounded-lg bg-[var(--color-accent-primary)]/10 text-[var(--color-accent-secondary)] border border-[var(--color-accent-primary)]/20">
                            GOVERNMENT
                        </span>
                    </div>
                </div>
                <div className="hidden md:flex items-center gap-6">
                    <Link to="/dashboard" className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] font-medium transition-colors">Dashboard</Link>
                    <Link to="/portfolio" className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] font-medium transition-colors">Portfolio</Link>
                    <Link to="/bulk" className="text-[var(--color-text-muted)] hover:text-[var(--color-text-primary)] font-medium transition-colors">Bulk Upload</Link>
                    <Link to="/intake" className="btn-primary flex items-center gap-2">
                        Start Assessment
                        <ArrowRight size={16} />
                    </Link>
                </div>
            </nav>

            {/* Hero */}
            <section className="relative z-10 max-w-7xl mx-auto px-6 pt-16 pb-24 text-center">
                {/* Hackathon Badge */}
                <div className="inline-flex items-center gap-3 px-5 py-2.5 rounded-full bg-gradient-to-r from-amber-500/10 to-orange-500/10 border border-amber-500/20 mb-6 animate-fade-in">
                    <span className="text-xl">🏆</span>
                    <span className="text-amber-300/90 text-sm font-semibold">Shortlisted for Jal Shakti Hackathon 2026</span>
                </div>

                {/* Alignment Badge */}
                <div className="inline-flex items-center gap-2 px-4 py-2 rounded-full bg-[var(--color-accent-success)]/10 border border-[var(--color-accent-success)]/20 mb-6 ml-3 animate-fade-in stagger-1">
                    <Shield className="text-[var(--color-accent-success)]" size={14} />
                    <span className="text-[var(--color-accent-success)] text-sm font-medium">Jal Shakti Aligned</span>
                </div>

                {/* Credits */}
                <div className="mb-10 animate-fade-in stagger-2">
                    <span className="text-sm text-[var(--color-text-muted)]">Created by </span>
                    <span className="text-sm font-semibold text-[var(--color-accent-secondary)]">Prashant Mishra</span>
                    <span className="text-sm text-[var(--color-text-muted)]"> & </span>
                    <span className="text-sm font-semibold text-[var(--color-accent-success)]">Ishita Parmar</span>
                </div>

                {/* Main Headline */}
                <h1 className="text-5xl sm:text-6xl lg:text-7xl font-bold text-[var(--color-text-primary)] mb-6 leading-[1.1] animate-fade-in-up">
                    Rainwater Harvesting<br />
                    <span className="text-gradient-primary">
                        at National Scale
                    </span>
                </h1>

                <p className="text-lg sm:text-xl text-[var(--color-text-secondary)] max-w-3xl mx-auto mb-12 leading-relaxed animate-fade-in-up stagger-2">
                    AI-powered platform for government-grade RWH planning, deployment, verification, and impact reporting.
                    From 1 rooftop to 10,000 buildings — RainForge scales with you.
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center animate-fade-in-up stagger-3">
                    <Link
                        to="/intake"
                        className="btn-primary text-lg px-8 py-4 flex items-center justify-center gap-2"
                    >
                        <Sparkles size={18} />
                        Single Site Assessment
                    </Link>
                    <Link
                        to="/bulk"
                        className="btn-secondary text-lg px-8 py-4 flex items-center justify-center gap-2"
                    >
                        <FileSpreadsheet size={18} />
                        Bulk / City Mode
                    </Link>
                </div>
            </section>

            {/* Stats */}
            <section className="relative z-10 max-w-6xl mx-auto px-6 py-12">
                <div className="card-premium rounded-3xl p-8 lg:p-10">
                    <div className="grid grid-cols-2 md:grid-cols-4 gap-8 text-center">
                        <div className="animate-fade-in-up stagger-1">
                            <div className="text-3xl lg:text-4xl font-bold text-[var(--color-accent-secondary)] mb-1">50K+</div>
                            <div className="text-[var(--color-text-muted)] text-sm">Sites Assessed</div>
                        </div>
                        <div className="animate-fade-in-up stagger-2">
                            <div className="text-3xl lg:text-4xl font-bold text-[var(--color-accent-success)] mb-1">2.5B L</div>
                            <div className="text-[var(--color-text-muted)] text-sm">Water Potential</div>
                        </div>
                        <div className="animate-fade-in-up stagger-3">
                            <div className="text-3xl lg:text-4xl font-bold text-purple-400 mb-1">12</div>
                            <div className="text-[var(--color-text-muted)] text-sm">States Onboarded</div>
                        </div>
                        <div className="animate-fade-in-up stagger-4">
                            <div className="text-3xl lg:text-4xl font-bold text-amber-400 mb-1">₹850Cr</div>
                            <div className="text-[var(--color-text-muted)] text-sm">Investment Planned</div>
                        </div>
                    </div>
                </div>
            </section>

            {/* Platform Features */}
            <section className="relative z-10 max-w-7xl mx-auto px-6 py-16">
                <div className="text-center mb-12">
                    <h2 className="text-3xl lg:text-4xl font-bold text-[var(--color-text-primary)] mb-4">
                        Complete Platform
                    </h2>
                    <p className="text-[var(--color-text-muted)] max-w-2xl mx-auto">
                        Everything you need to plan, deploy, verify, and monitor RWH systems at scale
                    </p>
                </div>

                <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-5">
                    {features.map((feature, i) => (
                        <div
                            key={i}
                            className="card-premium p-6 hover-lift animate-fade-in-up"
                            style={{ animationDelay: `${i * 100}ms` }}
                        >
                            <div className={`w-12 h-12 rounded-xl bg-gradient-to-br ${feature.gradient} flex items-center justify-center mb-5 shadow-lg`}>
                                <feature.icon className="text-white" size={22} />
                            </div>
                            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">{feature.title}</h3>
                            <p className="text-[var(--color-text-muted)] text-sm leading-relaxed">{feature.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Workflow */}
            <section className="relative z-10 max-w-7xl mx-auto px-6 py-16">
                <h2 className="text-3xl lg:text-4xl font-bold text-[var(--color-text-primary)] text-center mb-14">
                    City-Scale Workflow
                </h2>

                <div className="grid md:grid-cols-4 gap-8">
                    {[
                        { step: "1", title: "Upload Sites", desc: "CSV with addresses or GIS data" },
                        { step: "2", title: "Batch Assess", desc: "AI processes all sites in minutes" },
                        { step: "3", title: "Deploy", desc: "Connect with certified installers" },
                        { step: "4", title: "Monitor", desc: "Track impact across portfolio" }
                    ].map((item, i) => (
                        <div
                            key={i}
                            className="text-center animate-fade-in-up"
                            style={{ animationDelay: `${i * 150}ms` }}
                        >
                            <div className="w-16 h-16 mx-auto mb-5 rounded-2xl bg-gradient-to-br from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] flex items-center justify-center text-2xl font-bold text-white shadow-lg shadow-[var(--color-accent-primary)]/20">
                                {item.step}
                            </div>
                            <h3 className="text-lg font-semibold text-[var(--color-text-primary)] mb-2">{item.title}</h3>
                            <p className="text-[var(--color-text-muted)] text-sm">{item.desc}</p>
                        </div>
                    ))}
                </div>
            </section>

            {/* CTA */}
            <section className="relative z-10 max-w-4xl mx-auto px-6 py-20">
                <div className="card-premium card-glow rounded-3xl p-10 lg:p-14 text-center">
                    <h2 className="text-2xl lg:text-3xl font-bold text-[var(--color-text-primary)] mb-4">
                        Ready to transform water management?
                    </h2>
                    <p className="text-[var(--color-text-secondary)] mb-10 max-w-lg mx-auto">
                        Join 12 states already using RainForge for Jal Shakti mission targets
                    </p>
                    <div className="flex flex-col sm:flex-row gap-4 justify-center">
                        <Link to="/portfolio" className="btn-primary text-lg px-8 py-4">
                            View Demo Dashboard
                        </Link>
                        <Link to="/bulk" className="btn-secondary text-lg px-8 py-4">
                            Try Bulk Upload
                        </Link>
                    </div>
                </div>
            </section>

            {/* Footer */}
            <footer className="relative z-10 border-t border-[var(--color-border)] py-8">
                <div className="max-w-7xl mx-auto px-6 flex flex-col md:flex-row justify-between items-center gap-6">
                    <div className="flex items-center gap-3">
                        <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-[var(--color-accent-primary)] to-[var(--color-accent-secondary)] flex items-center justify-center">
                            <Droplets className="h-4 w-4 text-white" />
                        </div>
                        <span className="text-[var(--color-text-muted)] text-sm">
                            © 2026 RainForge • Ministry of Jal Shakti
                        </span>
                    </div>
                    <div className="text-sm text-[var(--color-text-muted)]">
                        Built by <span className="text-[var(--color-accent-secondary)] font-medium">Prashant Mishra</span> & <span className="text-[var(--color-accent-success)] font-medium">Ishita Parmar</span>
                    </div>
                    <div className="flex gap-6 text-sm text-[var(--color-text-muted)]">
                        <a href="#" className="hover:text-[var(--color-text-primary)] transition-colors">Docs</a>
                        <a href="#" className="hover:text-[var(--color-text-primary)] transition-colors">API</a>
                        <a href="#" className="hover:text-[var(--color-text-primary)] transition-colors">Contact</a>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default LandingPage;
