/**
 * 404 Not Found Page
 * Beautiful water-themed error page with navigation options
 */

import { Link } from 'react-router-dom';
import { Droplets, Home, Search, ArrowLeft, Compass } from 'lucide-react';

const NotFoundPage = () => {
    return (
        <div className="min-h-screen bg-gradient-to-br from-slate-900 via-blue-900 to-slate-900 flex items-center justify-center px-4">
            {/* Background Animation */}
            <div className="absolute inset-0 overflow-hidden pointer-events-none">
                <div className="absolute top-1/4 left-1/4 w-64 h-64 bg-cyan-500/10 rounded-full blur-3xl animate-pulse" />
                <div className="absolute bottom-1/4 right-1/4 w-96 h-96 bg-blue-500/10 rounded-full blur-3xl animate-pulse delay-1000" />
            </div>

            <div className="relative z-10 text-center max-w-lg">
                {/* Animated 404 */}
                <div className="relative mb-8">
                    <div className="text-[180px] font-black text-transparent bg-clip-text bg-gradient-to-r from-cyan-400/20 to-blue-400/20 leading-none select-none">
                        404
                    </div>
                    <div className="absolute inset-0 flex items-center justify-center">
                        <Droplets className="w-24 h-24 text-cyan-400 animate-bounce" />
                    </div>
                </div>

                {/* Message */}
                <h1 className="text-3xl md:text-4xl font-black text-white mb-4">
                    Page Not Found
                </h1>
                <p className="text-gray-400 text-lg mb-8 leading-relaxed">
                    This page seems to have evaporated! Don't worry,
                    let's help you find your way back to collecting rainwater.
                </p>

                {/* Navigation Options */}
                <div className="flex flex-col sm:flex-row gap-4 justify-center mb-8">
                    <Link
                        to="/"
                        className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-bold rounded-xl hover:scale-105 transition-transform shadow-lg hover:shadow-cyan-500/30"
                    >
                        <Home size={20} />
                        Go Home
                    </Link>
                    <Link
                        to="/intake"
                        className="inline-flex items-center justify-center gap-2 px-6 py-3 bg-white/10 hover:bg-white/20 text-white font-bold rounded-xl border border-white/20 transition-colors"
                    >
                        <Compass size={20} />
                        Start Assessment
                    </Link>
                </div>

                {/* Quick Links */}
                <div className="glass rounded-2xl p-6">
                    <h3 className="text-sm font-semibold text-gray-400 uppercase tracking-wider mb-4">
                        Popular Destinations
                    </h3>
                    <div className="flex flex-wrap justify-center gap-3">
                        {[
                            { path: '/portfolio', label: 'Dashboard' },
                            { path: '/marketplace', label: 'Find Pros' },
                            { path: '/bulk', label: 'Bulk Upload' },
                            { path: '/public', label: 'Public Stats' },
                            { path: '/monitoring', label: 'Monitoring' },
                        ].map((link) => (
                            <Link
                                key={link.path}
                                to={link.path}
                                className="px-4 py-2 text-sm text-gray-300 hover:text-cyan-400 hover:bg-white/5 rounded-lg transition-colors"
                            >
                                {link.label}
                            </Link>
                        ))}
                    </div>
                </div>

                {/* Back Button */}
                <button
                    onClick={() => window.history.back()}
                    className="mt-6 inline-flex items-center gap-2 text-gray-400 hover:text-white transition-colors"
                >
                    <ArrowLeft size={16} />
                    Go Back
                </button>
            </div>
        </div>
    );
};

export default NotFoundPage;
