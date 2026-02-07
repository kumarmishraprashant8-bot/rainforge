/**
 * Animated Hero Section
 * Water droplet animations and gradient effects
 */

import { Link } from 'react-router-dom';
import { Droplets, ArrowRight, Sparkles, TrendingUp, Users, Award } from 'lucide-react';

const AnimatedHero = () => {
    return (
        <section className="relative min-h-screen flex items-center justify-center overflow-hidden bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900">

            {/* Animated Background */}
            <div className="absolute inset-0 overflow-hidden">
                {/* Floating water droplets */}
                {[...Array(20)].map((_, i) => (
                    <div
                        key={i}
                        className="absolute animate-float"
                        style={{
                            left: `${Math.random() * 100}%`,
                            top: `${Math.random() * 100}%`,
                            animationDelay: `${Math.random() * 5}s`,
                            animationDuration: `${5 + Math.random() * 5}s`,
                        }}
                    >
                        <div
                            className="w-2 h-3 bg-cyan-400/30 rounded-full blur-sm"
                            style={{ transform: `scale(${0.5 + Math.random() * 1.5})` }}
                        />
                    </div>
                ))}

                {/* Gradient orbs */}
                <div className="absolute top-1/4 -left-32 w-96 h-96 bg-cyan-500/20 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 -right-32 w-96 h-96 bg-purple-500/20 rounded-full blur-3xl animate-pulse" style={{ animationDelay: '1s' }} />
                <div className="absolute top-1/2 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[600px] h-[600px] bg-blue-500/10 rounded-full blur-3xl" />

                {/* Grid pattern */}
                <div className="absolute inset-0 bg-[url('data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNjAiIGhlaWdodD0iNjAiIHZpZXdCb3g9IjAgMCA2MCA2MCIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48ZyBmaWxsPSJub25lIiBmaWxsLXJ1bGU9ImV2ZW5vZGQiPjxwYXRoIGQ9Ik0wIDBoNjB2NjBIMHoiLz48cGF0aCBkPSJNNjAgNjBIMFYwaDYweiIgc3Ryb2tlPSJyZ2JhKDI1NSwyNTUsMjU1LDAuMDUpIiBzdHJva2Utd2lkdGg9IjEiLz48L2c+PC9zdmc+')] opacity-50" />
            </div>

            {/* Content */}
            <div className="relative z-10 max-w-6xl mx-auto px-4 text-center">
                {/* Badge */}
                <div className="inline-flex items-center gap-2 px-4 py-2 bg-white/10 backdrop-blur rounded-full border border-white/20 mb-8 animate-fadeIn">
                    <Sparkles className="text-yellow-400" size={16} />
                    <span className="text-white text-sm">India's #1 Rainwater Harvesting Platform</span>
                </div>

                {/* Main Heading */}
                <h1 className="text-5xl md:text-7xl font-black text-white mb-6 animate-slideUp">
                    Every Drop
                    <span className="block bg-gradient-to-r from-cyan-400 via-blue-400 to-purple-400 bg-clip-text text-transparent">
                        Counts
                    </span>
                </h1>

                {/* Subheading */}
                <p className="text-xl md:text-2xl text-gray-300 max-w-2xl mx-auto mb-10 animate-slideUp" style={{ animationDelay: '0.2s' }}>
                    Calculate your rainwater potential, find installers,
                    and save <span className="text-cyan-400 font-semibold">₹15,000+</span> annually
                </p>

                {/* CTA Buttons */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center mb-16 animate-slideUp" style={{ animationDelay: '0.4s' }}>
                    <Link
                        to="/intake"
                        className="group px-8 py-4 bg-gradient-to-r from-cyan-500 to-blue-500 rounded-2xl text-white font-bold text-lg hover:scale-105 transition-transform shadow-lg shadow-cyan-500/30 flex items-center justify-center gap-2"
                    >
                        Start Free Assessment
                        <ArrowRight className="group-hover:translate-x-1 transition-transform" size={20} />
                    </Link>
                    <Link
                        to="/community"
                        className="px-8 py-4 bg-white/10 backdrop-blur border border-white/20 rounded-2xl text-white font-semibold text-lg hover:bg-white/20 transition-colors flex items-center justify-center gap-2"
                    >
                        <Users size={20} />
                        View Leaderboard
                    </Link>
                </div>

                {/* Stats */}
                <div className="grid grid-cols-3 gap-8 max-w-2xl mx-auto animate-fadeIn" style={{ animationDelay: '0.6s' }}>
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-black text-white mb-1">50K+</div>
                        <div className="text-gray-400 text-sm">Assessments</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-black text-cyan-400 mb-1">2.5B L</div>
                        <div className="text-gray-400 text-sm">Water Saved</div>
                    </div>
                    <div className="text-center">
                        <div className="text-3xl md:text-4xl font-black text-green-400 mb-1">₹35 Cr</div>
                        <div className="text-gray-400 text-sm">Saved by Users</div>
                    </div>
                </div>

                {/* Trust Badges */}
                <div className="mt-16 flex flex-wrap items-center justify-center gap-6 animate-fadeIn" style={{ animationDelay: '0.8s' }}>
                    <div className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl">
                        <Award className="text-yellow-500" size={20} />
                        <span className="text-gray-400 text-sm">Govt. Approved</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl">
                        <TrendingUp className="text-green-500" size={20} />
                        <span className="text-gray-400 text-sm">500+ Verified Installers</span>
                    </div>
                    <div className="flex items-center gap-2 px-4 py-2 bg-white/5 rounded-xl">
                        <Droplets className="text-cyan-500" size={20} />
                        <span className="text-gray-400 text-sm">Made in India 🇮🇳</span>
                    </div>
                </div>
            </div>

            {/* Scroll Indicator */}
            <div className="absolute bottom-8 left-1/2 -translate-x-1/2 animate-bounce">
                <div className="w-6 h-10 rounded-full border-2 border-white/30 flex items-start justify-center p-2">
                    <div className="w-1 h-2 bg-white/50 rounded-full animate-scroll" />
                </div>
            </div>

            {/* CSS Animations */}
            <style>{`
                @keyframes float {
                    0%, 100% { transform: translateY(0) rotate(0deg); opacity: 0.3; }
                    50% { transform: translateY(-20px) rotate(5deg); opacity: 0.8; }
                }
                @keyframes fadeIn {
                    from { opacity: 0; }
                    to { opacity: 1; }
                }
                @keyframes slideUp {
                    from { opacity: 0; transform: translateY(20px); }
                    to { opacity: 1; transform: translateY(0); }
                }
                @keyframes scroll {
                    0%, 100% { transform: translateY(0); opacity: 1; }
                    50% { transform: translateY(4px); opacity: 0.5; }
                }
                .animate-float { animation: float ease-in-out infinite; }
                .animate-fadeIn { animation: fadeIn 0.8s ease-out forwards; }
                .animate-slideUp { animation: slideUp 0.8s ease-out forwards; }
                .animate-scroll { animation: scroll 1.5s ease-in-out infinite; }
            `}</style>
        </section>
    );
};

export default AnimatedHero;
