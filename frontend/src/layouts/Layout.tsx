import { Outlet, Link, useLocation } from 'react-router-dom';
import {
    Droplets, Home, ShoppingBag, Upload, Activity, Camera,
    LayoutDashboard, Menu, X, User, Trophy, HelpCircle, Waves, TrendingUp, Calendar
} from 'lucide-react';
import { useState } from 'react';
import { ThemeToggleSimple } from '../components/ThemeToggle';
import { KeyboardHint } from '../components/CommandPalette';
import CrisisBanner from '../components/CrisisBanner';
import LanguageSwitcher from '../components/LanguageSwitcher';
import { useAuth } from '../context/AuthContext';
import LoginModal from '../components/LoginModal';
import AICopilot from '../components/copilot/AICopilot';

const Layout = () => {
    const location = useLocation();
    const [mobileMenuOpen, setMobileMenuOpen] = useState(false);
    const [showLoginModal, setShowLoginModal] = useState(false);
    const { user, isAuthenticated } = useAuth();

    const navItems = [
        { path: '/intake', label: 'Assessment', icon: Home },
        { path: '/iot', label: 'IoT Dashboard', icon: Waves },
        { path: '/community', label: 'Community', icon: Trophy },
        { path: '/impact', label: 'Impact', icon: TrendingUp },
        { path: '/book-installer', label: 'Book Installer', icon: Calendar },
        { path: '/marketplace', label: 'Find Pros', icon: ShoppingBag },
        { path: '/help', label: 'Help', icon: HelpCircle },
    ];

    const govItems = [
        { path: '/bulk', label: 'Bulk Upload', icon: Upload },
        { path: '/portfolio', label: 'Portfolio', icon: LayoutDashboard },
        { path: '/monitoring', label: 'Monitoring', icon: Activity },
        { path: '/verification', label: 'Verification', icon: Camera },
    ];

    const isActive = (path: string) => location.pathname === path;

    return (
        <div className="min-h-screen flex flex-col">
            <CrisisBanner />
            {/* Login Modal */}
            <LoginModal isOpen={showLoginModal} onClose={() => setShowLoginModal(false)} />

            {/* Header - Sleek & Modern */}
            <header className="sticky top-0 z-50 glass-dark border-b border-white/5">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 h-16 flex items-center justify-between">
                    <Link to="/" className="flex items-center gap-3 group">
                        {/* Logo with gradient glow */}
                        <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-violet-600 to-fuchsia-500 flex items-center justify-center shadow-lg shadow-violet-500/30 group-hover:shadow-violet-500/50 transition-shadow">
                            <Droplets className="h-5 w-5 text-white" />
                        </div>
                        <div className="flex items-center gap-2">
                            <span className="text-xl font-bold text-white">
                                RainForge
                            </span>
                            <span className="badge-purple text-[10px] py-0.5 px-2">
                                BEAST
                            </span>
                        </div>
                    </Link>

                    {/* Desktop Nav - Pills style */}
                    <nav className="hidden lg:flex items-center gap-1">
                        {navItems.map((item) => (
                            <Link
                                key={item.path}
                                to={item.path}
                                className={`flex items-center gap-2 px-3 py-2 rounded-lg text-sm font-medium transition-all duration-200 ${isActive(item.path)
                                    ? 'bg-violet-500/20 text-violet-300 border border-violet-500/30'
                                    : 'text-zinc-400 hover:text-white hover:bg-white/5'
                                    }`}
                            >
                                <item.icon size={16} />
                                {item.label}
                            </Link>
                        ))}
                    </nav>

                    {/* Header Actions */}
                    <div className="flex items-center gap-2">
                        <LanguageSwitcher compact />
                        <KeyboardHint />
                        <ThemeToggleSimple />

                        {/* User Profile / Login */}
                        {isAuthenticated ? (
                            <Link
                                to="/profile"
                                className="flex items-center gap-2 px-3 py-2 rounded-xl bg-gradient-to-r from-violet-500/20 to-fuchsia-500/20 border border-violet-500/30 hover:border-violet-500/50 transition-all"
                            >
                                <div className="w-6 h-6 rounded-full bg-gradient-to-r from-cyan-500 to-blue-500 flex items-center justify-center text-white text-xs font-bold">
                                    {user?.name?.charAt(0) || 'U'}
                                </div>
                                <span className="text-white text-sm hidden xl:block">{user?.name?.split(' ')[0]}</span>
                            </Link>
                        ) : (
                            <button
                                onClick={() => setShowLoginModal(true)}
                                className="flex items-center gap-2 px-4 py-2 rounded-xl bg-gradient-to-r from-cyan-500 to-blue-500 text-white font-medium text-sm hover:opacity-90 transition-opacity"
                            >
                                <User size={16} />
                                <span className="hidden sm:block">Login</span>
                            </button>
                        )}

                        {/* Mobile menu button */}
                        <button
                            onClick={() => setMobileMenuOpen(!mobileMenuOpen)}
                            className="lg:hidden p-2 rounded-lg text-zinc-400 hover:text-white hover:bg-white/10 transition-colors"
                            aria-label={mobileMenuOpen ? "Close menu" : "Open menu"}
                            aria-expanded={mobileMenuOpen}
                        >
                            {mobileMenuOpen ? <X size={22} /> : <Menu size={22} />}
                        </button>
                    </div>
                </div>

                {/* Mobile Nav */}
                {mobileMenuOpen && (
                    <div className="lg:hidden border-t border-white/5 glass-dark animate-fade-in">
                        <nav className="max-w-7xl mx-auto px-4 py-3 space-y-1">
                            {navItems.map((item) => (
                                <Link
                                    key={item.path}
                                    to={item.path}
                                    onClick={() => setMobileMenuOpen(false)}
                                    className={`flex items-center gap-3 px-4 py-3 rounded-xl font-medium transition-colors ${isActive(item.path)
                                        ? 'bg-violet-500/20 text-violet-300'
                                        : 'text-zinc-400 hover:text-white hover:bg-white/5'
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
            <main className="flex-1 w-full bg-[var(--color-bg-primary)] mt-0">
                <div className="w-full">
                    <Outlet />
                </div>
            </main>

            {/* AI Copilot Widget - Added Here */}
            <AICopilot userId={user?.id || 'guest'} currentPage={location.pathname} />

            {/* Footer */}
            <footer className="border-t border-white/5 py-8 glass-dark">
                <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
                    <div className="flex flex-col md:flex-row justify-between items-center gap-6">
                        <div className="flex items-center gap-3">
                            <div className="w-8 h-8 rounded-lg bg-gradient-to-br from-violet-600 to-fuchsia-500 flex items-center justify-center">
                                <Droplets className="h-4 w-4 text-white" />
                            </div>
                            <span className="text-zinc-500 text-sm">
                                © 2026 RainForge • Government Platform
                            </span>
                        </div>
                        <div className="text-sm text-zinc-500">
                            Built by <span className="text-violet-400 font-medium">Prashant Mishra</span> & <span className="text-emerald-400 font-medium">Ishita Parmar</span>
                        </div>
                        <div className="flex gap-6 text-sm text-zinc-500">
                            <Link to="/help" className="hover:text-white transition-colors">Help</Link>
                            <Link to="/impact" className="hover:text-white transition-colors">Impact</Link>
                            <Link to="/profile" className="hover:text-white transition-colors">Profile</Link>
                        </div>
                    </div>
                </div>
            </footer>
        </div>
    );
};

export default Layout;
