import { Outlet, Link, useLocation } from 'react-router-dom';
import {
    Droplets, Home, ShoppingBag, Upload, Activity, Camera,
    LayoutDashboard, Menu, X
} from 'lucide-react';
import { useState } from 'react';

const Layout = () => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

    const navItems = [
        { path: '/intake', label: 'New Assessment', icon: Home },
        { path: '/bulk', label: 'Bulk Upload', icon: Upload },
        { path: '/portfolio', label: 'Portfolio', icon: LayoutDashboard },
        { path: '/monitoring', label: 'Monitoring', icon: Activity },
        { path: '/verification', label: 'Verification', icon: Camera },
        { path: '/marketplace', label: 'Find Pros', icon: ShoppingBag },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="min-h-screen flex flex-col bg-slate-900">
            {/* Header */}
            <header className="glass-dark border-b border-white/10 sticky top-0 z-50 backdrop-blur-xl">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-3 group">
                        <div className="relative">
                            <Droplets className="h-8 w-8 text-cyan-400 group-hover:scale-110 transition-transform" />
                        </div>
                        <div>
                            <span className="text-xl font-black bg-clip-text text-transparent bg-gradient-to-r from-cyan-400 to-blue-400">
                                RainForge
                            </span>
                            <span className="ml-2 text-xs bg-indigo-500/20 text-indigo-300 px-2 py-0.5 rounded-full">
                                Gov Edition
                            </span>
                        </div>
                    </Link>

                    {/* Desktop Nav */}
                    <nav className="hidden lg:flex items-center gap-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-2 px-4 py-2 rounded-lg text-sm font-medium transition-colors ${isActive(item.path)
                                    ? 'bg-cyan-500/20 text-cyan-400'
                                    : 'text-gray-300 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <item.icon size={16} />
                                {item.label}
                            </Link>
                        ))}
                    </nav>

                    {/* Mobile menu button */}
                    <button
                        onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                        className="lg:hidden p-2 text-gray-300 hover:text-white"
                    >
                        {mobileMenuOpen ? <X size={24} /> : <Menu size={24} />}
                    </button>
                </div>

                {/* Mobile Nav */}
                {mobileMenuOpen && (
                    <div className="lg:hidden border-t border-white/10 bg-slate-900/95 backdrop-blur-xl">
                        <nav className="max-w-7xl mx-auto px-4 py-4 space-y-1">
                            {navItems.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-lg font-medium transition-colors ${isActive(item.path)
                                        ? 'bg-cyan-500/20 text-cyan-400'
                                        : 'text-gray-300 hover:text-white hover:bg-white/5'
                                        }`}
                                >
                                    <item.icon size={18} />
                                    {item.label}
                                </Link>
                            ))}
                        </nav>
                    </div>
                )}
            </header>

            {/* Main Content */}
            <main className="flex-1">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="glass-dark border-t border-white/10 py-6">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-4">
                        <div className="flex items-center gap-2">
                            <Droplets className="h-5 w-5 text-cyan-400" />
                            <span className="text-gray-400 text-sm">
                                © 2024 RainForge • Government Platform • Jal Shakti Aligned
                            </span>
                        </div>
                        <div className="text-sm text-gray-400">
                            Made by <span className="text-cyan-400 font-medium">Prashant Mishra</span> & <span className="text-purple-400 font-medium">Ishita Parmar</span>
                        </div>
                        <div className="flex gap-6 text-sm text-gray-400">
                            <a href="#" className="hover:text-cyan-400 transition-colors">Documentation</a>
                            <a href="#" className="hover:text-cyan-400 transition-colors">API</a>
                            <a href="#" className="hover:text-cyan-400 transition-colors">Support</a>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
